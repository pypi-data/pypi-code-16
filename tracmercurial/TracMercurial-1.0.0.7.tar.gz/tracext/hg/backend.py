# -*- coding: iso-8859-1 -*-
#
# Copyright (C) 2005-2012 Edgewall Software
# Copyright (C) 2005-2012 Christian Boos <cboos@edgewall.org>
# All rights reserved.
#
# This software may be used and distributed according to the terms
# of the GNU General Public License, incorporated herein by reference.
#
# This software consists of voluntary contributions made by many
# individuals. For the exact contribution history, see the revision
# history and logs, available at http://trac.edgewall.org/log/.
#
# Author: Christian Boos <cboos@edgewall.org>

from bisect import bisect
from datetime import datetime
from heapq import heappop, heappush
import os
import time
import posixpath
import re
import sys
import types

import pkg_resources

from genshi.builder import tag

from trac.core import *
from trac.config import BoolOption, ChoiceOption, ListOption, PathOption
from trac.env import ISystemInfoProvider
from trac.util import arity
from trac.util.datefmt import FixedOffset, utc
from trac.util.text import exception_to_unicode, shorten_line, to_unicode
from trac.util.translation import _, domain_functions
from trac.versioncontrol.api import Changeset, Node, Repository, \
                                    IRepositoryConnector, RepositoryManager, \
                                    NoSuchChangeset, NoSuchNode
from trac.versioncontrol.web_ui import IPropertyRenderer, RenderedProperty
from trac.wiki import IWikiSyntaxProvider
try:
    from trac.versioncontrol.api import InvalidRepository
except ImportError:
    InvalidRepository = TracError

# -- plugin i18n

gettext, _, tag_, N_, add_domain = \
    domain_functions('tracmercurial',
                     ('gettext', '_', 'tag_', 'N_', 'add_domain'))

# -- Using internal Mercurial API, see:
#     * http://mercurial.selenic.com/wiki/MercurialApi
#     * http://mercurial.selenic.com/wiki/ApiChanges

hg_import_error = []
try:
    # The new `demandimport` mechanism doesn't play well with code relying
    # on the `ImportError` exception being caught.
    # OTOH, we can't disable `demandimport` because mercurial relies on it
    # (circular reference issue). So for now, we activate `demandimport`
    # before loading mercurial modules, and desactivate it afterwards.
    #
    # See http://www.selenic.com/mercurial/bts/issue605

    try:
        from mercurial import demandimport
        demandimport.enable();
    except ImportError, hg_import_error:
        demandimport = None

    from mercurial import hg
    from mercurial.context import filectx
    from mercurial.ui import ui
    from mercurial.node import hex, short, nullid, nullrev
    from mercurial.util import pathto, cachefunc
    from mercurial import cmdutil
    from mercurial import encoding
    from mercurial import extensions
    from mercurial.extensions import loadall
    from mercurial.error import RepoLookupError

    # Note: due to the nature of demandimport, there will be no actual
    # import error until those symbols get accessed, so here we go:
    for sym in ("filectx ui hex short nullid pathto "
                "cachefunc loadall".split()):
        if repr(globals()[sym]) == "<unloaded module '%s'>" % sym:
            hg_import_error.append(sym)
    if hg_import_error:
        hg_import_error = "Couldn't import symbols: "+','.join(hg_import_error)

    # Mercurial versions >= 1.2 won't have mercurial.repo.RepoError anymore
    try:
        from mercurial.repo import RepoError
    except ImportError: # Mercurial 2.3.1 doesn't even have mercurial.repo!
        RepoError = None
    from mercurial.revlog import LookupError as HgLookupError
    if RepoError is None or repr(RepoError) == "<unloaded module 'RepoError'>":
        from mercurial.error import RepoError, LookupError as HgLookupError

    # Force local encoding to be non-lossy (#7217)
    os.environ['HGENCODING'] = 'utf-8'
    encoding.tolocal = str

    if demandimport:
        demandimport.disable()

    # API compatibility (watch http://mercurial.selenic.com/wiki/ApiChanges)

    if hasattr(cmdutil, 'match'):
        def match(ctx, *args, **kwargs):
            return cmdutil.match(ctx._repo, *args, **kwargs)
    else:
        from mercurial.scmutil import match

    has_bookmarks = None
    has_phasestr = None

except ImportError, e:
    hg_import_error = e
    ui = object


### Helpers

def checked_encode(u, encodings, check):
    """Convert `unicode` to `str` trying several encodings until a
    condition is met.

    :param u: the `unicode` input
    :param encodings: the list of possible encodings
    :param check: the predicate to satisfy

    :return: the first converted `str` if `check(s)` is `True`,
             otherwise `None`.  Note that if no encoding is able to
             successfully convert the input, the empty string will be
             given to `check`, which can accept it as valid or not.
    """
    s = u
    if isinstance(u, unicode):
        for enc in encodings:
            try:
                s = u.encode(enc)
                if check(s):
                    return s
            except UnicodeEncodeError:
                pass
        else:
            s = ''
    if check(s):
        return s

def get_bookmarks(ctx):
    global has_bookmarks
    if has_bookmarks:
        return ctx.bookmarks()
    if has_bookmarks is None:
        has_bookmarks = hasattr(ctx, 'bookmarks')
        if has_bookmarks:
            return get_bookmarks(ctx)
    return ()

def get_phasestr(ctx):
    global has_phasestr
    if has_phasestr:
        return ctx.phasestr()
    if has_phasestr is None:
        has_phasestr = hasattr(ctx, 'phasestr')
        if has_phasestr:
            return get_phasestr(ctx)
    return None

