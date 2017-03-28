from lxml import etree as ET

from rdflib import Namespace, URIRef, Literal, RDF

from .identified import Identified
from .types import *
from .namespaces import SBOL, NS

class Sequence(Identified):
    """
    Represents the primary structure of a ComponentDefinition
    """
    def __init__(self,
                 identity,
                 elements,
                 encoding='DNA',
                 fromURI=False,
                 **kwargs):
        super().__init__(identity, **kwargs)

        self._encoding = None

        self.encoding = encoding
        self.elements = elements

    def __str__(self):
        return 'Sequence: {}'.format(self.identity)

    @property
    def encoding(self):
        return self._encoding

    @encoding.setter
    def encoding(self, value):
        self._encoding = checktype(value, ENCODING_URI)

    def _as_rdf_xml(self, ns):
        elements = super()._as_rdf_xml(ns)
        sequence = ET.Element(NS('sbol', 'Sequence'), attrib={NS('rdf', 'about'):
                                                              self.rdf_identity})
        sequence.extend(elements)
        element_elem = ET.Element(NS('sbol', 'elements'))
        element_elem.text = self.elements
        sequence.append(element_elem)
        sequence.append(ET.Element(NS('sbol', 'encoding'), attrib={NS('rdf', 'resource'):
                                                                   self.encoding}))
        return sequence


class SequenceAnnotation(Identified):
    """
    Describes one or more regions of interest on a Sequence object
    """
    def __init__(self,
                 identity,
                 locations,
                 component=None,
                 roles=[],
                 **kwargs):
        super().__init__(identity, **kwargs)
        self.locations = locations
        self.component = component
        self.roles = roles

    def _as_rdf_xml(self, ns):
        elements = super()._as_rdf_xml(ns)
        sap = ET.Element(NS('sbol', 'sequenceAnnotation'))
        sequence_annotation = ET.SubElement(sap, NS('sbol', 'SequenceAnnotation'),
                                            attrib={NS('rdf', 'about'): self.rdf_identity})
        sequence_annotation.extend(elements)
        if self.component is not None:
            ET.SubElement(sequence_annotation,
                          NS('sbol', 'component'), attrib={NS('rdf', 'resource'):
                                                           self.component._get_identity(ns)})
        for r in self.roles:
            ET.SubElement(sequence_annotation, NS('sbol', 'role'),
                          attrib={NS('rdf', 'resource'): r})
        for l in self.locations:
            location = ET.SubElement(sequence_annotation, NS('sbol', 'location'))
            location.append(l._as_rdf_xml(ns))
        return sap


class SequenceConstraint(Identified):
    """
    Assert restrictions on the relative, sequence-based positions of pairs of Component objects
    """
    def __init__(self,
                 identity,
                 subject,
                 obj,
                 restriction,
                 **kwargs):
        super().__init__(identity, **kwargs)
        self.subject = subject
        self.obj = obj
        self.restriction = restriction

    def _as_rdf_xml(self, ns):
        elements = super()._as_rdf_xml(ns)
        scp = ET.Element(NS('sbol', 'sequenceConstraint'))
        sequence_constraint = ET.SubElement(scp, NS('sbol', 'SequenceConstraint'),
                                            attrib={NS('rdf', 'about'): self.rdf_identity})
        sequence_constraint.extend(elements)
        sequence_constraint.append(ET.Element(NS('sbol', 'restriction'),
                                              attrib={NS('rdf', 'resource'): self.restriction}))
        sequence_constraint.append(ET.Element(NS('sbol', 'subject'),
                                              attrib={NS('rdf', 'resource'):
                                                      self.subject._get_identity(ns)}))
        sequence_constraint.append(ET.Element(NS('sbol', 'object'),
                                              attrib={NS('rdf', 'resource'):
                                                      self.obj._get_identity(ns)}))
        return scp
