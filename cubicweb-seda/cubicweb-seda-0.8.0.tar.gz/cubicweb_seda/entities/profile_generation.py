# copyright 2016-2017 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr -- mailto:contact@logilab.fr
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
"""cubicweb-seda adapter classes for profile (schema) generation"""

from functools import partial
from collections import defaultdict, namedtuple

from six import text_type, string_types

from lxml import etree
from pyxst.xml_struct import graph_nodes

from logilab.common import attrdict

from yams import BASE_TYPES

from cubicweb.predicates import is_instance
from cubicweb.view import EntityAdapter

from ..xsd import XSDM_MAPPING, JUMP_ELEMENTS
from ..xsd2yams import SKIP_ATTRS
from . import simplified_profile


JUMPED_OPTIONAL_ELEMENTS = set(('DataObjectPackage', 'FileInfo', 'PhysicalDimensions', 'Coverage'))


def substitute_xml_prefix(prefix_name, namespaces):
    """Given an XML prefixed name in the form `'ns:name'`, return the string `'{<ns_uri>}name'`
    where `<ns_uri>` is the URI for the namespace prefix found in `namespaces`.

    This new string is then suitable to build an LXML etree.Element object.

    Example::

      >>> substitude_xml_prefix('xlink:href', {'xlink': 'http://wwww.w3.org/1999/xlink'})
      '{http://www.w3.org/1999/xlink}href'

    """
    try:
        prefix, name = prefix_name.split(':', 1)
    except ValueError:
        return prefix_name
    assert prefix in namespaces, 'Unknown namespace prefix: {0}'.format(prefix)
    return '{{{0}}}'.format(namespaces[prefix]) + name


def content_types(content_type):
    """Return an ordered tuple of content types from pyxst `textual_content_type` that may be None, a
    set or a string value.
    """
    if content_type:
        if isinstance(content_type, set):
            content_types = sorted(content_type)
        else:
            content_types = (content_type,)
    else:
        content_types = ()
    return content_types


def _internal_reference(value):
    """Return True if the given value is a reference to an entity within the profile."""
    return getattr(value, 'cw_etype', None) in ('SEDAArchiveUnit',
                                                'SEDABinaryDataObject', 'SEDAPhysicalDataObject')


def _concept_value(concept, language):
    """Return string value to be inserted in a SEDA export for the given concept.

    * `concept` may be None, in which case None will be returned

    * `language` is the language matching the exported format (one of 'seda-2', 'seda-1' or
      'seda-02')
    """
    assert language in ('seda-2', 'seda-1', 'seda-02')
    if concept is None:
        return None
    for code in (language, 'seda', 'en'):
        try:
            return concept.labels[code]
        except KeyError:
            continue
    raise RuntimeError('Concept %s has no preferred label in one of "%s", "seda" or "en" language'
                       % (concept.eid, language))


def eid2xmlid(eid):
    """Return a value usable as ID/IDREF for the given eid."""
    return 'id' + text_type(eid)


def serialize(value):
    """Return typed `value` as an XSD string."""
    if value is None:
        return None
    if hasattr(value, 'eid'):
        if value.cw_etype == 'ConceptScheme':
            return value.absolute_url()
        if value.cw_etype == 'Concept':
            return _concept_value(value, 'seda-2')
        if _internal_reference(value):
            return eid2xmlid(value.eid)
        return None  # intermediary entity
    if isinstance(value, bool):
        return 'true' if value else 'false'
    assert isinstance(value, string_types), repr(value)
    return text_type(value)


def minmax_cardinality(string_cardinality, _allowed=('0..1', '0..n', '1', '1..n')):
    """Return (minimum, maximum) cardinality for the cardinality as string (one of '0..1', '0..n',
    '1' or '1..n').
    """
    assert string_cardinality in _allowed, '%s not allowed %s' % (string_cardinality, _allowed)
    if string_cardinality[0] == '0':
        minimum = 0
    else:
        minimum = 1
    if string_cardinality[-1] == 'n':
        maximum = graph_nodes.INFINITY
    else:
        maximum = 1
    return minimum, maximum


def element_minmax_cardinality(occ, card_entity):
    """Return (minimum, maximum) cardinality for the given pyxst Occurence and entity.

    Occurence 's cardinality may be overriden by the entity's user_cardinality value.
    """
    cardinality = getattr(card_entity, 'user_cardinality', None)
    if cardinality is None:
        return occ.minimum, occ.maximum
    else:
        return minmax_cardinality(cardinality)


def attribute_minimum_cardinality(occ, card_entity):
    """Return 0 or 1 for the given pyxst attribute's Occurence. Cardinality may be overriden by
    the data model's user_cardinality value.
    """
    cardinality = getattr(card_entity, 'user_cardinality', None)
    if cardinality is None:
        return occ.minimum
    else:
        return minmax_cardinality(cardinality, ('0..1', '1'))[0]


def iter_path_children(xselement, entity):
    """Return an iterator on `entity` children entities according to `xselement` definition.

    (`path`, `target`) is returned with `path` the path definition leading to the target, and
    `target` either a final value in case of attributes or a list of entities.
    """
    for rtype, role, _path in XSDM_MAPPING.iter_rtype_role(xselement.local_name):
        if _path[0][2] in BASE_TYPES:
            # entity attribute
            if getattr(entity, rtype) is not None:
                yield _path, getattr(entity, rtype)
        else:
            related = entity.related(rtype, role, entities=True)
            if related:
                yield _path, related


class RNGMixin(object):
    """Mixin class providing some Relax NG schema generation helper methods."""

    def rng_element_parent(self, parent, minimum, maximum=1):
        """Given a etree node and minimum/maximum cardinalities of a desired child element,
        return suitable parent node for it.

        This will be one of rng:optional, rng:zeroOrMore or rng:oneOrMore that will be created by
        this method or the given parent itself if minimum == maximum == 1.
        """
        if minimum == 1 and maximum == 1:
            return parent
        elif minimum == 0 and maximum == 1:
            return self.element('rng:optional', parent)
        elif minimum == 0 and maximum == graph_nodes.INFINITY:
            return self.element('rng:zeroOrMore', parent)
        elif minimum == 1 and maximum == graph_nodes.INFINITY:
            return self.element('rng:oneOrMore', parent)
        else:
            assert False, ('unexpected min/max cardinality:', minimum, maximum)

    def rng_attribute_parent(self, parent, minimum):
        """Given a etree node and minimum cardinality of a desired attribute,
        return suitable parent node for it.

        This will be rng:optional that will be created by this method or the given parent itself if
        minimum == 1.
        """
        if minimum == 1:
            return parent
        else:
            return self.element('rng:optional', parent)

    def rng_value(self, element, qualified_datatype, fixed_value=None):
        """Given a (etree) schema element, a data type (e.g. 'xsd:token') and an optional fixed
        value, add RNG declaration to the element to declare the datatype and fix the value if
        necessary.
        """
        prefix, datatype = qualified_datatype.split(':')
        if prefix != 'xsd':
            # XXX RelaxNG compatible version of custom types? this would allow
            # `type_attrs['datatypeLibrary'] = self.namespaces[prefix]`. In the mean time, turn
            # every custom type to string, supposing transfer are also checked against the original
            # schema (as agape v1 was doing).
            datatype = 'string'
        type_attrs = {'type': datatype}
        if fixed_value is not None:
            self.element('rng:value', element, type_attrs, text=fixed_value)
        else:
            self.element('rng:data', element, type_attrs)