# Note: localrepository.branchtags was removed in mercurial-2.9
#       see http://selenic.com/hg/rev/4274eda143cb
def get_branchtags(repo):
    """return a dict where branch names map to the tipmost head of
    the branch, open heads come before closed_branches
    """
    def branchtip(heads):
        '''return the tipmost branch head in heads'''
        tip = heads[-1]
        for h in reversed(heads):
            if not repo[h].closesbranch():
              tip = h
              break
        return tip

    bt = {}
    for bn, heads in repo.branchmap().iteritems():
        bt[bn] = branchtip(heads)
    return bt

class trac_ui(ui):
    # Note: will be dropped in 0.13, see MercurialConnector._setup_ui
    def __init__(self, *args, **kwargs):
        ui.__init__(self, *args)
        self.setconfig('ui', 'interactive', 'off')
        self._log = kwargs.get('log', args[0]._log if args and
                               isinstance(args[0], trac_ui) else None)

    def write(self, *args, **opts):
        for a in args:
            self._log.info('(mercurial status) %s', a)

    def write_err(self, *args, **opts):
        for a in args:
            self._log.warn('(mercurial warning) %s', a)

    def plain(self, *args, **kw):
        return False # so that '[hg] hgrc' file can specify [ui] options

    def interactive(self):
        return False

    def readline(self):
        raise TracError('*** Mercurial ui.readline called ***')


### Components

def render_source_prop(repos, context, name, value):
    try:
        ctx = repos.changectx(value)
        chgset = MercurialChangeset(repos, ctx)
        href = context.href.changeset(ctx.hex(), repos.reponame)
        link = tag.a(repos._display(ctx), class_="changeset",
                     title=shorten_line(chgset.message), href=href)
    except NoSuchChangeset:
        link = tag.a(hex(value), class_="missing changeset",
                     title=_("no such changeset"), rel="nofollow")
    return RenderedProperty(name=name, content=link,
                            name_attributes=[("class", "property")])


class CsetPropertyRenderer(Component):

    implements(IPropertyRenderer)

    def match_property(self, name, mode):
        return (name.startswith('hg-') and
                name[3:] in ('Parents', 'Children', 'Tags', 'Branch',
                             'Bookmarks', 'source') and
                mode == 'revprop') and 4 or 0

    def render_property(self, name, mode, context, props):
        if name == 'hg-source':
            repos, value = props[name]
            return render_source_prop(repos, context, _("Graft:"), value)
        return RenderedProperty(name=gettext(name[3:] + ':'),
                name_attributes=[("class", "property")],
                content=self._render_property(name, mode, context, props))

    def _render_property(self, name, mode, context, props):
        repos, revs = props[name]

        if name in ('hg-Parents', 'hg-Children'):
            label = repos.display_rev
        else:
            label = lambda rev: rev

        def link(rev):
            chgset = repos.get_changeset(rev)
            return tag.a(label(rev), class_="changeset",
                         title=shorten_line(chgset.message),
                         href=context.href.changeset(rev, repos.reponame))

        if name == 'hg-Parents' and len(revs) == 2: # merge
            new = context.resource.id
            parent_links = [
                    (link(rev), ' (',
                     tag.a('diff', title=_("Diff against this parent "
                           "(show the changes merged from the other parents)"),
                           href=context.href.changeset(new, repos.reponame,
                                                       old=rev)), ')')
                           for rev in revs]
            return tag([(parent, ', ') for parent in parent_links[:-1]],
                       parent_links[-1], tag.br(),
                       tag.span(tag_("Note: this is a %(merge)s changeset, "
                                     "the changes displayed below correspond "
                                     "to the merge itself.",
                                     merge=tag.strong('merge')),
                                class_='hint'), tag.br(),
                       # TODO: only keep chunks present in both parents
                       #       (conflicts) or in none (extra changes)
                       # tag.span('No changes means the merge was clean.',
                       #         class_='hint'), tag.br(),
                       tag.span(tag_("Use the %(diff)s links above to see all "
                                     "the changes relative to each parent.",
                                     diff=tag.tt('(diff)')),
                                class_='hint'))
        return tag([tag(link(rev), ', ') for rev in revs[:-1]],
                   link(revs[-1]))


class HgExtPropertyRenderer(Component):

    implements(IPropertyRenderer)

    def match_property(self, name, mode):
       return name in ('hg-transplant_source', 'hg-rebase_source',
                       'hg-amend_source', 'hg-convert_revision') and \
           mode == 'revprop' and 4 or 0

    def render_property(self, name, mode, context, props):
        repos, value = props[name]
        if name == 'hg-transplant_source':
            return render_source_prop(repos, context, _("Transplant:"), value)
        elif name == 'hg-rebase_source':
            return render_source_prop(repos, context, _("Rebase:"), value)
        elif name == 'hg-amend_source':
            return render_source_prop(repos, context, _("Amend:"), value)
        elif name == 'hg-convert_revision':
            text = repos.to_u(value)
            if value.startswith('svn:'):
                # e.g. 'svn:af82e41b-90c4-0310-8c96-b1721e28e2e2/trunk@9517'
                uuid = value[:40]
                rev = value.rsplit('@', 1)[-1]
                for r in RepositoryManager(self.env).get_real_repositories():
                    if r.name.startswith(uuid + ':'):
                        path = r.reponame
                        href = context.href.changeset(rev, path or None)
                        text = tag.a('[%s%s]' % (rev, path and '/' + path),
                                     class_='changeset', href=href,
                                     title=_('Changeset in source repository'))
                        break
            return RenderedProperty(name=_('Convert:'), content=text,
                                    name_attributes=[("class", "property")])


