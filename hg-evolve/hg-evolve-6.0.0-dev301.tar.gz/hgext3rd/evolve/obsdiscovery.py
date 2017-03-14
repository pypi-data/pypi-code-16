# Code dedicated to the discovery of obsolescence marker "over the wire"
#
# Copyright 2017 Pierre-Yves David <pierre-yves.david@ens-lyon.org>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.

from __future__ import absolute_import

try:
    import StringIO as io
    StringIO = io.StringIO
except ImportError:
    import io
    StringIO = io.StringIO

import collections
import hashlib
import heapq
import math
import struct

from mercurial import (
    bundle2,
    cmdutil,
    commands,
    dagutil,
    error,
    exchange,
    extensions,
    localrepo,
    node,
    obsolete,
    scmutil,
    setdiscovery,
    util,
    wireproto,
)
from mercurial.hgweb import hgweb_mod
from mercurial.i18n import _

from . import (
    exthelper,
    utility,
)

_pack = struct.pack
_unpack = struct.unpack

eh = exthelper.exthelper()
obsexcmsg = utility.obsexcmsg

##########################################
###  trigger discovery during exchange ###
##########################################

@eh.wrapfunction(exchange, '_pushdiscoveryobsmarkers')
def _pushdiscoveryobsmarkers(orig, pushop):
    if (obsolete.isenabled(pushop.repo, obsolete.exchangeopt)
        and pushop.repo.obsstore
        and 'obsolete' in pushop.remote.listkeys('namespaces')):
        repo = pushop.repo
        obsexcmsg(repo.ui, "computing relevant nodes\n")
        revs = list(repo.revs('::%ln', pushop.futureheads))
        unfi = repo.unfiltered()
        cl = unfi.changelog
        if not pushop.remote.capable('_evoext_obshash_0'):
            # do not trust core yet
            # return orig(pushop)
            nodes = [cl.node(r) for r in revs]
            if nodes:
                obsexcmsg(repo.ui, "computing markers relevant to %i nodes\n"
                                   % len(nodes))
                pushop.outobsmarkers = repo.obsstore.relevantmarkers(nodes)
            else:
                obsexcmsg(repo.ui, "markers already in sync\n")
                pushop.outobsmarkers = []
                pushop.outobsmarkers = repo.obsstore.relevantmarkers(nodes)
            return

        common = []
        missing = None
        obsexcmsg(repo.ui, "looking for common markers in %i nodes\n"
                           % len(revs))
        commonrevs = list(unfi.revs('::%ln', pushop.outgoing.commonheads))
        if _canobshashrange(repo, pushop.remote):
            missing = findmissingrange(pushop.ui, unfi, pushop.remote,
                                       commonrevs)
        else:
            common = findcommonobsmarkers(pushop.ui, unfi, pushop.remote,
                                          commonrevs)
        if missing is None:
            revs = list(unfi.revs('%ld - (::%ln)', revs, common))
            nodes = [cl.node(r) for r in revs]
        else:
            revs = list(repo.revs('only(%ln, %ln)', pushop.futureheads,
                        pushop.outgoing.commonheads))
            nodes = [cl.node(r) for r in revs]
            nodes += missing

        if nodes:
            obsexcmsg(repo.ui, "computing markers relevant to %i nodes\n"
                               % len(nodes))
            pushop.outobsmarkers = repo.obsstore.relevantmarkers(nodes)
        else:
            obsexcmsg(repo.ui, "markers already in sync\n")
            pushop.outobsmarkers = []

@eh.extsetup
def _installobsmarkersdiscovery(ui):
    olddisco = exchange.pushdiscoverymapping['obsmarker']

    def newdisco(pushop):
        _pushdiscoveryobsmarkers(olddisco, pushop)
    exchange.pushdiscoverymapping['obsmarker'] = newdisco

def buildpullobsmarkersboundaries(pullop, bundle2=True):
    """small function returning the argument for pull markers call
    may to contains 'heads' and 'common'. skip the key for None.

    It is a separed function to play around with strategy for that."""
    repo = pullop.repo
    remote = pullop.remote
    unfi = repo.unfiltered()
    revs = unfi.revs('::(%ln - null)', pullop.common)
    boundaries = {'heads': pullop.pulledsubset}
    if not revs: # nothing common
        boundaries['common'] = [node.nullid]
        return boundaries

    if bundle2 and _canobshashrange(repo, remote):
        obsexcmsg(repo.ui, "looking for common markers in %i nodes\n"
                  % len(revs))
        boundaries['missing'] = findmissingrange(repo.ui, repo, pullop.remote,
                                                 revs)
    elif remote.capable('_evoext_obshash_0'):
        obsexcmsg(repo.ui, "looking for common markers in %i nodes\n"
                           % len(revs))
        boundaries['common'] = findcommonobsmarkers(repo.ui, repo, remote, revs)
    else:
        boundaries['common'] = [node.nullid]
    return boundaries

