"""
    thriftdomain
    ~~~~~~~~~~~~

    Sphinx domain for documenting Thrift services.

    :copyright: Copyright 2016 by Neumitra, Inc.
    :license: Apache, see LICENSE for details.

"""

import re

from six import iteritems
from docutils import nodes
from docutils.parsers.rst import directives

from pygments.lexer import RegexLexer, bygroups
from pygments.lexers import get_lexer_by_name
from pygments.token import Literal, Text, Operator, Keyword, Name, Number
from pygments.util import ClassNotFound

from sphinx import addnodes
from sphinx.roles import XRefRole
from sphinx.locale import l_, _
from sphinx.domains import Domain, ObjType, Index
from sphinx.directives import ObjectDescription, directives
from sphinx.util.compat import Directive
from sphinx.util.nodes import make_refnode
from sphinx.util.docfields import GroupedField, TypedField, Field

from . import multisource


# REs for Thrift signatures
thrift_sig_re = re.compile(
    r'''^ ([\w.]*\.)?            # namespace name
          (?:<(\w+)>  \s*)?      # type name
          (\w+)  \s*             # thing name
          (?: \((.*)\)           # optional: arguments
           (?:\s* -> \s* (.*))?  #           return annotation
          )? $                   # and nothing more
          ''', re.VERBOSE)


def _pseudo_parse_arglist(signode, arglist):
    """"Parse" a list of arguments separated by commas.

    Arguments can have "optional" annotations given by enclosing them in
    brackets.  Currently, this will split at any comma, even if it's inside a
    string literal (e.g. default argument value).
    """
    paramlist = addnodes.desc_parameterlist()
    stack = [paramlist]
    try:
        for argument in arglist.split(','):
            argument = argument.strip()
            ends_open = ends_close = 0
            while argument.startswith('['):
                stack.append(addnodes.desc_optional())
                stack[-2] += stack[-1]
                argument = argument[1:].strip()
            while argument.startswith(']'):
                stack.pop()
                argument = argument[1:].strip()
            while argument.endswith(']') and not argument.endswith('[]'):
                ends_close += 1
                argument = argument[:-1].strip()
            while argument.endswith('['):
                ends_open += 1
                argument = argument[:-1].strip()
            if argument:
                stack[-1] += addnodes.desc_parameter(argument, argument)
            while ends_open:
                stack.append(addnodes.desc_optional())
                stack[-2] += stack[-1]
                ends_open -= 1
            while ends_close:
                stack.pop()
                ends_close -= 1
        if len(stack) != 1:
            raise IndexError
    except IndexError:
        # if there are too few or too many elements on the stack, just give up
        # and treat the whole argument list as one argument, discarding the
        # already partially populated paramlist node
        signode += addnodes.desc_parameterlist()
        signode[-1] += addnodes.desc_parameter(arglist, arglist)
    else:
        signode += paramlist


# This override allows our inline type specifiers to behave like :class: link
# when it comes to handling "." and "~" prefixes.
class ThriftXrefMixin(object):
    def make_xref(self, rolename, domain, target, innernode=nodes.emphasis,
                  contnode=None):
        result = super(ThriftXrefMixin, self).make_xref(rolename, domain, target,
                                                        innernode, contnode)
        result['refspecific'] = True
        if target.startswith(('.', '~')):
            prefix, result['reftarget'] = target[0], target[1:]
            if prefix == '.':
                text = target[1:]
            elif prefix == '~':
                text = target.split('.')[-1]
            for node in result.traverse(nodes.Text):
                node.parent[node.parent.index(node)] = nodes.Text(text)
                break
        return result


def remove_empty_comment(node):
    name, body = node
    for field in body:
        if type(field) == nodes.paragraph and not field[-1].astext().strip():
            field.pop()
            field.pop()
            break
        elif type(field) == nodes.bullet_list:
            for item in field:
                para = item[0]
                if not para[-1].astext().strip():
                    para.pop()
                    para.pop()

    return node