class HgDefaultPropertyRenderer(Component):

    implements(IPropertyRenderer)

    def match_property(self, name, mode):
       return name.startswith('hg-') and mode == 'revprop' and 1 or 0

    def render_property(self, name, mode, context, props):
        return RenderedProperty(name=name[3:] + ':',
                                name_attributes=[("class", "property")],
                                content=self._render_property(name, mode,
                                                              context, props))

    def _render_property(self, name, mode, context, props):
        repos, value = props[name]
        try:
            return unicode(value)
        except UnicodeDecodeError:
            if len(value) <= 100:
                return tag.tt(''.join(("%02x" % ord(c)) for c in value))
            else:
                return tag.em(_("(binary, size greater than 100 bytes)"))


class MercurialConnector(Component):

    implements(ISystemInfoProvider, IRepositoryConnector, IWikiSyntaxProvider)

    encoding = ListOption('hg', 'encoding', 'utf-8', doc="""
        Encoding that should be used to decode filenames, file
        content, and changeset metadata.  If multiple encodings are
        used for these different situations (or even multiple
        encodings were used for filenames), simply specify a list of
        encodings which will be tried in turn (''since 0.12.0.24'').
        """)

    show_rev = BoolOption('hg', 'show_rev', True, doc="""
        Show decimal revision in front of the commit SHA1 hash.  While
        this number is specific to the particular clone used to browse
        the repository, this can sometimes give an useful hint about
        the relative "age" of a revision.
        """)

    node_format = ChoiceOption('hg', 'node_format', ['short', 'hex'], doc="""
        Specify how the commit SHA1 hashes should be
        displayed. Possible choices are: 'short', the SHA1 hash is
        abbreviated to its first 12 digits, or 'hex', the hash is
        shown in full.
        """)

    hgrc = PathOption('hg', 'hgrc', '', doc="""
        Optional path to an hgrc file which will be used to specify
        extra Mercurial configuration options (see
        http://www.selenic.com/mercurial/hgrc.5.html).
        """)

    def __init__(self):
        self.ui = None
        locale_dir = pkg_resources.resource_filename(__name__, 'locale')
        add_domain(self.env.path, locale_dir)
        self._version = self._version_info = None
        if not hg_import_error:
            try:
                from mercurial.version import get_version
                self._version = get_version()
            except ImportError: # gone in Mercurial 1.2 (hg:9626819b2e3d)
                from mercurial.util import version
                self._version = version()
            # development version assumed to be always the ''newest'' one,
            # i.e. old development version won't be supported
            self._version_info = (999, 0, 0)
            m = re.match(r'(\d+)\.(\d+)(?:\.(\d+))?', self._version or '')
            if m:
                self._version_info = tuple([int(n or 0) for n in m.groups()])

    def _setup_ui(self, hgrc_path):
        # Starting with Mercurial 1.3 we can probably do simply:
        #
        #   ui = baseui.copy() # there's no longer a parent/child concept
        #   ui.setconfig('ui', 'interactive', 'off')
        #
        self.ui = trac_ui(log=self.log)

        # (code below adapted from mercurial.dispatch._dispatch)

        # read the local repository .hgrc into a local ui object
        if hgrc_path:
            if not os.path.exists(hgrc_path):
                self.log.warn("'[hg] hgrc' file (%s) not found ", hgrc_path)
            try:
                self.ui = trac_ui(self.ui, log=self.log)
                self.ui.check_trusted = False
                self.ui.readconfig(hgrc_path)
            except IOError, e:
                self.log.warn("'[hg] hgrc' file (%s) can't be read: %s",
                              hgrc_path, e)

        extensions.loadall(self.ui)
        if hasattr(extensions, 'extensions'):
            for name, module in extensions.extensions():
                # setup extensions
                extsetup = getattr(module, 'extsetup', None)
                if extsetup:
                    if arity(extsetup) == 1:
                        extsetup(self.ui)
                    else:
                        extsetup()

    # ISystemInfoProvider methods

    def get_system_info(self):
        yield 'Mercurial', self._version

    # IRepositoryConnector methods

    def get_supported_types(self):
        """Support for `repository_type = hg`"""
        if hg_import_error:
            self.error = hg_import_error
            yield ("hg", -1)
        else:
            yield ("hg", 8)

    def get_repository(self, type, dir, params):
        """Return a `MercurialRepository`"""
        if not self.ui:
            self._setup_ui(self.hgrc)
        repos = MercurialRepository(dir, params, self.log, self)
        repos.version_info = self._version_info
        return repos

    # IWikiSyntaxProvider methods

    def get_wiki_syntax(self):
        yield (r'!?(?P<hgrev>[0-9a-f]{12,40})(?P<hgpath>/\S+\b)?',
               lambda formatter, label, match:
                   self._format_link(formatter, 'cset', match.group(0),
                                     match.group(0), match))

    def get_link_resolvers(self):
        yield ('cset', self._format_link)
        yield ('chgset', self._format_link)
        yield ('branch', self._format_link)    # go to the corresponding head
        yield ('tag', self._format_link)

    def _format_link(self, formatter, ns, rev, label, fullmatch=None):
        reponame = path = ''
        repos = None
        rm = RepositoryManager(self.env)
        try:
            if fullmatch:
                rev = fullmatch.group('hgrev')
                path = fullmatch.group('hgpath')
                if path:
                    reponame, repos, path = \
                        rm.get_repository_by_path(path.strip('/'))
            if not repos:
                context = formatter.context
                while context:
                    if context.resource.realm in ('source', 'changeset'):
                        reponame = context.resource.parent.id
                        break
                    context = context.parent
                repos = rm.get_repository(reponame)
            if isinstance(repos, MercurialRepository):
                if ns == 'branch':
                    for b, n in repos.repo.branchtags().items():
                        if repos.to_u(b) == rev:
                            rev = repos.repo.changelog.rev(n)
                            break
                    else:
                        raise NoSuchChangeset(rev)
                chgset = repos.get_changeset(rev)
                return tag.a(label, class_="changeset",
                             title=shorten_line(chgset.message),
                             href=formatter.href.changeset(rev, reponame,
                                                           path))
            raise TracError("Repository not found")
        except NoSuchChangeset, e:
            errmsg = to_unicode(e)
        except TracError:
            errmsg = _("Repository '%(repo)s' not found", repo=reponame)
        return tag.a(label, class_="missing changeset",
                     title=errmsg, rel="nofollow")