##################################
###  Code performing discovery ###
##################################

def _canobshashrange(local, remote):
    return (local.ui.configbool('experimental', 'obshashrange', False)
            and remote.capable('_donotusemeever_evoext_obshashrange_1'))


def _obshashrange_capabilities(orig, repo, proto):
    """wrapper to advertise new capability"""
    caps = orig(repo, proto)
    enabled = repo.ui.configbool('experimental', 'obshashrange', False)
    if obsolete.isenabled(repo, obsolete.exchangeopt) and enabled:
        caps = caps.split()
        caps.append('_donotusemeever_evoext_obshashrange_1')
        caps.sort()
        caps = ' '.join(caps)
    return caps

@eh.extsetup
def obshashrange_extsetup(ui):
    extensions.wrapfunction(wireproto, 'capabilities', _obshashrange_capabilities)
    # wrap command content
    oldcap, args = wireproto.commands['capabilities']

    def newcap(repo, proto):
        return _obshashrange_capabilities(oldcap, repo, proto)
    wireproto.commands['capabilities'] = (newcap, args)

def findcommonobsmarkers(ui, local, remote, probeset,
                         initialsamplesize=100,
                         fullsamplesize=200):
    # from discovery
    roundtrips = 0
    cl = local.changelog
    dag = dagutil.revlogdag(cl)
    missing = set()
    common = set()
    undecided = set(probeset)
    totalnb = len(undecided)
    ui.progress(_("comparing with other"), 0, total=totalnb)
    _takefullsample = setdiscovery._takefullsample
    if remote.capable('_evoext_obshash_1'):
        getremotehash = remote.evoext_obshash1
        localhash = _obsrelsethashtreefm1(local)
    else:
        getremotehash = remote.evoext_obshash
        localhash = _obsrelsethashtreefm0(local)

    while undecided:

        ui.note(_("sampling from both directions\n"))
        if len(undecided) < fullsamplesize:
            sample = set(undecided)
        else:
            sample = _takefullsample(dag, undecided, size=fullsamplesize)

        roundtrips += 1
        ui.progress(_("comparing with other"), totalnb - len(undecided),
                    total=totalnb)
        ui.debug("query %i; still undecided: %i, sample size is: %i\n"
                 % (roundtrips, len(undecided), len(sample)))
        # indices between sample and externalized version must match
        sample = list(sample)
        remotehash = getremotehash(dag.externalizeall(sample))

        yesno = [localhash[ix][1] == remotehash[si]
                 for si, ix in enumerate(sample)]

        commoninsample = set(n for i, n in enumerate(sample) if yesno[i])
        common.update(dag.ancestorset(commoninsample, common))

        missinginsample = [n for i, n in enumerate(sample) if not yesno[i]]
        missing.update(dag.descendantset(missinginsample, missing))

        undecided.difference_update(missing)
        undecided.difference_update(common)

    ui.progress(_("comparing with other"), None)
    result = dag.headsetofconnecteds(common)
    ui.debug("%d total queries\n" % roundtrips)

    if not result:
        return set([node.nullid])
    return dag.externalizeall(result)