class SEDA2ExportAdapter(EntityAdapter):
    """Abstract base class for export of SEDA profile."""
    __abstract__ = True
    __select__ = is_instance('SEDAArchiveTransfer')
    encoding = 'utf-8'
    content_type = 'application/xml'
    # to be defined in concret implementations
    namespaces = {}
    root_attributes = {}

    def dump(self):
        """Return an schema string for the adapted SEDA profile."""
        root = self.dump_etree()
        return etree.tostring(root, encoding=self.encoding, pretty_print=True, standalone=False)

    def dump_etree(self):
        """Return an XSD etree for the adapted SEDA profile."""
        raise NotImplementedError()

    def qname(self, tag):
        return substitute_xml_prefix(tag, self.namespaces)

    def element(self, tag, parent=None, attributes=None, text=None):
        """Generic method to build a XSD element tag.

        Params:

        * `tag`, tag name of the element

        * `parent`, the parent etree node

        * `attributes`, dictionary of attributes - may contain a special 'documentation' attribute
          that will be added in a xsd:annotation node

        * `text`, textual content of the tag if any
        """
        attributes = attributes or {}
        tag = self.qname(tag)
        documentation = attributes.pop('documentation', None)
        for attr, value in attributes.items():
            newattr = substitute_xml_prefix(attr, self.namespaces)
            attributes[newattr] = value
            if newattr != attr:
                attributes.pop(attr)
        if parent is None:
            elt = etree.Element(tag, attributes, nsmap=self.namespaces)
        else:
            elt = etree.SubElement(parent, tag, attributes)
        if text is not None:
            elt.text = text
        if documentation:
            annot = self.element('xsd:annotation', elt)
            self.element('xsd:documentation', annot).text = documentation
        return elt

    def dispatch_occ(self, profile_element, occ, target_value, to_process, card_entity):
        callback = getattr(self, 'element_' + occ.target.__class__.__name__.lower())
        callback(occ, profile_element, target_value, to_process, card_entity)

    def _dump(self, root):
        entity = self.entity
        xselement = XSDM_MAPPING.root_xselement
        transfer_element = self.init_transfer_element(xselement, root, entity)
        to_process = defaultdict(list)
        to_process[xselement].append((entity, transfer_element))
        # first round to ensure we have necessary basic structure
        for xselement, etype, child_defs in XSDM_MAPPING:
            # print 'PROCESS', getattr(xselement, 'local_name', xselement.__class__.__name__), etype
            for entity, profile_element in to_process.pop(xselement, ()):
                assert etype == entity.cw_etype
                self._process(entity, profile_element, child_defs, to_process)
        # then process remaining elements
        # print 'STARTING ROUND 2'
        while to_process:
            xselement = next(iter(to_process))
            entities_profiles = to_process.pop(xselement, ())
            if entities_profiles:
                try:
                    etype, child_defs = XSDM_MAPPING[xselement]
                except KeyError:
                    # element has no children
                    continue
                for entity, profile_element in entities_profiles:
                    assert etype == entity.cw_etype
                    self._process(entity, profile_element, child_defs, to_process)

        assert not to_process, to_process

    def _process(self, entity, profile_element, child_defs, to_process):
        for occ, path in child_defs:
            # print '  child', getattr(occ.target, 'local_name', occ.target.__class__.__name__), \
            #    [x[:-1] for x in path]
            if not path:
                assert not isinstance(occ.target, graph_nodes.XMLAttribute)
                assert occ.target.local_name in JUMP_ELEMENTS, occ.target
                if occ.minimum == 0 and not any(iter_path_children(occ.target, entity)):
                    # element has no children, skip it
                    continue
                if occ.target.local_name in JUMPED_OPTIONAL_ELEMENTS:
                    # elements in JUMPED_OPTIONAL_ELEMENTS are jumped but have optional cardinality,
                    # so search in all it's child element, and mark it as mandatory if one of them
                    # is mandatory, else keep it optional
                    cardinality = '0..1'
                    for _path, target in iter_path_children(occ.target, entity):
                        if _path[0][2] in BASE_TYPES:
                            # special case of a mandatory attribute: parent element will be
                            # mandatory if some value is specified, else that's fine
                            if target is not None:
                                cardinality = '1'
                                break
                        elif any(te.user_cardinality == '1' for te in target):
                            cardinality = '1'
                            break
                else:
                    cardinality = None
                # jumped element: give None as target_value but register the generated element for
                # later processing
                self.dispatch_occ(profile_element, occ, None, to_process,
                                  card_entity=attrdict({'user_cardinality': cardinality}))
                to_process[occ.target].append((entity, self.jumped_element(profile_element)))
            else:
                # print '  values', _path_target_values(entity, path)
                for card_entity, target_value in _path_target_values(entity, path):
                    self.dispatch_occ(profile_element, occ, target_value, to_process,
                                      card_entity=card_entity)

    def init_transfer_element(self, xselement, root, entity):
        """Initialize and return the XML element holding the ArchiveTransfer definition, as well as
        any other necessary global definitions.
        """
        raise NotImplementedError()

    def jumped_element(self, profile_element):
        """Return the last generated element, for insertion of its content."""
        raise NotImplementedError()