class ThriftField(ThriftXrefMixin, Field):
    is_typed = True

    def __init__(self, name, names=(), label=None, has_arg=True, rolename=None,
                 bodyrolename=None, typerolename=None):
        self.typenames = (rolename,)
        self.typerolename = bodyrolename
        super(ThriftField, self).__init__(name, names, label, has_arg, rolename, bodyrolename)

    def make_field(self, types, domain, items):
        node = super(ThriftField, self).make_field(types, domain, items)
        return remove_empty_comment(node)


class ThriftGroupedField(ThriftXrefMixin, GroupedField):
    def make_field(self, types, domain, items):
        node = super(ThriftGroupedField, self).make_field(types, domain, items)
        return remove_empty_comment(node)


class ThriftTypedField(ThriftXrefMixin, TypedField):
    def make_field(self, types, domain, items):
        node = super(ThriftTypedField, self).make_field(types, domain, items)
        return remove_empty_comment(node)


class ThriftObject(ObjectDescription):
    required_arguments = 1

    option_spec = {
        'noindex': directives.flag,
        'api': directives.unchanged,
    }

    doc_field_types = [
        ThriftTypedField('constant', label='Constants',
                         names=('const', 'constant'),
                         typerolename='obj', typenames=('consttype', 'type')),
        ThriftGroupedField('values', label='Values',
                           names=('val', 'vals', 'values', 'value'), rolename='enum',
                           can_collapse=True),
        ThriftTypedField('field', label='Fields',
                         names=('field', 'fields'), rolename='struct',
                         typerolename='obj',
                         can_collapse=False),
        ThriftTypedField('parameter', label=l_('Parameters'),
                         names=('param', 'parameter', 'arg', 'argument',
                                'keyword', 'kwarg', 'kwparam'),
                         typerolename='obj', typenames=('paramtype', 'type'),
                         can_collapse=True),
        ThriftTypedField('exceptions', label=l_('Throws'), rolename='svc',
                         can_collapse=True,
                         names=('throws', 'throw', 'exception', 'except')),
        ThriftField('return', label=l_('Returns'), has_arg=False,
                    names=('returns', 'return')),
        ThriftField('returntype', label=l_('Return type'), has_arg=False,
                    rolename='svc', names=('rtype',), bodyrolename='obj'),

    ]

    def get_signature_prefix(self, sig):
        """May return a prefix to put before the object name in the
        signature.
        """
        return ''

    def needs_arglist(self):
        """May return true if an empty argument list is to be generated even if
        the document contains none.
        """
        return False

    def handle_signature(self, sig, signode):
        """Transform a Thrift signature into RST nodes.

        Return (fully qualified name of the thing, svcname if any).

        If inside a service, the current service name is handled intelligently:
        * it is stripped from the displayed name if present
        * it is added to the full name (return value) if not present
        """
        m = thrift_sig_re.match(sig)
        if m is None:
            raise ValueError
        name_prefix, ttype, name, arglist, retann = m.groups()

        # determine module and class name (if applicable), as well as full name
        apiname = self.options.get(
            'api', self.env.ref_context.get('thrift:api'))
        svcname = self.env.ref_context.get('thrift:service')
        if svcname:
            add_module = False
            if name_prefix and name_prefix.startswith(svcname):
                fullname = name_prefix + name
                # service name is given again in the signature
                name_prefix = name_prefix[len(svcname):].lstrip('.')
            else:
                # service name is not given in the signature
                fullname = svcname + '.' + name
        else:
            add_module = True
            if name_prefix:
                svcname = name_prefix.rstrip('.')
                fullname = name_prefix + name
            else:
                svcname = ''
                fullname = name

        signode['api'] = apiname
        signode['svc'] = svcname
        signode['fullname'] = fullname

        sig_prefix = self.get_signature_prefix(sig)
        if sig_prefix:
            signode += addnodes.desc_annotation(sig_prefix, sig_prefix)

        if name_prefix:
            signode += addnodes.desc_addname(name_prefix, name_prefix)

        # exceptions are a special case, since they are documented in the
        # 'exceptions' module.
        elif add_module and self.env.config.add_module_names:
            apiname = self.options.get(
                'api', self.env.ref_context.get('thrift:api'))
            if apiname and apiname != 'exceptions':
                nodetext = apiname + '.'
                signode += addnodes.desc_addname(nodetext, nodetext)

        anno = self.options.get('annotation')

        signode += addnodes.desc_name(name, name)

        if ttype:
            signode += addnodes.desc_annotation(ttype, ' (%s)' % ttype)

        if not arglist:
            if self.needs_arglist():
                # for callables, add an empty parameter list
                signode += addnodes.desc_parameterlist()
            if retann:
                signode += addnodes.desc_returns(retann, retann)
            if anno:
                signode += addnodes.desc_annotation(' ' + anno, ' ' + anno)
            return fullname, name_prefix

        _pseudo_parse_arglist(signode, arglist)
        if retann:
            signode += addnodes.desc_returns(retann, retann)
        if anno:
            signode += addnodes.desc_annotation(' ' + anno, ' ' + anno)
        return fullname, name_prefix

    def add_target_and_index(self, name_cls, sig, signode):
        apiname = self.options.get(
            'api', self.env.ref_context.get('thrift:api'))
        fullname = (apiname and apiname + '.' or '') + name_cls[0]
        # note target
        if fullname not in self.state.document.ids:
            signode['names'].append(fullname)
            signode['ids'].append(fullname)
            signode['first'] = (not self.names)
            self.state.document.note_explicit_target(signode)
            objects = self.env.domaindata['thrift']['objects']
            if fullname in objects:
                self.state_machine.reporter.warning(
                    'duplicate object description of %s, ' % fullname +
                    'other instance in ' +
                    self.env.doc2path(objects[fullname][0]) +
                    ', use :noindex: for one of them',
                    line=self.lineno)
            objects[fullname] = (self.env.docname, self.objtype)

        indextext = self.get_index_text(apiname, name_cls)
        if indextext:
            self.indexnode['entries'].append(('single', indextext,
                                              fullname, ''))

    def before_content(self):
        # needed for automatic qualification of members (reset in subclasses)
        self.svcname_set = False

    def after_content(self):
        if self.svcname_set:
            self.env.ref_context.pop('thrift:service', None)