def findmissingrange(ui, local, remote, probeset,
                     initialsamplesize=100,
                     fullsamplesize=200):
    missing = set()

    heads = local.revs('heads(%ld)', probeset)

    # size of slice ?
    heappop = heapq.heappop
    heappush = heapq.heappush
    heapify = heapq.heapify

    tested = set()

    sample = []
    samplesize = initialsamplesize

    def addentry(entry):
        if entry in tested:
            return False
        sample.append(entry)
        tested.add(entry)
        return True

    for h in heads:
        entry = _range(local, h, 0)
        addentry(entry)

    querycount = 0
    ui.progress(_("comparing obsmarker with other"), querycount)
    overflow = []
    while sample or overflow:
        if overflow:
            sample.extend(overflow)
            overflow = []

        if samplesize < len(sample):
            # too much sample already
            overflow = sample[samplesize:]
            sample = sample[:samplesize]
        elif len(sample) < samplesize:
            # we need more sample !
            needed = samplesize - len(sample)
            sliceme = []
            heapify(sliceme)
            for entry in sample:
                if 1 < len(entry):
                    heappush(sliceme, (-len(entry), entry))

            while sliceme and 0 < needed:
                _key, target = heappop(sliceme)
                for new in target.subranges():
                    # XXX we could record hierarchy to optimise drop
                    if addentry(entry):
                        if 1 < len(entry):
                            heappush(sliceme, (-len(entry), entry))
                        needed -= 1
                        if needed <= 0:
                            break

        # no longer the first interation
        samplesize = fullsamplesize

        nbsample = len(sample)
        maxsize = max([len(r) for r in sample])
        ui.debug("query %i; sample size is %i, largest range %i\n"
                 % (querycount, maxsize, nbsample))
        nbreplies = 0
        replies = list(_queryrange(ui, local, remote, sample))
        sample = []
        for entry, remotehash in replies:
            nbreplies += 1
            if remotehash == entry.obshash:
                continue
            elif 1 == len(entry):
                missing.add(entry.node)
            else:
                for new in entry.subranges():
                    addentry(new)
        assert nbsample == nbreplies
        querycount += 1
        ui.progress(_("comparing obsmarker with other"), querycount)
    ui.progress(_("comparing obsmarker with other"), None)
    return sorted(missing)

def _queryrange(ui, repo, remote, allentries):
    mapping = {}

    def gen():
        for entry in allentries:
            key = entry.node + _pack('>I', entry.index)
            mapping[key] = entry
            yield key

    bundler = bundle2.bundle20(ui, bundle2.bundle2caps(remote))
    capsblob = bundle2.encodecaps(bundle2.getrepocaps(repo))
    bundler.newpart('replycaps', data=capsblob)
    bundler.newpart('_donotusemeever_evoext_obshashrange_1', data=gen())

    stream = util.chunkbuffer(bundler.getchunks())
    try:
        reply = remote.unbundle(
            stream, ['force'], remote.url())
    except error.BundleValueError as exc:
        raise error.Abort(_('missing support for %s') % exc)
    try:
        op = bundle2.processbundle(repo, reply)
    except error.BundleValueError as exc:
        raise error.Abort(_('missing support for %s') % exc)
    except bundle2.AbortFromPart as exc:
        ui.status(_('remote: %s\n') % exc)
        if exc.hint is not None:
            ui.status(_('remote: %s\n') % ('(%s)' % exc.hint))
        raise error.Abort(_('push failed on remote'))
    for rep in op.records['_donotusemeever_evoext_obshashrange_1']:
        yield mapping[rep['key']], rep['value']


@bundle2.parthandler('_donotusemeever_evoext_obshashrange_1', ())
def _processqueryrange(op, inpart):
    assert op.reply is not None
    replies = []
    data = inpart.read(24)
    while data:
        n = data[:20]
        index = _unpack('>I', data[20:])[0]
        r = op.repo.changelog.rev(n)
        rhash = _range(op.repo, r, index).obshash
        replies.append(data + rhash)
        data = inpart.read(24)
    op.reply.newpart('reply:_donotusemeever_evoext_obshashrange_1', data=iter(replies))


@bundle2.parthandler('reply:_donotusemeever_evoext_obshashrange_1', ())
def _processqueryrangereply(op, inpart):
    data = inpart.read(44)
    while data:
        key = data[:24]
        rhash = data[24:]
        op.records.add('_donotusemeever_evoext_obshashrange_1', {'key': key, 'value': rhash})
        data = inpart.read(44)

##################################
### Stable topological sorting ###
##################################
@eh.command(
    'debugstablesort',
    [
        ('', 'rev', [], 'heads to start from'),
    ] + commands.formatteropts,
    _(''))
def debugstablesort(ui, repo, **opts):
    """display the ::REVS set topologically sorted in a stable way
    """
    revs = scmutil.revrange(repo, opts['rev'])
    displayer = cmdutil.show_changeset(ui, repo, opts, buffered=True)
    for r in _stablesort(repo, revs):
        ctx = repo[r]
        displayer.show(ctx)
        displayer.flush(ctx)
    displayer.close()