class SEDA2XSDExport(SEDA2ExportAdapter):
    """Adapter to build an XSD representation of a SEDA profile, using SEDA 2.0 specification."""
    __regid__ = 'SEDA-2.0.xsd'
    namespaces = {
        None: 'fr:gouv:culture:archivesdefrance:seda:v2.0',
        'seda': 'fr:gouv:culture:archivesdefrance:seda:v2.0',
        'xsd': 'http://www.w3.org/2001/XMLSchema',
        'xlink': 'http://www.w3.org/1999/xlink',
    }
    root_attributes = {
        'attributeFormDefault': 'unqualified',
        'elementFormDefault': 'qualified',
        'targetNamespace': 'fr:gouv:culture:archivesdefrance:seda:v2.0',
        'version': '1.0',
    }

    def dump_etree(self):
        """Return an XSD etree for the adapted SEDA profile."""
        self.defined_content_types = set()
        self.root = root = self.element('xsd:schema', attributes=self.root_attributes)
        self.element('xsd:import', parent=root,
                     attributes={'namespace': 'http://www.w3.org/XML/1998/namespace',
                                 'schemaLocation': 'http://www.w3.org/2001/xml.xsd'})
        self.element('xsd:import', parent=root,
                     attributes={'namespace': 'http://www.w3.org/1999/xlink',
                                 'schemaLocation': 'http://www.w3.org/1999/xlink.xsd'})
        self._dump(root)
        xsd_cleanup_etree(root)
        return root

    def init_transfer_element(self, xselement, root, entity):
        profile_element = self.element('xsd:element', root,
                                       {'name': xselement.local_name,
                                        'documentation': entity.user_annotation})
        self.element('xsd:sequence', self.element('xsd:complexType', profile_element))
        open_type = self.element('xsd:complexType', root, {'name': 'OpenType', 'abstract': 'true'})
        open_type_seq = self.element('xsd:sequence', open_type)
        self.element('xsd:attribute', open_type, {'ref': 'xml:id', 'use': 'optional'})
        self.element('xsd:attribute', open_type, {'ref': 'xlink:href', 'use': 'optional'})
        self.element('xsd:any', open_type_seq, {'namespace': '##other', 'processContents': 'lax',
                                                'minOccurs': '0'})
        return profile_element

    def jumped_element(self, profile_element):
        return self._parent_element(profile_element)[-1]

    def element_alternative(self, occ, profile_element, target_value, to_process, card_entity):
        attrs = xsd_element_cardinality(occ, card_entity)
        parent_element = self._parent_element(profile_element)
        target_element = self.element('xsd:choice', parent_element, attrs)
        to_process[occ.target].append((target_value, target_element))

    def element_sequence(self, occ, profile_element, target_value, to_process, card_entity):
        attrs = xsd_element_cardinality(occ, card_entity)
        parent_element = self._parent_element(profile_element)
        target_element = self.element('xsd:sequence', parent_element, attrs)
        to_process[occ.target].append((target_value, target_element))

    def element_xmlattribute(self, occ, profile_element, target_value, to_process, card_entity):
        attrs = xsd_attribute_cardinality(occ, card_entity)
        q = self.qname
        xpath = q('xsd:complexType') + '/' + q('xsd:simpleContent') + '/' + q('xsd:extension')
        parent = profile_element.find(xpath)
        if parent is None:
            parent = profile_element.find(self.qname('xsd:complexType'))
            assert parent is not None
        xselement = occ.target
        attrs['name'] = xselement.local_name
        content_type = self.xsd_content_type(xselement.textual_content_type)
        attrs['type'] = content_type
        target_element = self.element('xsd:attribute', parent, attrs)
        value = serialize(target_value)
        if value is not None:
            attr = self.qname('seda:profid') if xselement.local_name == 'id' else 'fixed'
            target_element.attrib[attr] = value

    def element_xmlelement(self, occ, profile_element, target_value, to_process, card_entity):  # noqa
        attrs = xsd_element_cardinality(occ, card_entity)
        attrs['documentation'] = getattr(card_entity, 'user_annotation', None)
        xselement = occ.target
        if xselement.local_name == 'Signature':
            attrs['type'] = 'OpenType'
            self._target_element(xselement, profile_element, attrs)
        elif isinstance(occ, dict):  # fake occurence introduced for some elements'content
            # target element has already been introduced: it is now given as profile_element
            target_element = profile_element
            try:
                extension_element = target_element[0][0][0]
            except IndexError:
                # XXX debugging information for traceback which occured on our demo
                # should disappear at some point
                descendants = []
                while len(target_element) and len(descendants) < 3:
                    descendants.append(target_element[0])
                    target_element = target_element[0]
                self.error('Unexpected target_element: %s', descendants)
                raise
            self.fill_element(xselement, target_element, extension_element,
                              target_value, card_entity)
        else:
            target_element = self._target_element(xselement, profile_element, attrs)
            content_type = self.xsd_content_type(xselement.textual_content_type)
            if content_type:
                type_element = self.element('xsd:complexType', target_element)
                content_element = self.element('xsd:simpleContent', parent=type_element)
                extension_element = self.element('xsd:extension', parent=content_element,
                                                 attributes={'base': content_type})
                self.fill_element(xselement, target_element, extension_element,
                                  target_value, card_entity, copy_attributes=True)
            else:
                type_element = self.element('xsd:complexType', target_element)
                seq_element = self.element('xsd:sequence', type_element)
                # target is a complex element
                if getattr(target_value, 'eid', None):  # value is an entity
                    if target_value.cw_etype == 'AuthorityRecord':
                        self.fill_organization_element(seq_element, target_value)
                elif xselement.local_name in ('ArchivalAgency', 'TransferringAgency'):
                    self.fill_organization_element(seq_element, None)
                elif target_value is not None:
                    assert False, (xselement, target_value)
            if getattr(target_value, 'eid', None):  # value is an entity
                to_process[xselement].append((target_value, target_element))

    def fill_element(self, xselement, target_element, extension_element, value, card_entity,
                     copy_attributes=False):
        if xselement.local_name == 'KeywordType':
            if value:
                attrs = {'fixed': value.scheme.description or value.scheme.dc_title()}
            else:
                attrs = {'default': 'edition 2009'}
            attrs['name'] = 'listVersionID'
            self.element('xsd:attribute', attributes=attrs, parent=extension_element)
        elif (xselement.local_name == 'KeywordReference' and card_entity.scheme):
            self.concept_scheme_attribute(xselement, extension_element, card_entity.scheme)
        elif getattr(value, 'cw_etype', None) == 'Concept':
            self.concept_scheme_attribute(xselement, extension_element, value.scheme)
        elif copy_attributes:
            for attrname, occ in xselement.attributes.items():
                if attrname in ('id', 'href') or attrname.startswith(('list', 'scheme')):
                    attrs = xsd_attribute_cardinality(occ, None)
                    attrs['name'] = attrname
                    attrs['type'] = self.xsd_content_type(occ.target.textual_content_type)
                    self.element('xsd:attribute', attributes=attrs, parent=extension_element)
        fixed_value = serialize(value)
        if fixed_value is not None:
            attr = 'default' if _internal_reference(value) else 'fixed'
            target_element.attrib[attr] = fixed_value

    def concept_scheme_attribute(self, xselement, type_element, scheme):
        try:
            scheme_attr = xselement_scheme_attribute(xselement)
        except KeyError:
            return
        self.element('xsd:attribute', type_element,
                     attributes={'name': scheme_attr,
                                 'fixed': scheme.absolute_url()})

    def fill_organization_element(self, parent_element, value):
        target_element = self.element('xsd:element', parent_element, {'name': 'Identifier'})
        type_element = self.element('xsd:simpleType', target_element)
        restriction_element = self.element('xsd:restriction', type_element,
                                           {'base': 'xsd:string'})
        if value:
            self.element('xsd:enumeration', restriction_element,
                         {'value': value.absolute_url()})

    def _parent_element(self, profile_element):
        q = self.qname
        if profile_element.tag in (q('xsd:choice'), q('xsd:sequence')):
            parent = profile_element
        else:
            xpath = q('xsd:complexType') + '/' + q('xsd:sequence')
            parent = profile_element.find(xpath)
            assert parent is not None
        return parent

    def _target_element(self, xselement, profile_element, attrs):
        parent_element = self._parent_element(profile_element)
        attrs['name'] = xselement.local_name
        return self.element('xsd:element', parent_element, attrs)

    def xsd_content_type(self, content_type):
        """Return XSD content type from pyxst `textual_content_type` that may be None, a set or a string
        value.
        """
        if content_type:
            if isinstance(content_type, set):
                # to satisfy XSD schema, we've to create an intermediary type holding the union of
                # types
                type_name = ''.join(sorted(content_type))
                if type_name not in self.defined_content_types:
                    type_element = self.element('xsd:simpleType', self.root, {'name': type_name})
                    union_element = self.element('xsd:union', parent=type_element)
                    content_type = ' '.join(sorted('xsd:' + ct for ct in content_type))
                    union_element.attrib['memberTypes'] = content_type
                    self.defined_content_types.add(type_name)
                return type_name
            content_type = 'xsd:' + content_type
        return content_type