### Version Control API

class MercurialRepository(Repository):
    """Repository implementation based on the mercurial API.

    This wraps an hg.repository object.  The revision navigation
    follows the branches, and defaults to the first parent/child in
    case there are many.  The eventual other parents/children are
    listed as additional changeset properties.
    """

    def __init__(self, path, params, log, connector):
        self.ui = connector.ui
        self._show_rev = connector.show_rev
        self._node_fmt = connector.node_format
        # TODO 0.13: per repository ui and options

        # -- encoding
        encoding = connector.encoding
        if not encoding:
            encoding = ['utf-8']
        # verify given encodings
        for enc in encoding:
            try:
                u''.encode(enc)
            except LookupError, e:
                log.warning("'[hg] encoding' (%r) not valid", e)
        if 'latin1' not in encoding:
            encoding.append('latin1')
        self.encoding = encoding

        def to_u(s):
            if isinstance(s, unicode):
                return s
            for enc in encoding:
                try:
                    return unicode(s, enc)
                except UnicodeDecodeError:
                    pass
        def to_s(u):
            if isinstance(u, str):
                return u
            for enc in encoding:
                try:
                    return u.encode(enc)
                except UnicodeEncodeError:
                    pass
        self.to_u = to_u
        self.to_s = to_s

        # -- repository path
        self.path = str_path = path
        # Note: `path` is a filesystem path obtained either from the
        #       trac.ini file or from the `repository` table, so it's
        #       normally an `unicode` instance. '[hg] encoding'
        #       shouldn't play a role here, but we can nevertheless
        #       use that as secondary choices.
        fsencoding = [sys.getfilesystemencoding() or 'utf-8'] + encoding
        str_path = checked_encode(path, fsencoding, os.path.exists)
        if str_path is None:
            raise InvalidRepository(_("Repository path '%(path)s' does not "
                                      "exist.", path=path))
        try:
            self.repo = hg.repository(ui=self.ui, path=str_path)
        except RepoError, e:
            version = connector._version
            error = exception_to_unicode(e)
            log.error("Mercurial %s can't open repository (%s)", version, error)
            raise InvalidRepository(_("'%(path)s' does not appear to contain "
                                      "a repository (Mercurial %(version)s "
                                      "says %(error)s)", path=path,
                                      version=version, error=error))
        # restore branchtags() if needed (see StackOverflow:972)
        if not getattr(self.repo, 'branchtags', None):
            self.repo.branchtags = types.MethodType(get_branchtags, self.repo)
        Repository.__init__(self, 'hg:%s' % path, params, log)

    def from_hg_time(self, timeinfo):
        time, tz = timeinfo
        tzinfo = FixedOffset(tz / 60, 'GMT %d:00' % (tz / 3600))
        return datetime.fromtimestamp(time, tzinfo)

    def changectx(self, rev=None):
        """Produce a Mercurial `context.changectx` from given Trac revision."""
        return self.repo[self.short_rev(rev)]

    def close(self):
        self.repo = None

    def normalize_path(self, path):
        """Remove leading "/", except at root"""
        return path and path.strip('/') or '/'

    def normalize_rev(self, rev):
        """Return the full hash for the specified rev."""
        return self.changectx(rev).hex()

    def short_rev(self, rev):
        """Find Mercurial revision number corresponding to given Trac revision.

        :param rev: any kind of revision specification, either an
                    `unicode` string, or a revision number.  If `None`
                    or '', latest revision will be returned.

        :return: an integer revision
        """
        repo = self.repo
        if rev == 0:
            return rev
        if not rev:
            return len(repo) - 1
        if isinstance(rev, (long, int)):
            return rev
        if rev[0] != "'": # "'11:11'" can be a tag name?
            rev = rev.split(':', 1)[0]
            if rev == '-1':
                return nullrev
            if rev.isdigit():
                r = int(rev)
                if 0 <= r < len(repo):
                    return r
        try:
            return repo[repo.lookup(self.to_s(rev))].rev()
        except (HgLookupError, RepoError):
            raise NoSuchChangeset(rev)

    def display_rev(self, rev):
        return self._display(self.changectx(rev))

    def _display(self, ctx):
        """Return user-readable revision information for node `n`.

        The specific format depends on the `node_format` and
        `show_rev` options.
        """
        nodestr = self._node_fmt == "hex" and ctx.hex() or str(ctx)
        if self._show_rev:
            return '%s:%s' % (ctx.rev(), nodestr)
        else:
            return nodestr

    def get_quickjump_entries(self, rev):
        # map ctx to (unicode) branch
        branches = {}
        closed_branches = {}
        for b, n in self.repo.branchtags().items():
            b = self.to_u(b)
            ctx = self.repo[n]
            if 'close' in ctx.extra():
                closed_branches[ctx] = b
            else:
                branches[ctx] = b
        # map node to tag names
        tags = {}
        tagslist = self.repo.tagslist()
        for tag, n in tagslist:
            tags.setdefault(n, []).append(self.to_u(tag))
        def taginfo(ctx):
            t = tags.get(ctx.node())
            if t:
                return ' (%s)' % ', '.join(t)
            else:
                return ''
        def quickjump_entries(ctx_name_pairs):
            for ctx, name in sorted(ctx_name_pairs, reverse=True,
                                    key=lambda (ctx, name): ctx.rev()):
                nodestr = self._display(ctx)
                yield ((name or nodestr) + taginfo(ctx), '/', nodestr)
        # bookmarks
        bookmarks = [(self.changectx(b), b)
                     for b in get_bookmarks(self.changectx(rev))]
        for e in quickjump_entries(bookmarks):
            yield _("Bookmarks"), e[0], e[1], e[2]
        # branches
        for e in quickjump_entries(branches.items()):
            yield _("Branches"), e[0], e[1], e[2]
        # heads
        heads = [self.repo[n] for n in self.repo.heads()]
        interesting_heads = [(ctx, None) for ctx in heads
                             if (ctx not in branches and
                                 ctx not in closed_branches)]
        for e in quickjump_entries(interesting_heads):
            yield _("Extra heads"), e[0], e[1], e[2]
        # tags
        for t, n in reversed(tagslist):
            try:
                yield (_("Tags"), ', '.join(tags[n]), '/',
                       self._display(self.repo[n]))
            except (KeyError, RepoLookupError):
                pass
        # closed branches
        for e in quickjump_entries(closed_branches.items()):
            yield _("closed branches"), e[0], e[1], e[2]

    def get_path_url(self, path, rev):
        url = self.params.get('url')
        if url and (not path or path == '/'):
            if not rev:
                return url
            branch = self.changectx(rev).branch()
            if branch == 'default':
                return url
            return url + '#' + self.to_u(branch) # URL for cloning that branch

            # Note: link to matching location in Mercurial's file browser
            #rev = rev is not None and short(n) or 'tip'
            #return '/'.join([url, 'file', rev, path])

    def get_changeset(self, rev):
        return MercurialChangeset(self, self.changectx(rev))

    def get_changeset_uid(self, rev):
        return self.changectx(rev).hex()

    def get_changesets(self, start, stop):
        """Follow each head and parents in order to get all changesets

        FIXME: this can only be handled correctly and efficiently by
        using the db repository cache.

        The code below is only an heuristic, and doesn't work in the
        general case. E.g. look at the mercurial repository timeline
        for 2006-10-18, you need to give ''38'' daysback in order to
        see the changesets from 2006-10-17...

        This is because of the following '''linear''' sequence of csets:
          - 3445:233c733e4af5         10/18/2006 9:08:36 AM mpm
          - 3446:0b450267cf47         9/10/2006 3:25:06 AM  hopper
          - 3447:ef1032c223e7         9/10/2006 3:25:06 AM  hopper
          - 3448:6ca49c5fe268         9/10/2006 3:25:07 AM  hopper
          - 3449:c8686e3f0291         10/18/2006 9:14:26 AM hopper

          This is most probably because [3446:3448] correspond to old
          changesets that have been ''hg import''ed, with their
          original dates.
        """
        seen = {nullrev: 1}
        seeds = [self.repo[n] for n in self.repo.heads()]
        while seeds:
            ctx = seeds.pop(0)
            time = self.from_hg_time(ctx.date())
            if time < start:
                continue # assume no ancestor is younger and use next seed
                # (and that assumption is wrong for 3448 in the example above)
            elif time < stop:
                yield MercurialChangeset(self, ctx)
            for p in ctx.parents():
                if p.rev() not in seen:
                    seen[p.rev()] = 1
                    seeds.append(p)

    def get_node(self, path, rev=None):
        return MercurialNode(self, self.normalize_path(path),
                             self.changectx(rev))

    def get_oldest_rev(self):
        return 0

    def get_youngest_rev(self):
        return self.changectx().hex()

    def get_path_history(self, path, rev=None, limit=None):
        raise TracError(_('Unsupported "Show only adds and deletes"'))

    def previous_rev(self, rev, path=''): # FIXME: path ignored for now
        for p in self.changectx(rev).parents():
            if p:
                return p.hex() # always follow first parent

    def next_rev(self, rev, path=''):
        ctx = self.changectx(rev)
        if path: # might be a file
            fc = filectx(self.repo, self.to_s(path), ctx.node())
            # Note: the simpler form below raises an HgLookupError for a dir
            # fc = ctx.filectx(self.to_s(path))
            if fc: # it is a file
                for c in fc.children():
                    return c.hex()
                else:
                    return None
        # it might be a directory (not supported for now) FIXME
        for c in ctx.children():
            return c.hex() # always follow first child

    def parent_revs(self, rev):
        return [p.hex() for p in self.changectx(rev).parents()]

    def rev_older_than(self, rev1, rev2):
        # FIXME use == and ancestors?
        return self.short_rev(rev1) < self.short_rev(rev2)