def _stablesort(repo, revs):
    """return '::revs' topologically sorted in "stable" order

    This is a depth first traversal starting from 'nullrev', using node as a
    tie breaker.
    """
    # Various notes:
    #
    # * Bitbucket is used dates as tie breaker, that might be a good idea.
    #
    # * It seemds we can traverse in the same order from (one) head to bottom,
    #   if we the following record data for each merge:
    #
    #  - highest (stablesort-wise) common ancestors,
    #  - order of parents (tablesort-wise)
    cl = repo.changelog
    parents = cl.parentrevs
    nullrev = node.nullrev
    n = cl.node
    # step 1: We need a parents -> children mapping for 2 reasons.
    #
    # * we build the order from nullrev to tip
    #
    # * we need to detect branching
    children = collections.defaultdict(list)
    for r in cl.ancestors(revs, inclusive=True):
        p1, p2 = parents(r)
        children[p1].append(r)
        if p2 != nullrev:
            children[p2].append(r)
    # step two: walk back up
    # * pick lowest node in case of branching
    # * stack disregarded part of the branching
    # * process merge when both parents are yielded

    # track what changeset has been
    seen = [0] * (max(revs) + 2)
    seen[-1] = True # nullrev is known
    # starts from repository roots
    # reuse the list form the mapping as we won't need it again anyway
    stack = children[nullrev]
    if not stack:
        return []
    if 1 < len(stack):
        stack.sort(key=n, reverse=True)

    # list of rev, maybe we should yield, but since we built a children mapping we are 'O(N)' already
    result = []

    current = stack.pop()
    while current is not None or stack:
        if current is None:
            # previous iteration reached a merge or an unready merge,
            current = stack.pop()
            if seen[current]:
                current = None
                continue
        p1, p2 = parents(current)
        if not (seen[p1] and seen[p2]):
            # we can't iterate on this merge yet because other child is not
            # yielded yet (and we are topo sorting) we can discard it for now
            # because it will be reached from the other child.
            current = None
            continue
        assert not seen[current]
        seen[current] = True
        result.append(current) # could be yield, cf earlier comment
        cs = children[current]
        if not cs:
            current = None
        elif 1 == len(cs):
            current = cs[0]
        else:
            cs.sort(key=n, reverse=True)
            current = cs.pop() # proceed on smallest
            stack.extend(cs)   # stack the rest for later
    assert len(result) == len(set(result))
    return result

##############################
### Range Hash computation ###
##############################

@eh.command(
    'debugstablerange',
    [
        ('', 'rev', [], 'heads to start from'),
    ],
    _(''))
def debugstablerange(ui, repo, **opts):
    """display the ::REVS set topologically sorted in a stable way
    """
    s = node.short
    revs = scmutil.revrange(repo, opts['rev'])
    # prewarm depth cache
    for r in repo.revs("::%ld", revs):
        utility.depth(repo, r)
    toproceed = [_range(repo, r, 0, ) for r in revs]
    ranges = set(toproceed)
    while toproceed:
        entry = toproceed.pop()
        for r in entry.subranges():
            if r not in ranges:
                ranges.add(r)
                toproceed.append(r)
    ranges = list(ranges)
    ranges.sort(key=lambda r: (-len(r), r.node))
    ui.status('rev         node index size depth      obshash\n')
    for r in ranges:
        d = (r.head, s(r.node), r.index, len(r), r.depth, node.short(r.obshash))
        ui.status('%3d %s %5d %4d %5d %s\n' % d)

def _hlp2(i):
    """return highest power of two lower than 'i'"""
    return 2 ** int(math.log(i - 1, 2))