class SEDA2RelaxNGExport(RNGMixin, SEDA2ExportAdapter):
    """Adapter to build a Relax NG representation of a SEDA profile, using SEDA 2.0 specification.
    """
    __regid__ = 'SEDA-2.0.rng'

    namespaces = SEDA2XSDExport.namespaces.copy()
    namespaces['rng'] = 'http://relaxng.org/ns/structure/1.0'
    namespaces['a'] = 'http://relaxng.org/ns/compatibility/annotations/1.0'

    root_attributes = {
        'ns': 'fr:gouv:culture:archivesdefrance:seda:v2.0',
        'datatypeLibrary': 'http://www.w3.org/2001/XMLSchema-datatypes',
    }

    def dump_etree(self):
        """Return an XSD etree for the adapted SEDA profile."""
        root = self.element('rng:grammar', attributes=self.root_attributes)
        start = self.element('rng:start', root)
        # XXX http://lists.xml.org/archives/xml-dev/200206/msg01074.html ?
        # self.element('xsd:import', parent=root,
        #              attributes={'namespace': 'http://www.w3.org/1999/xlink',
        #                          'schemaLocation': 'http://www.w3.org/1999/xlink.xsd'})
        self._dump(start)

        open_type = self.element('rng:define', root, {'name': 'OpenType'})
        open_elt = self._create_hierarchy(open_type, ['rng:zeroOrMore', 'rng:element'])
        self.element('rng:anyName', open_elt)
        self._create_hierarchy(open_elt, ['rng:zeroOrMore', 'rng:attribute', 'rng:anyName'])

        # add a 'text' node to empty rng:element to satisfy the RNG grammar
        namespaces = self.namespaces.copy()
        del namespaces[None]  # xpath engine don't want None prefix
        for element in root.xpath('//rng:element[not(*)]', namespaces=namespaces):
            self.element('rng:text', element)
        return root

    def init_transfer_element(self, xselement, root, entity):
        transfer_element = self.element('rng:element', root,
                                        {'name': xselement.local_name,
                                         'documentation': entity.user_annotation})
        exc = self._create_hierarchy(
            transfer_element, ['rng:zeroOrMore', 'rng:attribute', 'rng:anyName', 'rng:except'])
        self.element('rng:nsName', exc)
        self.element('rng:nsName', exc, {'ns': ''})
        return transfer_element

    def jumped_element(self, profile_element):
        element = profile_element[-1]
        if element.tag != '{http://relaxng.org/ns/structure/1.0}element':
            # optional, zeroOrMore, etc.: should pick their child element
            element = element[-1]
            assert element.tag == '{http://relaxng.org/ns/structure/1.0}element', element
        return element

    def element_alternative(self, occ, profile_element, target_value, to_process, card_entity):
        parent_element = self._rng_element_parent(occ, card_entity, profile_element)
        target_element = self.element('rng:choice', parent_element)
        to_process[occ.target].append((target_value, target_element))

    def element_sequence(self, occ, profile_element, target_value, to_process, card_entity):
        parent_element = self._rng_element_parent(occ, card_entity, profile_element)
        target_element = self.element('rng:group', parent_element)  # XXX sequence
        to_process[occ.target].append((target_value, target_element))

    def element_xmlattribute(self, occ, profile_element, target_value, to_process, card_entity):
        parent_element = self._rng_attribute_parent(occ, card_entity, profile_element)
        self._rng_attribute(occ.target, parent_element, serialize(target_value))

    def element_xmlelement(self, occ, profile_element, target_value, to_process, card_entity):  # noqa
        parent_element = self._rng_element_parent(occ, card_entity, profile_element)
        xselement = occ.target
        attrs = {'documentation': getattr(card_entity, 'user_annotation', None),
                 'name': xselement.local_name}
        if xselement.local_name == 'Signature':
            element = self.element('rng:element', parent_element, attrs)
            self.element('rng:ref', element, {'name': 'OpenType'})
        elif isinstance(occ, dict):  # fake occurence introduced for some elements'content
            # target element has already been introduced: it is now given as profile_element
            self.fill_element(xselement, profile_element, target_value, card_entity)
        else:
            target_element = self.element('rng:element', parent_element, attrs)
            xstypes = content_types(xselement.textual_content_type)
            if xstypes:
                if len(xstypes) == 1:
                    parent_element = target_element
                else:
                    parent_element = self.element('rng:choice', target_element)
                for xstype in xstypes:
                    self.fill_element(xselement, parent_element, target_value, card_entity,
                                      xstype=xstype, copy_attributes=True)
            else:
                # target is a complex element
                if getattr(target_value, 'eid', None):  # value is an entity
                    if target_value.cw_etype == 'AuthorityRecord':
                        self.fill_organization_element(target_element, target_value)
                elif xselement.local_name in ('ArchivalAgency', 'TransferringAgency'):
                    self.fill_organization_element(target_element, None)
                elif target_value is not None:
                    assert False, (xselement, target_value)
            if getattr(target_value, 'eid', None):  # value is an entity
                to_process[xselement].append((target_value, target_element))

    def fill_element(self, xselement, profile_element, value, card_entity,  # noqa
                     copy_attributes=False, xstype=None):
        if xselement.local_name == 'KeywordType':
            attr = self.element('rng:attribute', attributes={'name': 'listVersionID'},
                                parent=self.element('rng:optional', profile_element))
            if value:
                list_value = value.scheme.description or value.scheme.dc_title()
                attrs = {'type': xstype} if xstype else {}
                self.element('rng:value', attr, attrs, text=list_value)
            else:
                attr.attrib[self.qname('a:defaultValue')] = 'edition 2009'

        elif (xselement.local_name == 'KeywordReference' and card_entity.scheme):
            self.concept_scheme_attribute(xselement, profile_element, card_entity.scheme)

        elif getattr(value, 'cw_etype', None) == 'Concept':
            self.concept_scheme_attribute(xselement, profile_element, value.scheme)

        elif copy_attributes:
            for attrname, occ in xselement.attributes.items():
                if attrname in ('id', 'href') or attrname.startswith(('list', 'scheme')):
                    parent_element = self._rng_attribute_parent(occ, None, profile_element)
                    self._rng_attribute(occ.target, parent_element)
        fixed_value = serialize(value)
        if fixed_value is not None:
            if _internal_reference(value):
                profile_element.attrib[self.qname('a:defaultValue')] = fixed_value
                self.element('rng:data', profile_element, {'type': 'NCName'})
            else:
                if (len(profile_element)
                        and profile_element[-1].tag == '{http://relaxng.org/ns/structure/1.0}data'):
                    xstype = profile_element[-1].attrib.get('type')
                    profile_element.remove(profile_element[-1])
                attrs = {'type': xstype} if xstype else {}
                self.element('rng:value', profile_element, attrs, text=fixed_value)
        elif xstype is not None:
            self.element('rng:data', profile_element, {'type': xstype})

    def concept_scheme_attribute(self, xselement, type_element, scheme):
        try:
            scheme_attr = xselement_scheme_attribute(xselement)
        except KeyError:
            return
        scheme_attr = self.element('rng:attribute', type_element,
                                   attributes={'name': scheme_attr})
        self.element('rng:value', scheme_attr, text=scheme.absolute_url())

    def fill_organization_element(self, parent_element, value):
        target_element = self.element('rng:element', parent_element, {'name': 'Identifier'})
        if value:
            self.element('rng:value', target_element, text=value.absolute_url())

    def _rng_element_parent(self, occ, card_entity, profile_element):
        minimum, maximum = element_minmax_cardinality(occ, card_entity)
        return self.rng_element_parent(profile_element, minimum, maximum)

    def _rng_attribute_parent(self, occ, card_entity, profile_element):
        minimum = attribute_minimum_cardinality(occ, card_entity)
        return self.rng_element_parent(profile_element, minimum)

    def _rng_attribute(self, xselement, parent_element, value=None):
        xstypes = content_types(xselement.textual_content_type)
        if len(xstypes) > 1:
            parent_element = self.element('rng:choice', parent_element)
        for xstype in xstypes:
            attr_element = self.element('rng:attribute', parent_element,
                                        {'name': xselement.local_name})
            if value is not None:
                if xselement.local_name == 'id':
                    attr_element.attrib[self.qname('seda:profid')] = value
                    self.element('rng:data', attr_element, {'type': 'ID'})
                else:
                    self.element('rng:value', attr_element, {'type': xstype}, text=value)
            else:
                self.element('rng:data', attr_element, {'type': xstype})

    def _create_hierarchy(self, parent, tags):
        for tag in tags:
            parent = self.element(tag, parent)
        return parent


def climb_rule_holders(transfer_or_archive_unit):
    """Starting from a transfer or archive unit entity, yield entity that may be linked to management
    rule until the root (transfer) is reached.
    """
    while transfer_or_archive_unit is not None:
        if transfer_or_archive_unit.cw_etype == 'SEDAArchiveTransfer':
            yield transfer_or_archive_unit
        else:
            yield transfer_or_archive_unit.first_level_choice.content_sequence
        transfer_or_archive_unit = transfer_or_archive_unit.cw_adapt_to('ITreeBase').parent()


def _safe_cardinality(entity):
    """Return entity's cardinality if some entity is given, else None."""
    if entity is None:
        return None
    return entity.user_cardinality


def _safe_concept_value(entity, concepts_language):
    """Return entity's targetted concept if some entity is given, else None."""
    if entity is None:
        return None
    return _concept_value(entity.concept, concepts_language)


class XAttr(namedtuple('_XAttr', ['name', 'qualified_type', 'cardinality', 'fixed_value'])):
    """Simple representation of an attribute element in a schema (RNG or XSD).

    Parameters:

    * `name`, the attribute's name,

    * `qualified_type`, its qualified type (e.g. 'xsd:string'),

    * `cardinality`, optional cardinality as string (None, '1' or '0..1') - default to '1' if some
      fixed value is provided, else to None (i.e. attribute is prohibited),

    * `fixed_value`, optional fixed value for the attribute.

    """
    def __new__(cls, name, qualified_type, cardinality='0..1', fixed_value=None):
        assert cardinality in (None, '1', '0..1'), cardinality
        if fixed_value is not None:
            cardinality = '1'
        return super(XAttr, cls).__new__(cls, name, qualified_type, cardinality, fixed_value)


LIST_VERSION_ID_2009 = XAttr('listVersionID', 'xsd:token', '1', 'edition 2009')
LIST_VERSION_ID_2011 = XAttr('listVersionID', 'xsd:token', '1', 'edition 2011')