#    def get_path_history(self, path, rev=None, limit=None):
#      (not really relevant for Mercurial)

    def get_changes(self, old_path, old_rev, new_path, new_rev,
                    ignore_ancestry=1):
        """Generates changes corresponding to generalized diffs.

        Generator that yields change tuples (old_node, new_node, kind,
        change) for each node change between the two arbitrary
        (path,rev) pairs.

        The old_node is assumed to be None when the change is an ADD,
        the new_node is assumed to be None when the change is a
        DELETE.
        """
        old_node = new_node = None
        old_node = self.get_node(old_path, old_rev)
        new_node = self.get_node(new_path, new_rev)
        # check kind, both should be same.
        if new_node.kind != old_node.kind:
            raise TracError(
                _("Diff mismatch: "
                  "Base is a %(okind)s (%(opath)s in revision %(orev)s) "
                  "and Target is a %(nkind)s (%(npath)s in revision %(nrev)s).",
                  okind=old_node.kind, opath=old_path, orev=old_rev,
                  nkind=new_node.kind, npath=new_path, nrev=new_rev))
        # Correct change info from changelog(revlog)
        # Finding changes between two revs requires tracking back
        # several routes.

        if new_node.isdir:
            # TODO: Should we follow rename and copy?
            # As temporary workaround, simply compare entry names.
            changes = []
            str_new_path = new_node.str_path
            str_old_path = old_node.str_path
            # additions and edits
            for str_path in new_node.manifest:
                # changes out of scope
                if str_new_path and not str_path.startswith(str_new_path + '/'):
                    continue
                # 'added' if not present in old manifest
                str_op = str_old_path + str_path[len(str_new_path):]
                if str_op not in old_node.manifest:
                    changes.append((str_path, None, new_node.subnode(str_path),
                                    Node.FILE, Changeset.ADD))
                elif old_node.manifest[str_op] != new_node.manifest[str_path]:
                    changes.append((str_path, old_node.subnode(str_op),
                                    new_node.subnode(str_path),
                                    Node.FILE, Changeset.EDIT))
            # deletions
            for str_path in old_node.manifest:
                # changes out of scope
                if str_old_path and not str_path.startswith(str_old_path + '/'):
                    continue
                # 'deleted' if not present in new manifest
                str_np = str_new_path + str_path[len(str_old_path):]
                if str_np not in new_node.manifest:
                    changes.append((str_path, old_node.subnode(str_np), None,
                                    Node.FILE, Changeset.DELETE))
            # Note: `str_path` only used as a key, no need to convert to_u
            for change in sorted(changes, key=lambda c: c[0]):
                yield(change[1], change[2], change[3], change[4])
        else:
            if old_node.manifest[old_node.str_path] != \
                   new_node.manifest[new_node.str_path]:
                yield(old_node, new_node, Node.FILE, Changeset.EDIT)