class ThriftClasslike(ThriftObject):
    """
    Description of a class-like object (services, enums, exceptions).
    """

    def get_signature_prefix(self, sig):
        return self.objtype + ' '

    def get_index_text(self, apiname, name_cls):
        if self.objtype == 'service':
            return _('%s (service in %s API)') % (name_cls[0], apiname)
        elif self.objtype == 'exception':
            return _('%s (exception in %s API)') % (name_cls[0], apiname)
        else:
            return _('%s (struct in %s API)') % (name_cls[0], apiname)

    def before_content(self):
        ThriftObject.before_content(self)
        if self.names:
            self.env.ref_context['thrift:service'] = self.names[0][0]
            self.svcname_set = True


class ThriftClassmember(ThriftObject):
    """
    Description of a type member (methods, fields, enum values).
    """

    def needs_arglist(self):
        return self.objtype.endswith('method')

    def get_signature_prefix(self, sig):
        return ''

    def get_index_text(self, apiname, name_cls):
        name, cls = name_cls
        add_modules = self.env.config.add_module_names
        if self.objtype == 'method':
            try:
                svcname, methname = name.rsplit('.', 1)
            except ValueError:
                if apiname:
                    return _('%s() (in API %s)') % (name, apiname)
                else:
                    return '%s()' % name
            if apiname and add_modules:
                return _('%s() (%s.%s method)') % (methname, apiname, svcname)
            else:
                return _('%s() (%s method)') % (methname, svcname)
        elif self.objtype == 'enumvalue':
            try:
                enum, attrname = name.rsplit('.', 1)
            except ValueError:
                if apiname:
                    return _('%s (in API %s)') % (name, apiname)
                else:
                    return name
            if apiname and add_modules:
                return _('%s (%s.%s value)') % (attrname, apiname, svcname)
            else:
                return _('%s (%s value)') % (attrname, svcname)
        else:
            return ''

    def before_content(self):
        ThriftObject.before_content(self)
        lastname = self.names and self.names[-1][1]
        if lastname and not self.env.ref_context.get('thrift:service'):
            self.env.ref_context['thrift:service'] = lastname.strip('.')
            self.svcname_set = True