class SEDA1XSDExport(SEDA2XSDExport):
    """Adapter to build an XSD representation of a simplified SEDA profile, using SEDA 1.0
    specification.

    The SEDA2XSDExport implementation may be driven by the SEDA 2.0 XSD model because it's used as
    the basis for the Yams model generation. We can't do the same thing with lower version of SEDA,
    hence the limitation to simplified profile, and a direct implementation of the export.
    """
    __regid__ = 'SEDA-1.0.xsd'
    __select__ = SEDA2XSDExport.__select__ & simplified_profile()

    namespaces = {
        None: 'fr:gouv:culture:archivesdefrance:seda:v1.0',
        'xsd': 'http://www.w3.org/2001/XMLSchema',
        'qdt': 'fr:gouv:culture:archivesdefrance:seda:v1.0:QualifiedDataType:1',
        'udt': 'urn:un:unece:uncefact:data:standard:UnqualifiedDataType:10',
        'clmDAFFileTypeCode': 'urn:un:unece:uncefact:codelist:draft:DAF:fileTypeCode:2009-08-18',
        'clmIANACharacterSetCode':
        'urn:un:unece:uncefact:codelist:standard:IANA:CharacterSetCode:2007-05-14',
        'clmIANAMIMEMediaType':
        'urn:un:unece:uncefact:codelist:standard:IANA:MIMEMediaType:2008-11-12',
        'clm60133': 'urn:un:unece:uncefact:codelist:standard:6:0133:40106',
    }
    root_attributes = {
        'targetNamespace': 'fr:gouv:culture:archivesdefrance:seda:v1.0',
        'attributeFormDefault': 'unqualified',
        'elementFormDefault': 'qualified',
        'version': '1.0',
    }

    concepts_language = 'seda-1'

    def element_schema(self, parent, name, xsd_type=None, fixed_value=None, cardinality='1',
                       documentation=None, xsd_attributes=()):
        attributes = {'name': name}
        if fixed_value is not None:
            attributes['fixed'] = text_type(fixed_value)
        if xsd_type is not None and not xsd_attributes:
            attributes['type'] = xsd_type
        assert cardinality in ('0..1', '0..n', '1', '1..n')
        if cardinality != '1':
            if cardinality[0] == '0':
                attributes['minOccurs'] = '0'
            if cardinality[-1] == 'n':
                attributes['maxOccurs'] = 'unbounded'
        if documentation:
            attributes['documentation'] = documentation
        element = self.element('xsd:element', parent, attributes)
        children_parent = None
        if xsd_type is None:
            attributes_parent = self.element('xsd:complexType', element)
            children_parent = self.element('xsd:sequence', attributes_parent)
        elif xsd_attributes:
            ct = self.element('xsd:complexType', element)
            scontent = self.element('xsd:simpleContent', ct)
            attributes_parent = self.element('xsd:extension', scontent, {'base': xsd_type})
        for xattr in xsd_attributes:
            self.attribute_schema(attributes_parent, xattr)
        return children_parent

    def attribute_schema(self, parent, xattr):
        attrs = {'name': xattr.name, 'type': xattr.qualified_type}
        if xattr.cardinality is None:
            attrs['use'] = 'prohibited'
        elif xattr.cardinality == '1':
            attrs['use'] = 'required'
        else:
            attrs['use'] = 'optional'
        if xattr.fixed_value is not None:
            attrs['fixed'] = text_type(xattr.fixed_value)
        self.element('xsd:attribute', parent, attrs)

    # business visit methods #######################################################################

    def dump_etree(self):
        """Return an XSD etree for the adapted SEDA profile."""
        root = self.element('xsd:schema', attributes=self.root_attributes)
        # self.element('xsd:import', parent=root,
        #              attributes={'namespace': 'http://www.w3.org/XML/1998/namespace',
        #                          'schemaLocation': 'http://www.w3.org/2001/xml.xsd'})
        self.xsd_transfer(root, self.entity)
        return root

    def xsd_transfer(self, parent, archive_transfer):
        """Append XSD elements for the archive transfer to the given parent node."""
        transfer_node = self.element_schema(parent, 'ArchiveTransfer',
                                            documentation=archive_transfer.title,
                                            xsd_attributes=[XAttr('Id', 'xsd:ID')])
        for comment in archive_transfer.comments:
            self.element_schema(transfer_node, 'Comment', 'udt:TextType',
                                fixed_value=comment.comment,
                                cardinality=comment.user_cardinality,
                                documentation=comment.user_annotation,
                                xsd_attributes=[XAttr('languageID', 'xsd:language')])
        self.element_schema(transfer_node, 'Date', 'udt:DateTimeType')
        self.element_schema(transfer_node, 'TransferIdentifier', 'qdt:ArchivesIDType',
                            xsd_attributes=self.xsd_attributes_scheme())
        for agency_type in ('TransferringAgency', 'ArchivalAgency'):
            self.xsd_agency(transfer_node, agency_type)

        for archive_unit in archive_transfer.archive_units:
            self.xsd_archive(transfer_node, archive_unit)

    def xsd_archive(self, parent, archive_unit):
        """Append XSD elements for an archive to the given parent node."""
        archive_node = self.element_schema(parent, 'Archive',
                                           cardinality=archive_unit.user_cardinality,
                                           documentation=archive_unit.user_annotation,
                                           xsd_attributes=[XAttr('Id', 'xsd:ID')])
        transfer = archive_unit.cw_adapt_to('ITreeBase').parent()
        self.xsd_archival_agreement(archive_node, transfer)
        # hard-coded description's language XXX fine, content language may be specified
        self.element_schema(archive_node, 'DescriptionLanguage', 'qdt:CodeLanguageType',
                            fixed_value='fra',
                            xsd_attributes=[LIST_VERSION_ID_2011])
        name_entity = self.archive_unit_name(archive_unit)
        self.element_schema(archive_node, 'Name', 'udt:TextType',
                            fixed_value=name_entity.title,
                            documentation=name_entity.user_annotation,
                            xsd_attributes=[XAttr('languageID', 'xsd:language')])
        content_entity = self.archive_unit_content(archive_unit)
        self.xsd_transferring_agency_archive_identifier(archive_node, content_entity,
                                                        'TransferringAgencyArchiveIdentifier')
        self.xsd_content_description(archive_node, content_entity)
        appraisal_rule_entity = self.archive_unit_appraisal_rule(archive_unit)
        if appraisal_rule_entity:
            self.xsd_appraisal_rule(archive_node, appraisal_rule_entity)
        # not optional in seda 1
        access_rule_entity = self.archive_unit_access_rule(archive_unit)
        self.xsd_access_rule(archive_node, access_rule_entity)
        self.xsd_children(archive_node, archive_unit)

    archive_object_tag_name = 'ArchiveObject'

    def xsd_archive_object(self, parent, archive_unit):
        """Append XSD elements for the archive object to the given parent node."""
        ao_node = self.element_schema(parent, self.archive_object_tag_name,
                                      cardinality=archive_unit.user_cardinality,
                                      documentation=archive_unit.user_annotation,
                                      xsd_attributes=[XAttr('Id', 'xsd:ID')])
        content_entity = self.archive_unit_content(archive_unit)
        self.element_schema(ao_node, 'Name', 'udt:TextType',
                            fixed_value=content_entity.title.title,
                            documentation=content_entity.title.user_annotation,
                            xsd_attributes=[XAttr('languageID', 'xsd:language')])
        self.xsd_transferring_agency_archive_identifier(ao_node, content_entity,
                                                        'TransferringAgencyObjectIdentifier')
        if (self.__regid__.startswith('SEDA-1.0')
                or content_entity.start_date
                or content_entity.end_date
                or content_entity.description
                or content_entity.keywords):
            self.xsd_content_description(ao_node, content_entity)
        appraisal_rule_entity = self.archive_unit_appraisal_rule(archive_unit)
        if appraisal_rule_entity:
            self.xsd_appraisal_rule(ao_node, appraisal_rule_entity)
        access_rule_entity = self.archive_unit_access_rule(archive_unit)
        if access_rule_entity:
            self.xsd_access_rule(ao_node, access_rule_entity)
        self.xsd_children(ao_node, archive_unit)

        return ao_node

    def xsd_document(self, parent, data_object):
        """Append XSD elements for the document to the given parent node."""
        document_node = self.element_schema(parent, 'Document',
                                            cardinality=data_object.user_cardinality,
                                            documentation=data_object.user_annotation,
                                            xsd_attributes=[XAttr('Id', 'xsd:ID')])

        self.xsd_system_id(document_node, data_object)
        self.xsd_attachment(document_node, data_object)
        self.xsd_date_created(document_node, data_object)
        self.xsd_document_type(document_node, data_object)

    def xsd_children(self, parent, entity):
        """Iter on archive/archive object children, which may be either
        archive objects or documents, and append XSD elements for them to the given parent node.
        """
        for au_or_bdo in entity.cw_adapt_to('ITreeBase').iterchildren():
            if au_or_bdo.cw_etype == 'SEDABinaryDataObject':
                self.xsd_document(parent, au_or_bdo)
            else:
                assert au_or_bdo.cw_etype == 'SEDAArchiveUnit'
                self.xsd_archive_object(parent, au_or_bdo)

    def xsd_attachment(self, parent, data_object):
        _safe_concept = partial(_safe_concept_value, concepts_language=self.concepts_language)

        format_id = data_object.format_id
        encoding = data_object.encoding
        mime_type = data_object.mime_type
        self.element_schema(parent, 'Attachment', 'qdt:ArchivesBinaryObjectType',
                            xsd_attributes=[
                                XAttr('format', 'clmDAFFileTypeCode:FileTypeCodeType',
                                      cardinality=_safe_cardinality(format_id),
                                      fixed_value=_safe_concept(format_id)),
                                XAttr('encodingCode',
                                      'clm60133:CharacterSetEncodingCodeContentType',
                                      cardinality=_safe_cardinality(encoding),
                                      fixed_value=_safe_concept(encoding)),
                                XAttr('mimeCode', 'clmIANAMIMEMediaType:MIMEMediaTypeContentType',
                                      cardinality=_safe_cardinality(mime_type),
                                      fixed_value=_safe_concept(mime_type)),
                                XAttr('filename', 'xsd:string',
                                      cardinality='0..1',
                                      fixed_value=data_object.filename),
                                # hard-coded attributes
                                XAttr('characterSetCode',
                                      'clmIANACharacterSetCode:CharacterSetCodeContentType',
                                      cardinality=None),
                                XAttr('uri', 'xsd:anyURI',
                                      cardinality=None),
                            ])

    def xsd_date_created(self, parent, data_object):
        date_created = data_object.date_created_by_application
        if date_created:
            self.element_schema(parent, 'Creation', 'udt:DateTimeType',
                                cardinality=date_created.user_cardinality,
                                documentation=date_created.user_annotation)

    def xsd_document_type(self, parent, data_object):
        references = list(data_object.referenced_by)
        assert len(references) == 1, (
            'Unexpected number of references in document {} of {}: {}'.format(
                data_object.eid, data_object.container[0].eid, references))
        seq = references[0]
        self.element_schema(parent, 'Type', 'qdt:CodeDocumentType',
                            fixed_value=_safe_concept_value(seq.type, self.concepts_language),
                            xsd_attributes=[LIST_VERSION_ID_2009])

    system_id_tag_name = 'ArchivalAgencyDocumentIdentifier'

    def xsd_system_id(self, parent, data_object):
        system_id = self.system_id(data_object)
        if system_id:
            self.element_schema(parent, self.system_id_tag_name, 'qdt:ArchivesIDType',
                                cardinality=system_id.user_cardinality,
                                documentation=system_id.user_annotation,
                                xsd_attributes=self.xsd_attributes_scheme())

    def xsd_agency(self, parent, agency_type, agency=None):
        agency_node = self.element_schema(parent, agency_type,
                                          cardinality=agency.user_cardinality if agency else '1')
        self.element_schema(agency_node, 'Identification', 'qdt:ArchivesIDType',
                            fixed_value=self.agency_id(agency) if agency else None,
                            xsd_attributes=self.xsd_attributes_scheme())
        self.element_schema(agency_node, 'Name', 'udt:TextType',
                            fixed_value=self.agency_name(agency) if agency else None,
                            cardinality='0..1')

    def xsd_archival_agreement(self, parent, transfer):
        agreement = transfer.archival_agreement
        if agreement:
            self.element_schema(parent, 'ArchivalAgreement', 'qdt:ArchivesIDType',
                                cardinality=agreement.user_cardinality,
                                documentation=agreement.user_annotation,
                                fixed_value=agreement.archival_agreement,
                                xsd_attributes=self.xsd_attributes_scheme())

    def xsd_transferring_agency_archive_identifier(self, parent, content_entity, tag_name):
        if content_entity.transferring_agency_archive_unit_identifier:
            agency_entity = content_entity.transferring_agency_archive_unit_identifier
            self.element_schema(
                parent, tag_name, 'qdt:ArchiveIDType',
                fixed_value=agency_entity.transferring_agency_archive_unit_identifier,
                cardinality=agency_entity.user_cardinality,
                documentation=agency_entity.user_annotation,
                xsd_attributes=self.xsd_attributes_scheme())

    def xsd_appraisal_rule(self, parent, appraisal_rule):
        # XXX cardinality 1 on rule, not multiple + element name : 'Appraisal' ou 'AppraisalRule'
        # (cf http://www.archivesdefrance.culture.gouv.fr/seda/api/index.html)
        ar_node = self.element_schema(parent, 'Appraisal',
                                      cardinality=appraisal_rule.user_cardinality,
                                      documentation=appraisal_rule.user_annotation,
                                      xsd_attributes=[XAttr('Id', 'xsd:ID')])
        ar_code = appraisal_rule.final_action_concept
        ar_code_value = _concept_value(ar_code, self.concepts_language)
        self.element_schema(ar_node, 'Code', 'qdt:CodeAppraisalType',
                            fixed_value=ar_code_value,
                            xsd_attributes=[LIST_VERSION_ID_2009])

        rule = appraisal_rule.rules[0] if appraisal_rule.rules else None
        value = _concept_value(rule.rule_concept, self.concepts_language) if rule else None
        self.element_schema(ar_node, 'Duration', 'qdt:ArchivesDurationType',
                            fixed_value=value,
                            documentation=rule.user_annotation if rule else None)
        self.element_schema(ar_node, 'StartDate', 'udt:DateType')

    access_restriction_tag_name = 'AccessRestrictionRule'

    def xsd_access_rule(self, parent, access_rule):
        """Append XSD elements for an access restriction to the given parent node."""
        ar_node = self.element_schema(parent, self.access_restriction_tag_name,
                                      cardinality=access_rule.user_cardinality,
                                      documentation=access_rule.user_annotation,
                                      xsd_attributes=[XAttr('Id', 'xsd:ID')])
        # XXX cardinality 1
        rule = access_rule.rules[0] if access_rule.rules else None
        value = _concept_value(rule.rule_concept, self.concepts_language) if rule else None
        self.element_schema(ar_node, 'Code', 'qdt:CodeAccessRestrictionType',
                            fixed_value=value,
                            documentation=rule.user_annotation if rule else None,
                            xsd_attributes=[LIST_VERSION_ID_2009])
        self.element_schema(ar_node, 'StartDate', 'udt:DateType')

    def xsd_content_description(self, parent, content):
        """Append XSD elements for a description content to the given parent node"""
        cd_node = self.element_schema(parent, 'ContentDescription',
                                      xsd_attributes=[XAttr('Id', 'xsd:ID')])
        self.xsd_description_level(cd_node, content.description_level_concept)
        self.xsd_language(cd_node, content)
        self.xsd_content_dates(cd_node, content)
        self.xsd_description(cd_node, content)
        self.xsd_custodial_history(cd_node, content)
        self.xsd_keywords(cd_node, content)
        self.xsd_originating_agency(cd_node, content)

    def xsd_language(self, parent, content):
        # XXX language is 0..1 in SEDA 2, 1..n in earlier version
        language = content.language.concept if content.language else None
        self.element_schema(parent, 'Language', 'qdt:CodeLanguageType',
                            fixed_value=_concept_value(language, self.concepts_language),
                            xsd_attributes=[LIST_VERSION_ID_2009])

    def xsd_content_dates(self, parent, content):
        for seda2_name, seda1_name in (('end', 'latest'), ('start', 'oldest')):
            date_entity = getattr(content, '%s_date' % seda2_name)
            if date_entity:
                self.element_schema(parent, '%sDate' % seda1_name.capitalize(), 'udt:DateType',
                                    cardinality=date_entity.user_cardinality,
                                    documentation=date_entity.user_annotation)

    def xsd_description_level(self, parent, concept):
        """Append XSD elements for a description level to the given parent node"""
        value = _concept_value(concept, self.concepts_language)
        self.element_schema(parent, 'DescriptionLevel', 'qdt:CodeDescriptionLevelType',
                            fixed_value=value,
                            xsd_attributes=[LIST_VERSION_ID_2009])

    def xsd_description(self, parent, content):
        """Append XSD elements for a description to the given parent node"""
        if content.description:
            self.element_schema(parent, 'Description', 'udt:TextType',
                                cardinality=content.description.user_cardinality,
                                documentation=content.description.user_annotation,
                                fixed_value=content.description.description,
                                xsd_attributes=[XAttr('languageID', 'xsd:language')])

    def xsd_keywords(self, parent, content):
        for keyword in content.keywords:
            self.xsd_keyword(parent, keyword)

    def xsd_custodial_history(self, parent, content):
        if content.custodial_history_items:
            ch_node = self.element_schema(parent, 'CustodialHistory',
                                          cardinality='0..1')
            for item in content.custodial_history_items:
                when_card = item.when.user_cardinality if item.when else None
                self.element_schema(ch_node, 'CustodialHistoryItem', 'qdt:CustodialHistoryItemType',
                                    cardinality=item.user_cardinality,
                                    documentation=item.user_annotation,
                                    xsd_attributes=[XAttr('when', 'udt:DateType',
                                                          cardinality=when_card),
                                                    XAttr('languageID', 'xsd:language')])

    def xsd_originating_agency(self, parent, content):
        if content.originating_agency:
            self.xsd_agency(parent, 'OriginatingAgency', content.originating_agency)

    # extracted from xsd_keyword to allow parametrization for SEDA 1.0 vs 0.2 generation
    kw_tag_name = 'Keyword'
    kw_content_tag_type = 'qdt:KeywordContentType'
    kw_content_tag_attributes = [XAttr('role', 'xsd:token'),
                                 XAttr('languageID', 'xsd:language')]

    def xsd_keyword(self, parent, keyword):
        """Append XSD elements for a keyword to the given parent node"""
        kw_node = self.element_schema(parent, self.kw_tag_name,
                                      cardinality=keyword.user_cardinality,
                                      documentation=keyword.user_annotation,
                                      xsd_attributes=[XAttr('Id', 'xsd:ID')])
        content = keyword.keyword_content
        url = None
        if keyword.reference:
            concept = keyword.reference.concept
            if concept:
                url = self.cwuri_url(concept)
                if content is None:
                    content = concept.label()
        self.element_schema(kw_node, 'KeywordContent', self.kw_content_tag_type,
                            fixed_value=content,
                            xsd_attributes=self.kw_content_tag_attributes)
        if keyword.reference:
            scheme = keyword.reference.scheme
            self.element_schema(kw_node, 'KeywordReference', 'qdt:ArchivesIDType',
                                cardinality=keyword.reference.user_cardinality,
                                documentation=keyword.reference.user_annotation,
                                fixed_value=url,
                                xsd_attributes=self.xsd_attributes_scheme(scheme))
        if keyword.type:
            self.element_schema(kw_node, 'KeywordType', 'qdt:CodeKeywordType',
                                cardinality=keyword.type.user_cardinality,
                                documentation=keyword.type.user_annotation,
                                fixed_value=_concept_value(keyword.type.concept,
                                                           self.concepts_language),
                                xsd_attributes=[LIST_VERSION_ID_2009])

    @classmethod
    def xsd_attributes_scheme(cls, scheme=None):
        """Return a list of :class:`XAttr` for a scheme definition, with some proper values
        specified if a scheme is given.
        """
        attributes = [
            XAttr('schemeID', 'xsd:token'),
            XAttr('schemeName', 'xsd:string',
                  fixed_value=scheme.title if scheme and scheme.title else None),
            XAttr('schemeAgencyName', 'xsd:string'),
            XAttr('schemeVersionID', 'xsd:token'),
            XAttr('schemeDataURI', 'xsd:anyURI'),
            XAttr('schemeURI', 'xsd:anyURI',
                  fixed_value=cls.cwuri_url(scheme) if scheme else None),
        ]
        # if scheme is not None:
        #     # schemeID XXX move to saem
        #     attributes[0]['fixed'] = scheme.ark
        #     attributes[0]['use'] = 'required'
        return attributes

    def archive_unit_access_rule(self, archive_unit):
        for rule_holder in climb_rule_holders(archive_unit):
            if rule_holder.reverse_seda_access_rule:
                return rule_holder.reverse_seda_access_rule[0]
        return None

    def archive_unit_name(self, archive_unit):
        seq = archive_unit.first_level_choice.content_sequence
        return seq.title

    def archive_unit_appraisal_rule(self, archive_unit):
        for rule_holder in climb_rule_holders(archive_unit):
            if rule_holder.reverse_seda_appraisal_rule:
                return rule_holder.reverse_seda_appraisal_rule[0]
        return None

    def agency_name(self, agency):
        return agency.agency.dc_title() if agency and agency.agency else None

    def agency_id(self, agency):
        return text_type(agency.agency.eid) if agency and agency.agency else None

    def archive_unit_content(self, archive_unit):
        return archive_unit.first_level_choice.content_sequence

    def system_id(self, data_object):
        return (data_object.cw_adapt_to('ITreeBase').parent().first_level_choice.content_sequence
                .system_id)

    @staticmethod
    def cwuri_url(entity):
        """Return "public" URI for the given entity.

        In a staticmethod to ease overriding in subclasses (eg saem).
        """
        return entity.cwuri