class _range(object):

    def __init__(self, repo, head, index, revs=None):
        self._repo = repo.unfiltered()
        self.head = head
        self.index = index
        if revs is not None:
            assert len(revs) == len(self)
            self._revs = revs
        assert index < self.depth, (head, index, self.depth, revs)

    def __repr__(self):
        return '%s %d %d %s' % (node.short(self.node), self.depth, self.index, node.short(self.obshash))

    def __hash__(self):
        return self._id

    def __eq__(self, other):
        if type(self) != type(other):
            raise NotImplementedError()
        return self.stablekey == other.stablekey

    @util.propertycache
    def _id(self):
        return hash(self.stablekey)

    @util.propertycache
    def stablekey(self):
        return (self.node, self.index)

    @util.propertycache
    def node(self):
        return self._repo.changelog.node(self.head)

    def __len__(self):
        return self.depth - self.index

    @util.propertycache
    def depth(self):
        return utility.depth(self._repo, self.head)

    @util.propertycache
    def _revs(self):
        r = _stablesort(self._repo, [self.head])[self.index:]
        assert len(r) == len(self), (self.head, self.index, len(r), len(self))
        return r

    def _slicesat(self, globalindex):
        localindex = globalindex - self.index

        cl = self._repo.changelog

        result = []
        bottom = self._revs[:localindex]
        top = _range(self._repo, self.head, globalindex, self._revs[localindex:])
        #
        toprootdepth = utility.depth(self._repo, top._revs[0])
        if toprootdepth + len(top) == self.depth + 1:
            bheads = [bottom[-1]]
        else:
            bheads = set(bottom)
            parentrevs = cl.parentrevs
            du = bheads.difference_update
            for r in bottom:
                du(parentrevs(r))
            # if len(bheads) == 1:
            #     assert 1 == len(self._repo.revs('roots(%ld)', top._revs))
        if len(bheads) == 1:
            newhead = bottom[-1]
            bottomdepth = utility.depth(self._repo, newhead)
            newstart = bottomdepth - len(bottom)
            result.append(_range(self._repo, newhead, newstart, bottom))
        else:
            # assert 1 < len(bheads), (toprootdepth, len(top), len(self))
            cl = self._repo.changelog
            for h in bheads:
                subset = cl.ancestors([h], inclusive=True)
                hrevs = [r for r in bottom if r in subset]
                start = utility.depth(self._repo, h) - len(hrevs)
                entry = _range(self._repo, h, start, [r for r in bottom if r in subset])
                result.append(entry)
        result.append(top)
        return result

    def subranges(self):
        if not util.safehasattr(self._repo, '_subrangecache'):
            self._repo._subrangecache = {}
        cached = self._repo._subrangecache.get(self)
        if cached is not None:
            return cached
        if len(self) == 1:
            return []
        step = _hlp2(self.depth)
        standard_start = 0
        while standard_start < self.index and 0 < step:
            if standard_start + step < self.depth:
                standard_start += step
            step //= 2
        if self.index == standard_start:
            slicesize = _hlp2(len(self))
            slicepoint = self.index + slicesize
        else:
            assert standard_start < self.depth
            slicepoint = standard_start
        result = self._slicesat(slicepoint)
        self._repo._subrangecache[self] = result
        return result

    @util.propertycache
    def obshash(self):
        cache = self._repo.obsstore.rangeobshashcache
        obshash = cache.get(self)
        if obshash is not None:
            return obshash
        pieces = []
        nullid = node.nullid
        if len(self) == 1:
            tmarkers = self._repo.obsstore.relevantmarkers([self.node])
            pieces = []
            for m in tmarkers:
                mbin = obsolete._fm1encodeonemarker(m)
                pieces.append(mbin)
            pieces.sort()
        else:
            for subrange in self.subranges():
                obshash = subrange.obshash
                if obshash != nullid:
                    pieces.append(obshash)

        sha = hashlib.sha1()
        # note: if there is only one subrange with actual data, we'll just
        # reuse the same hash.
        if not pieces:
            obshash = node.nullid
        elif len(pieces) != 1 or obshash is None:
            sha = hashlib.sha1()
            for p in pieces:
                sha.update(p)
            obshash = cache[self] = sha.digest()
        return obshash

@eh.wrapfunction(obsolete.obsstore, '_addmarkers')
def _addmarkers(orig, obsstore, *args, **kwargs):
    obsstore.rangeobshashcache.clear()
    return orig(obsstore, *args, **kwargs)

@eh.addattr(obsolete.obsstore, 'rangeobshashcache')
@util.propertycache
def rangeobshashcache(obsstore):
    return {}

#############################
### Tree Hash computation ###
#############################

# Dash computed from a given changesets using all markers relevant to it and
# the obshash of its parents.  This is similar to what happend for changeset
# node where the parent is used in the computation

@eh.command(
    'debugobsrelsethashtree',
    [('', 'v0', None, 'hash on marker format "0"'),
     ('', 'v1', None, 'hash on marker format "1" (default)')], _(''))
def debugobsrelsethashtree(ui, repo, v0=False, v1=False):
    """display Obsolete markers, Relevant Set, Hash Tree
    changeset-node obsrelsethashtree-node

    It computed form the "orsht" of its parent and markers
    relevant to the changeset itself."""
    if v0 and v1:
        raise error.Abort('cannot only specify one format')
    elif v0:
        treefunc = _obsrelsethashtreefm0
    else:
        treefunc = _obsrelsethashtreefm1

    for chg, obs in treefunc(repo):
        ui.status('%s %s\n' % (node.hex(chg), node.hex(obs)))