class ThriftApiLevel(ThriftObject):
    """
    Description of an object on API level (const, enum, service).
    """

    def needs_arglist(self):
        return False;

    def get_index_text(self, apiname, name_cls):
        if self.objtype == 'const':
            return _('%s (Constant in %s API)') % (name_cls[0], apiname)
        else:
            return ''


class ThriftApi(Directive):
    """
    Directive to mark description of a new API.
    """

    has_content = False
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = False
    option_spec = {
        'synopsis': lambda x: x,
        'noindex': directives.flag,
        'deprecated': directives.flag,
    }

    def run(self):
        env = self.state.document.settings.env
        apiname = self.arguments[0].strip()
        noindex = 'noindex' in self.options
        env.ref_context['thrift:api'] = apiname
        ret = []
        if not noindex:
            env.domaindata['thrift']['api'][apiname] = \
                (env.docname, self.options.get('synopsis', ''),
                 'deprecated' in self.options)
            # make a duplicate entry in 'objects' to facilitate searching for
            # the module in ThriftDomain.find_obj()
            env.domaindata['thrift']['objects'][apiname] = (env.docname, 'api')
            targetnode = nodes.target('', '', ids=['api-' + apiname], ismod=True)
            self.state.document.note_explicit_target(targetnode)
            # the synopsis isn't printed; in fact, they are only
            # used in the modindex currently
            ret.append(targetnode)
            indextext = _('%s (module)') % apiname
            inode = addnodes.index(entries=[('single', indextext,
                                             'api-' + apiname, '')])
            ret.append(inode)
        return ret


class ThriftCurrentApi(Directive):
    """
    This directive is just to tell Sphinx that we're documenting
    stuff in API foo, but links to API foo won't lead here.
    """

    has_content = False
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = False
    option_spec = {}

    def run(self):
        env = self.state.document.settings.env
        apiname = self.arguments[0].strip()
        if apiname == 'None':
            env.ref_context.pop('thrift:api', None)
        else:
            env.ref_context['thrift:api'] = apiname
        return []


class ThriftXRefRole(XRefRole):
    def process_link(self, env, refnode, has_explicit_title, title, target):
        refnode['thrift:api'] = env.ref_context.get('thrift:api')
        refnode['thrift:service'] = env.ref_context.get('thrift:service')
        if not has_explicit_title:
            title = title.lstrip('.')    # only has a meaning for the target
            target = target.lstrip('~')  # only has a meaning for the title
            # if the first character is a tilde, don't display the module/class
            # parts of the contents
            if title[0:1] == '~':
                title = title[1:]
                dot = title.rfind('.')
                if dot != -1:
                    title = title[dot+1:]
        # if the first character is a dot, search more specific namespaces first
        # else search builtins first
        if target[0:1] == '.':
            target = target[1:]
            refnode['refspecific'] = True

        # Remove API name from methods
        parts = title.split('.')
        if len(parts) == 3 and env.config.strip_api_name:
            title = '.'.join(parts[1:])

        return title, target