class SEDA02XSDExport(SEDA1XSDExport):
    """Adapter to build an XSD representation of a SEDA profile, using SEDA 0.2 specification"""
    __regid__ = 'SEDA-0.2.xsd'

    namespaces = SEDA1XSDExport.namespaces.copy()
    namespaces[None] = 'fr:gouv:ae:archive:draft:standard_echange_v0.2'
    namespaces['qdt'] = 'fr:gouv:ae:archive:draft:standard_echange_v0.2:QualifiedDataType:1'
    namespaces['udt'] = 'urn:un:unece:uncefact:data:standard:UnqualifiedDataType:6'

    root_attributes = SEDA1XSDExport.root_attributes.copy()
    root_attributes['targetNamespace'] = 'fr:gouv:ae:archive:draft:standard_echange_v0.2'
    root_attributes['version'] = '1.1'

    def xsd_archive(self, parent, archive_unit):
        """Append XSD elements for an archive to the given parent node."""
        archive_node = self.element_schema(parent, 'Contains',
                                           cardinality=archive_unit.user_cardinality,
                                           documentation=archive_unit.user_annotation,
                                           xsd_attributes=[XAttr('Id', 'xsd:ID')])
        transfer = archive_unit.cw_adapt_to('ITreeBase').parent()
        self.xsd_archival_agreement(archive_node, transfer)
        # hard-coded description's language
        self.element_schema(archive_node, 'DescriptionLanguage', 'qdt:CodeLanguageType',
                            fixed_value='fr',
                            xsd_attributes=[LIST_VERSION_ID_2009])
        # in SEDA 0.2, description level is on the archive element, not on its content description
        content_entity = self.archive_unit_content(archive_unit)
        self.xsd_description_level(archive_node, content_entity.description_level_concept)
        name_entity = self.archive_unit_name(archive_unit)
        self.element_schema(archive_node, 'Name', 'udt:TextType',
                            fixed_value=name_entity.title,
                            documentation=name_entity.user_annotation,
                            xsd_attributes=[XAttr('languageID', 'xsd:language')])
        self.xsd_transferring_agency_archive_identifier(archive_node, content_entity,
                                                        'TransferringAgencyArchiveIdentifier')
        self.xsd_content_description(archive_node, content_entity)

        appraisal_rule_entity = self.archive_unit_appraisal_rule(archive_unit)
        if appraisal_rule_entity:
            self.xsd_appraisal_rule(archive_node, appraisal_rule_entity)
        # in SEDA 0.2, access restriction is not mandatory
        access_rule_entity = self.archive_unit_access_rule(archive_unit)
        if access_rule_entity:
            self.xsd_access_rule(archive_node, access_rule_entity)
        self.xsd_children(archive_node, archive_unit)
        return archive_node

    def xsd_archive_object(self, parent, archive_unit):
        """Append XSD elements for the archive object to the given parent node."""
        ao_node = super(SEDA02XSDExport, self).xsd_archive_object(parent, archive_unit)
        # in SEDA 0.2, description level is on the archive object element, not on its content
        # description
        content_entity = self.archive_unit_content(archive_unit)
        self.xsd_description_level(ao_node, content_entity.description_level_concept)
        # actually DescriptionLevel should be before Name (ie. currently the last and first
        # elements)
        ao_node.insert(0, ao_node[-1])

    def xsd_document(self, parent, data_object):
        """Append XSD elements for the document to the given parent node."""
        document_node = self.element_schema(parent, 'Document',
                                            cardinality=data_object.user_cardinality,
                                            documentation=data_object.user_annotation,
                                            xsd_attributes=[XAttr('Id', 'xsd:ID')])

        self.xsd_attachment(document_node, data_object)
        self.xsd_date_created(document_node, data_object)
        self.xsd_system_id(document_node, data_object)
        self.xsd_document_type(document_node, data_object)

    def xsd_content_description(self, parent, content):
        """Append XSD elements for a description content to the given parent node"""
        cd_node = self.element_schema(parent, 'ContentDescription',
                                      xsd_attributes=[XAttr('Id', 'xsd:ID')])
        self.xsd_custodial_history(cd_node, content)
        self.xsd_language(cd_node, content)
        self.xsd_content_dates(cd_node, content)
        self.xsd_description(cd_node, content)
        self.xsd_originating_agency(cd_node, content)
        self.xsd_keywords(cd_node, content)

    def xsd_custodial_history(self, parent, content):
        if content.custodial_history_items:
            item = content.custodial_history_items[0]
            self.element_schema(parent, 'CustodialHistory', 'udt:TextType',
                                cardinality=item.user_cardinality,
                                documentation=item.user_annotation,
                                xsd_attributes=[XAttr('languageID', 'xsd:language')])

    system_id_tag_name = 'Identification'
    # in SEDA 0.2, ArchiveObject tag name is 'Contains' (as for Archive)
    archive_object_tag_name = 'Contains'
    # in SEDA 0.2, AccessRestrictionRule tag name is 'AccessRestriction'
    access_restriction_tag_name = 'AccessRestriction'
    # in SEDA 0.2, keyword tag name is 'ContentDescriptive', not 'Keyword' and keyword content type
    # is TextType and there is no 'role' attribute
    kw_tag_name = 'ContentDescriptive'
    kw_content_tag_type = 'udt:TextType'
    kw_content_tag_attributes = [XAttr('languageID', 'xsd:language')]