class MercurialNode(Node):
    """A path in the repository, at a given revision.

    It encapsulates the repository manifest for the given revision.

    As directories are not first-class citizens in Mercurial,
    retrieving revision information for directory can be much slower
    than for files, except when created as a `subnode()` of an
    existing MercurialNode.
    """

    filectx = dirnode = None

    def __init__(self, repos, path, changectx,
                 manifest=None, dirctx=None, str_entry=None):
        """
        :param repos: the `MercurialRepository`
        :param path: the `unicode` path corresponding to this node
        :param rev: requested revision (i.e. "browsing at")
        :param changectx: the `changectx` for the  "requested" revision

        The following parameters are passed when creating a subnode
        instance:

        :param manifest: `manifest` object from parent `MercurialNode`
        :param dirctx: `changectx` for a directory determined by
                       parent `MercurialNode`
        :param str_entry: entry name if node created from parent node
        """
        repo = repos.repo
        self.repos = repos
        self.changectx = changectx
        self.manifest = manifest or changectx.manifest()
        str_entries = []

        if path == '' or path == '/':
            str_path = ''
        elif dirctx:
            str_path = str_entry
        else:
            # Fast path: check for existing file
            str_path = checked_encode(path, repos.encoding,
                                      lambda s: s in self.manifest)
            if str_path is None:
                # Slow path: this might be a directory node
                str_files = sorted(self.manifest)
                idx = [-1]
                def has_dir_node(str_dir):
                    if not str_dir: # no encoding matched, i.e. not existing
                        return False
                    idx[0] = lo = bisect(str_files, str_dir)
                    return lo < len(str_files) \
                           and str_files[lo].startswith(str_dir)
                str_path = checked_encode(path + '/', repos.encoding,
                                          has_dir_node)
                if str_path is None:
                    raise NoSuchNode(path, changectx.hex())
                lo = idx[0]
                for hi in xrange(lo, len(str_files)):
                    if not str_files[hi].startswith(str_path):
                        break
                str_path = str_path[:-1]
                str_entries = str_files[lo:hi]
        self.str_path = str_path

        # Determine `kind`, `rev` (requested rev) and `created_rev`
        # (last changed revision before requested rev)

        kind = None
        rev = changectx.rev()
        if str_path == '':
            kind = Node.DIRECTORY
            dirctx = changectx
        elif str_path in self.manifest: # then it's a file
            kind = Node.FILE
            self.filectx = changectx.filectx(str_path)
            created_rev = self.filectx.linkrev()
            # FIXME (0.13) this is a hack, we should fix that at the
            #       Trac level, which should really show the
            #       created_rev value for files in the browser.
            rev = created_rev
        else: # we already know it's a dir
            kind = Node.DIRECTORY
            if not dirctx:
                # we need to find the most recent change for a file below dir
                str_dir = str_path + '/'
                dirctxs = self._find_dirctx(changectx.rev(), [str_dir,],
                                            {str_dir: str_entries})
                dirctx = dirctxs.values()[0]

        if not kind:
            if repo.changelog.tip() == nullid or \
                    not (self.manifest or str_path):
                # empty or emptied repository
                kind = Node.DIRECTORY
                dirctx = changectx
            else:
                raise NoSuchNode(path, changectx.hex())

        self.time = self.repos.from_hg_time(changectx.date())
        if dirctx is not None:
            # FIXME (0.13) same remark as above
            rev = created_rev = dirctx.rev()
        Node.__init__(self, self.repos, path, rev or '0', kind)
        self.created_path = path
        self.created_rev = created_rev
        self.data = None

    def _find_dirctx(self, max_rev, str_dirnames, str_entries):
        """Find most recent modification for each given directory path.

        :param max_rev: find no revision more recent than this one
        :param str_dirnames: directory paths to consider
                             (list of `str` ending with '/')
        :param str_entries: maps each directory to the files it contains

        :return: a `dict` with `str_dirnames` as keys, `changectx` as values

        As directories are not first-class citizens in Mercurial, this
        operation is not trivial. There are basically two strategies:

         - for each file below the given directories, retrieve the
           linkrev (most recent modification for this file), and take
           the max; this approach is very inefficient for repositories
           containing many files (#7746)

         - retrieve the files modified when going backward through the
           changelog and detect the first occurrence of a change in
           each directory; this is much faster but can still be slow
           if some folders are only modified in the distant past

        It is possible to combine both approaches, and this can
        produce excellent results in some cases, for example browsing
        the root of the Hg mirror of the Linux repository (at revision
        118733) takes several minutes with the first approach, 11s
        with the second, but only 1.2s with the hybrid approach.

        Note that the specialized scan of the changelog we do below is
        more efficient than the general cmdutil.walkchangerevs.
        """
        str_dirctxs = {}
        repo = self.repos.repo
        max_ctx = repo[max_rev]
        orevs = [-max_rev]
        revs = set(orevs)
        while orevs:
            r = -heappop(orevs)
            ctx = repo[r]
            for p in ctx.parents():
                if p and p.rev() not in revs:
                    revs.add(p.rev())
                    heappush(orevs, -p.rev())
            # lookup changes to str_dirnames in current cset
            for str_file in ctx.files():
                for str_dir in str_dirnames[:]:
                    if str_file.startswith(str_dir):
                        # rev for str_dir was found using first strategy
                        str_dirctxs[str_dir] = ctx
                        str_dirnames.remove(str_dir)
                        if not str_dirnames: # nothing left to find
                            return str_dirctxs

            # In parallel, try the filelog strategy (the 463, 2, 40
            # values below look a bit like magic numbers; actually
            # they were selected by testing the plugin on the Linux
            # and NetBeans repositories)

            # only use the filelog strategy every `n` revs
            n = 463

            # k, the number of files to examine per directory,
            # will be comprised between `min_files` and `max_files`
            min_files = 2
            max_files = 40 # (will be the max if there's only one dir left)

            if r % n == 0:
                k = max(min_files, max_files / len(str_dirnames))
                for str_dir in str_dirnames[:]:
                    str_files = str_entries[str_dir]
                    dr = str_dirctxs.get(str_dir, 0)
                    for f in str_files[:k]:
                        dr = max(dr, max_ctx.filectx(f).linkrev())
                    str_files = str_files[k:]
                    if str_files:
                        # not all files for str_dir seen yet,
                        # store max rev found so far
                        str_entries[str_dir] = str_files
                        str_dirctxs[str_dir] = dr
                    else:
                        # all files for str_dir were examined,
                        # rev found using filelog strategy
                        str_dirctxs[str_dir] = repo[dr]
                        str_dirnames.remove(str_dir)
                        if not str_dirnames:
                            return str_dirctxs


    def subnode(self, str_path, subctx=None):
        """Return a node with the same revision information but for
        another path

        :param str_path: should be the an existing entry in the manifest
        """
        return MercurialNode(self.repos, self.repos.to_u(str_path),
                             self.changectx, self.manifest, subctx, str_path)

    def get_content(self):
        if self.isdir:
            return None
        self.pos = 0 # reset the read()
        return self # something that can be `read()` ...

    def read(self, size=None):
        if self.isdir:
            return TracError(_("Can't read from directory %(path)s",
                               path=self.path))
        if self.data is None:
            self.data = self.filectx.data()
            self.pos = 0
        if size:
            prev_pos = self.pos
            self.pos += size
            return self.data[prev_pos:self.pos]
        return self.data

    def get_entries(self):
        if self.isfile:
            return

        # dirnames are entries which are sub-directories
        str_entries = {}
        str_dirnames = []
        def add_entry(str_file, idx):
            str_entry = str_file
            if idx > -1: # directory
                str_entry = str_file[:idx + 1]
                str_files = str_entries.setdefault(str_entry, [])
                if not str_files:
                    str_dirnames.append(str_entry)
                str_files.append(str_file)
            else:
                str_entries[str_entry] = 1

        if self.str_path:
            str_dir = self.str_path + '/'
            for str_file in self.manifest:
                if str_file.startswith(str_dir):
                    add_entry(str_file, str_file.find('/', len(str_dir)))
        else:
            for str_file in self.manifest:
                add_entry(str_file, str_file.find('/'))

        # pre-computing the changectx for the last change in each sub-directory
        if str_dirnames:
            dirctxs = self._find_dirctx(self.created_rev, str_dirnames,
                                        str_entries)
        else:
            dirctxs = {}

        for str_entry in str_entries:
            yield self.subnode(str_entry.rstrip('/'), dirctxs.get(str_entry))

    def get_history(self, limit=None):
        repo = self.repos.repo
        pats = []
        if self.str_path:
            pats.append('path:' + self.str_path)
        opts = {'rev': ['%s:0' % self.changectx.hex()]}
        if self.isfile and self.repos.version_info < (2, 1, 1):
            opts['follow'] = True
        if arity(cmdutil.walkchangerevs) == 4:
            return self._get_history_1_4(repo, pats, opts, limit)
        else:
            return self._get_history_1_3(repo, pats, opts, limit)

    def _get_history_1_4(self, repo, pats, opts, limit):
        matcher = match(repo[None], pats, opts)
        if self.isfile:
            fncache = {}
            def prep(ctx, fns):
                if self.isfile:
                    fncache[ctx.rev()] = self.repos.to_u(fns[0])
        else:
            def prep(ctx, fns):
                pass

        # keep one lookahead entry so that we can detect renames
        path = self.path
        entry = None
        count = 0
        for ctx in cmdutil.walkchangerevs(repo, matcher, opts, prep):
            if self.isfile and entry:
                path = fncache[ctx.rev()]
                if path != entry[0]:
                    entry = entry[0:2] + (Changeset.COPY,)
            if entry:
                yield entry
                count += 1
                if limit is not None and count >= limit:
                    return
            entry = (path, ctx.hex(), Changeset.EDIT)
        if entry:
            if limit is None or count < limit:
                entry = entry[0:2] + (Changeset.ADD,)
            yield entry

    def _get_history_1_3(self, repo, pats, opts, limit):
        if self.repos.version_info > (1, 3, 999):
            changefn = lambda r: repo[r]
        else:
            changefn = lambda r: repo[r].changeset()
        get = cachefunc(changefn)
        if self.isfile:
            fncache = {}
        chgiter, matchfn = cmdutil.walkchangerevs(self.repos.ui, repo, pats,
                                                  get, opts)
        # keep one lookahead entry so that we can detect renames
        path = self.path
        entry = None
        count = 0
        for st, rev, fns in chgiter:
            if st == 'add' and self.isfile:
                fncache[rev] = self.repos.to_u(fns[0])
            elif st == 'iter':
                if self.isfile and entry:
                    path = fncache[rev]
                    if path != entry[0]:
                        entry = entry[0:2] + (Changeset.COPY,)
                if entry:
                    yield entry
                    count += 1
                    if limit is not None and count >= limit:
                        return
                n = repo.changelog.node(rev)
                entry = (path, hex(n), Changeset.EDIT)
        if entry:
            if limit is None or count < limit:
                entry = entry[0:2] + (Changeset.ADD,)
            yield entry

    def get_annotations(self):
        annotations = []
        if self.filectx:
            for fc, line in self.filectx.annotate(follow=True):
                annotations.append(fc.rev() or '0')
        return annotations

    def get_properties(self):
        if self.isfile and 'x' in self.manifest.flags(self.str_path):
            return {'exe': '*'}
        else:
            return {}

    def get_content_length(self):
        if self.isdir:
            return None
        return self.filectx.size()

    def get_content_type(self):
        if self.isdir:
            return None
        if 'mq' in self.repos.params: # FIXME
            if self.str_path not in ('.hgignore', 'series'):
                return 'text/x-diff'
        return ''

    def get_last_modified(self):
        return self.time