class ThriftApiIndex(Index):
    """
    Index subclass to provide the Thrift API index.
    """

    name = 'apiindex'
    localname = l_('Thrift API Index')
    shortname = l_('apis')

    def generate(self, docnames=None):
        content = {}
        # list of prefixes to ignore
        ignores = self.domain.env.config['apiindex_common_prefix']
        ignores = sorted(ignores, key=len, reverse=True)
        # list of all modules, sorted by module name
        apis = sorted(iteritems(self.domain.data['api']),
                         key=lambda x: x[0].lower())
        # sort out collapsable modules
        prev_apiname = ''
        num_toplevels = 0
        for apiname, (docname, synopsis, deprecated) in apis:
            if docnames and docname not in docnames:
                continue

            for ignore in ignores:
                if apiname.startswith(ignore):
                    apiname = apiname[len(ignore):]
                    stripped = ignore
                    break
            else:
                stripped = ''

            # we stripped the whole module name?
            if not apiname:
                apiname, stripped = stripped, ''

            entries = content.setdefault(apiname[0].lower(), [])

            num_toplevels += 1
            subtype = 0

            qualifier = deprecated and _('Deprecated') or ''
            entries.append([stripped + apiname, subtype, docname,
                            'api-' + stripped + apiname, [],
                            qualifier, synopsis])
            prev_apiname = apiname

        # apply heuristics when to collapse modindex at page load:
        # only collapse if number of toplevel modules is larger than
        # number of submodules
        collapse = len(apis) - num_toplevels < num_toplevels

        # sort by first letter
        content = sorted(iteritems(content))

        return content, collapse