def _obsrelsethashtreefm0(repo):
    return _obsrelsethashtree(repo, obsolete._fm0encodeonemarker)

def _obsrelsethashtreefm1(repo):
    return _obsrelsethashtree(repo, obsolete._fm1encodeonemarker)

def _obsrelsethashtree(repo, encodeonemarker):
    cache = []
    unfi = repo.unfiltered()
    markercache = {}
    repo.ui.progress(_("preparing locally"), 0, total=len(unfi))
    for i in unfi:
        ctx = unfi[i]
        entry = 0
        sha = hashlib.sha1()
        # add data from p1
        for p in ctx.parents():
            p = p.rev()
            if p < 0:
                p = node.nullid
            else:
                p = cache[p][1]
            if p != node.nullid:
                entry += 1
                sha.update(p)
        tmarkers = repo.obsstore.relevantmarkers([ctx.node()])
        if tmarkers:
            bmarkers = []
            for m in tmarkers:
                if m not in markercache:
                    markercache[m] = encodeonemarker(m)
                bmarkers.append(markercache[m])
            bmarkers.sort()
            for m in bmarkers:
                entry += 1
                sha.update(m)
        if entry:
            cache.append((ctx.node(), sha.digest()))
        else:
            cache.append((ctx.node(), node.nullid))
        repo.ui.progress(_("preparing locally"), i, total=len(unfi))
    repo.ui.progress(_("preparing locally"), None)
    return cache

def _obshash(repo, nodes, version=0):
    if version == 0:
        hashs = _obsrelsethashtreefm0(repo)
    elif version == 1:
        hashs = _obsrelsethashtreefm1(repo)
    else:
        assert False
    nm = repo.changelog.nodemap
    revs = [nm.get(n) for n in nodes]
    return [r is None and node.nullid or hashs[r][1] for r in revs]

@eh.addattr(localrepo.localpeer, 'evoext_obshash')
def local_obshash(peer, nodes):
    return _obshash(peer._repo, nodes)

@eh.addattr(localrepo.localpeer, 'evoext_obshash1')
def local_obshash1(peer, nodes):
    return _obshash(peer._repo, nodes, version=1)

@eh.addattr(wireproto.wirepeer, 'evoext_obshash')
def peer_obshash(self, nodes):
    d = self._call("evoext_obshash", nodes=wireproto.encodelist(nodes))
    try:
        return wireproto.decodelist(d)
    except ValueError:
        self._abort(error.ResponseError(_("unexpected response:"), d))

@eh.addattr(wireproto.wirepeer, 'evoext_obshash1')
def peer_obshash1(self, nodes):
    d = self._call("evoext_obshash1", nodes=wireproto.encodelist(nodes))
    try:
        return wireproto.decodelist(d)
    except ValueError:
        self._abort(error.ResponseError(_("unexpected response:"), d))

def srv_obshash(repo, proto, nodes):
    return wireproto.encodelist(_obshash(repo, wireproto.decodelist(nodes)))

def srv_obshash1(repo, proto, nodes):
    return wireproto.encodelist(_obshash(repo, wireproto.decodelist(nodes),
                                version=1))

def _obshash_capabilities(orig, repo, proto):
    """wrapper to advertise new capability"""
    caps = orig(repo, proto)
    if obsolete.isenabled(repo, obsolete.exchangeopt):
        caps = caps.split()
        caps.append('_evoext_obshash_0')
        caps.append('_evoext_obshash_1')
        caps.sort()
        caps = ' '.join(caps)
    return caps

@eh.extsetup
def obshash_extsetup(ui):
    hgweb_mod.perms['evoext_obshash'] = 'pull'
    hgweb_mod.perms['evoext_obshash1'] = 'pull'

    wireproto.commands['evoext_obshash'] = (srv_obshash, 'nodes')
    wireproto.commands['evoext_obshash1'] = (srv_obshash1, 'nodes')
    extensions.wrapfunction(wireproto, 'capabilities', _obshash_capabilities)
    # wrap command content
    oldcap, args = wireproto.commands['capabilities']

    def newcap(repo, proto):
        return _obshash_capabilities(oldcap, repo, proto)
    wireproto.commands['capabilities'] = (newcap, args)