class OldSEDARNGExportMixin(RNGMixin):

    def element_schema(self, parent, name, xsd_type=None, fixed_value=None, cardinality='1',
                       documentation=None, xsd_attributes=()):
        attributes = {'name': name}
        if documentation:
            attributes['documentation'] = documentation
        parent = self.rng_element_parent(parent, *minmax_cardinality(cardinality))
        element = self.element('rng:element', parent, attributes)
        for xattr in xsd_attributes:
            self.attribute_schema(element, xattr)

        if xsd_type is not None:
            self.rng_value(element, xsd_type, fixed_value)
        else:
            assert fixed_value is None
        return element

    def attribute_schema(self, parent, xattr):
        if xattr.cardinality is None:
            return  # XXX prohibit?
        minimum = minmax_cardinality(xattr.cardinality, ('0..1', '1'))[0]
        parent = self.rng_element_parent(parent, minimum)
        attr = self.element('rng:attribute', parent, {'name': xattr.name})
        self.rng_value(attr, xattr.qualified_type, xattr.fixed_value)

    def dump_etree(self):
        """Return an RNG etree for the adapted SEDA profile."""
        root = self.element('rng:grammar', attributes=self.root_attributes)
        start = self.element('rng:start', root)
        self.xsd_transfer(start, self.entity)
        return root