class ThriftDomain(Domain):
    name = 'thrift'
    label = 'Thrift'
    object_types = {
        'constant':    ObjType(l_('constant'),   'const',   'obj'),
        'enum':        ObjType(l_('enum'),       'enum',    'obj'),
        'struct':      ObjType(l_('struct'),     'struct',  'typedef', 'svc', 'obj'),
        'typedef':     ObjType(l_('typedef'),    'typedef', 'obj'),
        'api':         ObjType(l_('api'),        'api',     'obj'),
        'method':      ObjType(l_('method'),     'meth',    'obj'),
        'service':     ObjType(l_('service'),    'svc',     'exc', 'obj'),
        'exception':   ObjType(l_('exception'),  'exc',     'svc', 'obj'),
    }

    directives = {
        'api':             ThriftApi,
        'currentapi':      ThriftCurrentApi,
        'enum':            ThriftApiLevel,
        'const':           ThriftApiLevel,
        'typedef':         ThriftApiLevel,
        'struct':          ThriftClasslike,
        'service':         ThriftClasslike,
        'exception':       ThriftClasslike,
        'method':          ThriftClassmember,
    }
    roles = {
        'const': ThriftXRefRole(),
        'api': ThriftXRefRole(),
        'enum': ThriftXRefRole(),
        'exc': ThriftXRefRole(),
        'typedef': ThriftXRefRole(),
        'struct': ThriftXRefRole(),
        'meth':  ThriftXRefRole(fix_parens=True),
        'svc': ThriftXRefRole(),
    }
    initial_data = {
        'objects': {},  # fullname -> docname, objtype
        'api': {},  # apiname -> docname, synopsis, deprecated
    }
    indices = [
        ThriftApiIndex,
    ]

    def clear_doc(self, docname):
        for fullname, (fn, _l) in list(self.data['objects'].items()):
            if fn == docname:
                del self.data['objects'][fullname]

        for apiname, (fn, _x, _x) in list(self.data['api'].items()):
            if fn == docname:
                del self.data['api'][apiname]

    def merge_domaindata(self, docnames, otherdata):
        # XXX check duplicates?
        for fullname, (fn, objtype) in otherdata['objects'].items():
            if fn in docnames:
                self.data['objects'][fullname] = (fn, objtype)
        for apiname, data in otherdata['api'].items():
            if data[0] in docnames:
                self.data['api'][apiname] = data

    def find_obj(self, env, apiname, svcname, name, type, searchmode=0):
        """Find a Thrift object for "name", perhaps using the given api
        and/or service name.  Returns a list of (name, object entry) tuples.
        """
        # skip parens
        if name[-2:] == '()':
            name = name[:-2]

        if not name:
            return []

        objects = self.data['objects']
        matches = []

        newname = None
        if searchmode == 1:
            if type is None:
                objtypes = list(self.object_types)
            else:
                objtypes = self.objtypes_for_role(type)
            if objtypes is not None:
                if apiname and svcname:
                    fullname = apiname + '.' + svcname + '.' + name
                    if fullname in objects and objects[fullname][1] in objtypes:
                        newname = fullname
                if not newname:
                    if apiname and apiname + '.' + name in objects and \
                       objects[apiname + '.' + name][1] in objtypes:
                        newname = apiname + '.' + name
                    elif name in objects and objects[name][1] in objtypes:
                        newname = name
                    else:
                        # "fuzzy" searching mode
                        searchname = '.' + name
                        matches = [(oname, objects[oname]) for oname in objects
                                   if oname.endswith(searchname) and
                                   objects[oname][1] in objtypes]
        else:
            # NOTE: searching for exact match, object type is not considered
            if name in objects:
                newname = name
            elif type == 'api':
                # only exact matches allowed for modules
                return []
            elif svcname and svcname + '.' + name in objects:
                newname = svcname + '.' + name
            elif apiname and apiname + '.' + name in objects:
                newname = apiname + '.' + name
            elif apiname and svcname and \
                    apiname + '.' + svcname + '.' + name in objects:
                newname = apiname + '.' + svcname + '.' + name
            # special case: builtin exceptions have module "exceptions" set
            elif type == 'exc' and '.' not in name and \
                    'exceptions.' + name in objects:
                newname = 'exceptions.' + name
            # special case: object methods
            elif type in ('func', 'meth') and '.' not in name and \
                    'object.' + name in objects:
                newname = 'object.' + name
        if newname is not None:
            matches.append((newname, objects[newname]))
        return matches

    def resolve_xref(self, env, fromdocname, builder,
                     type, target, node, contnode):
        apiname = node.get('thrift:api')
        svcname = node.get('thrift:service')
        searchmode = node.hasattr('refspecific') and 1 or 0
        matches = self.find_obj(env, apiname, svcname, target, type, searchmode)
        if not matches:
            return None
        elif len(matches) > 1:
            env.warn_node(
                'more than one target found for cross-reference '
                '%r: %s' % (target, ', '.join(match[0] for match in matches)),
                node)
        name, obj = matches[0]

        if obj[1] == 'api':
            return self._make_api_refnode(builder, fromdocname, name, contnode)
        else:
            return make_refnode(builder, fromdocname, obj[0], name, contnode, name)

    def resolve_any_xref(self, env, fromdocname, builder, target,
                         node, contnode):
        apiname = node.get('thrift:api')
        svcname = node.get('thrift:service')
        results = []

        # always search in "refspecific" mode with the :any: role
        matches = self.find_obj(env, apiname, svcname, target, None, 1)
        for name, obj in matches:
            if obj[1] == 'api':
                results.append(('thrift:api',
                                self._make_api_refnode(builder, fromdocname,
                                                          name, contnode)))
            else:
                results.append(('thrift:' + self.role_for_objtype(obj[1]),
                                make_refnode(builder, fromdocname, obj[0], name,
                                             contnode, name)))
        return results

    def _make_api_refnode(self, builder, fromdocname, name, contnode):
        # get additional info for APIs
        docname, synopsis, deprecated = self.data['api'][name]
        title = name
        if synopsis:
            title += ': ' + synopsis
        if deprecated:
            title += _(' (deprecated)')
        return make_refnode(builder, fromdocname, docname,
                            'api-' + name, contnode, title)

    def get_objects(self):
        for apiname, info in iteritems(self.data['api']):
            yield (apiname, apiname, 'api', info[0], 'api-' + apiname, 0)
        for refname, (docname, type) in iteritems(self.data['objects']):
            if type != 'api':  # apis are already handled
                yield (refname, refname, type, docname, refname, 1)


def setup(app):
    app.add_domain(ThriftDomain)
    app.add_config_value('apiindex_common_prefix', [], 'html')
    app.add_config_value('strip_api_name', True, 'html')
    multisource.setup(app)