class MercurialChangeset(Changeset):
    """A changeset in the repository.

    This wraps the corresponding information from the changelog.  The
    files changes are obtained by comparing the current manifest to
    the parent manifest(s).
    """

    def __init__(self, repos, ctx):
        self.repos = repos
        self.ctx = ctx
        self.branch = self.repos.to_u(ctx.branch())
        # Note: desc and time are already processed by hg's
        # `encoding.tolocal`; by setting $HGENCODING to latin1, we are
        # however guaranteed to get back the bytes as they were
        # stored.
        desc = repos.to_u(ctx.description())
        user = repos.to_u(ctx.user())
        time = repos.from_hg_time(ctx.date())
        Changeset.__init__(self, repos, ctx.hex(), desc, user, time)

    hg_properties = [
        N_("Parents:"), N_("Children:"), N_("Branch:"), N_("Tags:"),
        N_("Bookmarks:")
    ]

    def get_properties(self):
        properties = {}
        parents = self.ctx.parents()
        if len(parents) > 1:
            properties['hg-Parents'] = (self.repos,
                                        [p.hex() for p in parents if p])
        children = self.ctx.children()
        if len(children) > 1:
            properties['hg-Children'] = (self.repos,
                                         [c.hex() for c in children])
        if self.branch:
            properties['hg-Branch'] = (self.repos, [self.branch])
        tags = self.get_tags()
        if len(tags):
            properties['hg-Tags'] = (self.repos, tags)
        bookmarks = get_bookmarks(self.ctx)
        if len(bookmarks):
            properties['hg-Bookmarks'] = (self.repos, bookmarks)
        phasestr = get_phasestr(self.ctx)
        if phasestr is not None:
            properties['hg-Phase'] = (self.repos, phasestr)
        for k, v in self.ctx.extra().iteritems():
            if k != 'branch':
                properties['hg-' + k] = (self.repos, v)
        return properties

    def get_changes(self):
        u = self.repos.to_u
        repo = self.repos.repo
        manifest = self.ctx.manifest()
        parents = self.ctx.parents()

        renames = []
        str_deletions = {}
        changes = []
        for str_file in self.ctx.files(): # added, edited and deleted files
            f = u(str_file)
            # TODO: find a way to detect conflicts and show how they were
            #       solved (kind of 3-way diff - theirs/mine/merged)
            edits = [p for p in parents if str_file in p.manifest()]

            if str_file not in manifest:
                str_deletions[str_file] = edits[0]
            elif edits:
                for p in edits:
                    changes.append((f, Node.FILE, Changeset.EDIT, f, p.rev()))
            else:
                renamed = repo.file(str_file).renamed(manifest[str_file])
                if renamed:
                    renames.append((f, renamed))
                else:
                    changes.append((f, Node.FILE, Changeset.ADD, '', None))
        # distinguish between move and copy
        for f, (str_base_path, base_filenode) in renames:
            base_ctx = repo.filectx(str_base_path, fileid=base_filenode)
            if str_base_path in str_deletions:
                del str_deletions[str_base_path]
                action = Changeset.MOVE
            else:
                action = Changeset.COPY
            changes.append((f, Node.FILE, action, u(str_base_path),
                            base_ctx.rev()))
        # remaining str_deletions are real deletions
        for str_file, p in str_deletions.items():
            f = u(str_file)
            changes.append((f, Node.FILE, Changeset.DELETE, f, p.rev()))
        changes.sort()
        for change in changes:
            yield change

    def get_branches(self):
        """Yield branch names to which this changeset belong."""
        if self.branch:
            yield (self.branch, len(self.ctx.children()) == 0)

    def get_tags(self):
        """Yield tag names to which this changeset belong."""
        return [self.repos.to_u(t) for t in self.ctx.tags()]

    def get_bookmarks(self):
        """Yield bookmarks associated with this changeset."""
        return [self.repos.to_u(b) for b in get_bookmarks(self.ctx)]