class SEDA1RNGExport(OldSEDARNGExportMixin, SEDA1XSDExport):
    """Adapter to build an RNG representation of a simplified SEDA profile, using SEDA 1.0
    specification.
    """
    __regid__ = 'SEDA-1.0.rng'

    namespaces = SEDA1XSDExport.namespaces.copy()
    namespaces['rng'] = 'http://relaxng.org/ns/structure/1.0'
    root_attributes = {
        'ns': 'fr:gouv:culture:archivesdefrance:seda:v1.0',
        'datatypeLibrary': 'http://www.w3.org/2001/XMLSchema-datatypes',
    }


class SEDA02RNGExport(OldSEDARNGExportMixin, SEDA02XSDExport):
    """Adapter to build an RNG representation of a simplified SEDA profile, using SEDA 0.2
    specification.
    """
    __regid__ = 'SEDA-0.2.rng'

    namespaces = SEDA1XSDExport.namespaces.copy()
    namespaces['rng'] = 'http://relaxng.org/ns/structure/1.0'
    root_attributes = {
        'ns': 'fr:gouv:ae:archive:draft:standard_echange_v0.2',
        'datatypeLibrary': 'http://www.w3.org/2001/XMLSchema-datatypes',
    }


def xsd_element_cardinality(occ, card_entity):
    """Return XSD element cardinality for the given pyxst Occurence. Cardinality may be overriden by
    the data model's user_cardinality value.
    """
    minimum, maximum = element_minmax_cardinality(occ, card_entity)
    attribs = {}
    if minimum != 1:
        attribs['minOccurs'] = str(minimum)
    if maximum != 1:
        attribs['maxOccurs'] = 'unbounded'
    return attribs


def xsd_attribute_cardinality(occ, card_entity):
    """Return XSD attribute cardinality for the given pyxst Occurence. Cardinality may be overriden by
    the data model's user_cardinality value.
    """
    if attribute_minimum_cardinality(occ, card_entity) == 1:
        return {'use': 'required'}
    else:
        return {'use': 'optional'}


def xsd_cleanup_etree(element):
    """Cleanup given XSD element tree.

    * forces attributes to be defined after sequence/choices (enforced by XSD schema),
    * remove empty sequence/choice,
    * skip sequence/choice with only one child and which are either not a complexType child or their
      unique children is itself a sequence or choice.
    """
    for subelement in list(element):
        xsd_cleanup_etree(subelement)
        if subelement.tag == '{http://www.w3.org/2001/XMLSchema}attribute':
            element.remove(subelement)
            element.append(subelement)
        elif (subelement.tag in ('{http://www.w3.org/2001/XMLSchema}sequence',
                                 '{http://www.w3.org/2001/XMLSchema}choice',
                                 '{http://www.w3.org/2001/XMLSchema}complexType')
              and len(subelement) == 0):
            element.remove(subelement)
        elif (subelement.tag in ('{http://www.w3.org/2001/XMLSchema}sequence',
                                 '{http://www.w3.org/2001/XMLSchema}choice')
              and len(subelement) == 1
              and (element.tag != '{http://www.w3.org/2001/XMLSchema}complexType'
                   or subelement[0].tag in ('{http://www.w3.org/2001/XMLSchema}sequence',
                                            '{http://www.w3.org/2001/XMLSchema}choice'))):
            element.replace(subelement, subelement[0])


def _path_target_values(entity, path):
    """Given an entity and a path to traverse, return the list of (entity, value) at the end of the
    path.

    Values may be entities or final value if the last relation in the path is an attribute. Values
    are associated to the entity holding their cardinality, which may be either the given entity or
    an intermediary entity.
    """
    is_simple = len(path) == 1
    if is_simple:
        (rtype, role, target_etype, _), = path
        return _simple_path_target_values(entity, rtype, role, target_etype)
    else:
        return _complex_path_target_values(entity, path)


def _simple_path_target_values(entity, rtype, role, target_etype):
    if target_etype in BASE_TYPES:
        if rtype == 'id':
            return [(None, eid2xmlid(entity.eid))]
        return [(None, getattr(entity, rtype, None))]
    targets = entity.related(rtype, role, entities=True)
    rschema = entity._cw.vreg.schema.rschema
    rdefschema = next(iter(rschema(rtype).rdefs.values()))
    # data_object_reference_id is artificially composite to ease the case of simplified profile
    # (set explicitly in schema/__init__.py)
    if rtype != 'seda_data_object_reference_id' and rdefschema.composite:
        return [(target, target) for target in targets]
    elif targets:
        return [(None, target) for target in targets]
    else:
        return [(None, None)]


def _complex_path_target_values(entity, path):
    rschema = entity._cw.vreg.schema.rschema
    entities = (entity,)
    rtype_targets = []
    for rtype, role, target_etype, _ in path:
        try:
            rdefschema = next(iter(rschema(rtype).rdefs.values()))
        except KeyError:
            if rtype in SKIP_ATTRS:
                return [(e, None) for e in entities]
            # element is still in the intermediary representation but not in the schema
            return [(None, None)]
        rtype_targets = []
        for entity in entities:
            if target_etype in BASE_TYPES:
                rtype_targets.append((entity, getattr(entity, rtype, None)))
            else:
                try:
                    targets = entity.related(rtype, role, entities=True)
                except KeyError:
                    # the relation is not defined in the schema: element is not modelized but should
                    # be added in the XSD
                    rtype_targets.append((entity, None))
                    continue
                if targets:
                    rtype_targets += [(entity, t) for t in targets]
                # if relation is not composite, that means it's a "value" relation, hence we should
                # always emit a value (its associated XSD element must be defined)
                elif not rdefschema.composite:
                    rtype_targets.append((entity, None))
        entities = [v for e, v in rtype_targets]
    return rtype_targets


def xselement_scheme_attribute(xselement):
    try:
        return xselement.attributes['listSchemeURI'].target.local_name
    except KeyError:
        return xselement.attributes['schemeURI'].target.local_name
