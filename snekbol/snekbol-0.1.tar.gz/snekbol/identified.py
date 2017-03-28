import re

from lxml import etree as ET

from rdflib import BNode, URIRef, Literal, RDF
from rdflib.namespace import DCTERMS

import validators

from .namespaces import SBOL, PROV, XML_NS, NS


class Identified(object):
    """
    Mixin to provide identity support to SBOL objects
    """
    def __init__(self,
                 identity,
                 name = None,
                 was_derived_from = None,
                 version = None,
                 description = None,
                 display_id = None,
                 annotations=[]):
        self.identity = identity
        self.name = name
        self.was_derived_from = was_derived_from
        self.version = version
        self.description = description
        self.display_id = display_id
        self.annotations = annotations

        if display_id is None:
            self.display_id = re.sub('[\W_]+', '_', identity)

    @property
    def persistent_identitity(self):
        return '{}/{}'.format(self.display_id, self.version)

    def _get_identity(self, namespace=None, postfix=None):
        identity = self.identity
        if postfix is not None:
            identity = '{}{}'.format(self.identity, postfix)
        if not validators.url(identity):
            return namespace[identity]
        else:
            return identity

    def _get_persistent_identitity(self, namespace):
        if self.version is not None:
            return '{}/{}/{}'.format(self._get_identity(namespace), self.display_id, self.version)
        return '{}'.format(self._get_identity(namespace))

    def _get_rdf_identity(self, namespace=None, postfix=None):
        identity = self.identity
        if postfix is not None:
            identity = '{}{}'.format(self.identity, postfix)
        if not validators.url(identity):
            return URIRef(namespace[identity])
        else:
            return URIRef(identity)

    def _get_rdf_persistent_identitity(self, namespace):
        if self.version is not None:
            return URIRef('{}/{}'.format(self._get_rdf_identity(namespace), self.version))
        return self._get_rdf_identity(namespace)

    def _as_rdf_xml(self, ns):
        """
        Return identity details for the element as XML nodes
        """
        self.rdf_identity = self._get_identity(ns)
        elements = []
        elements.append(ET.Element(NS('sbol', 'persistentIdentity'),
                                   attrib={NS('rdf', 'resource'):
                                           self._get_persistent_identitity(ns)}))
        if self.name is not None:
            name = ET.Element(NS('dcterms', 'title'))
            name.text = self.name
            elements.append(name)
        if self.display_id is not None:
            display_id = ET.Element(NS('sbol', 'displayId'))
            display_id.text = self.display_id
            elements.append(display_id)
        if self.version is not None:
            version = ET.Element(NS('sbol', 'version'))
            version.text = self.version
            elements.append(version)
        if self.was_derived_from is not None:
            elements.append(ET.Element(NS('prov', 'wasDerivedFrom'),
                                       attrib={NS('rdf', 'resource'): self.was_derived_from}))
        if self.description is not None:
            description = ET.Element(NS('dcterms', 'description'))
            description.text = self.description
            elements.append(description)
        for a in self.annotations:
            elements.append(a._as_rdf_xml(ns))
        return elements


class TopLevel(Identified):
    """
    Mixin to indicate SBOL object is top level and should not be nested
    """
    isToplevel = True

    def __init__(self, identity, **kwargs):
        super().__init__(identity, **kwargs)


class GenericTopLevel(TopLevel):
    def __init__(self, identity, rdf_type, **kwargs):
        super().__init__(identity, **kwargs)
        self.rdf_type = rdf_type

    def _as_rdf_xml(self, ns):
        elements = super()._as_rdf_xml(ns)
        generic = ET.Element(NS(self.rdf_type.prefix, self.rdf_type.local_name),
                             attrib={NS('rdf', 'about'): self.rdf_identity})
        generic.extend(elements)
        return generic
