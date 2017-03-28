from lxml import etree as ET

from rdflib import Namespace, URIRef, Literal, RDF

from .identified import Identified
from .types import *
from .namespaces import SBOL, NS


class Location(Identified):
    """
    Mixin for use in Location classes
    """
    def __init__(self,
                 identity,
                 orientation=None,
                 **kwargs):
        super().__init__(identity, **kwargs)
        self.orientation = orientation

    def _as_rdf_xml(self, ns):
        elements = super()._as_rdf_xml(ns)
        if self.orientation is not None:
            elements.append(ET.Element(NS('sbol', 'orientation'),
                                       attrib={NS('rdf', 'resource'): self.orientation}))
        return elements

class Range(Location):
    """
    Specifies a region via discrete, inclusive start and end positions for a Sequence
    """
    def __init__(self,
                 identity,
                 start,
                 end,
                 **kwargs):
        super().__init__(identity, **kwargs)
        self.start = start
        self.end = end

    def _as_rdf_xml(self, ns):
        elements = super()._as_rdf_xml(ns)
        range_elem = ET.Element(NS('sbol', 'Range'),
                                attrib={NS('rdf', 'about'): self.rdf_identity})
        range_elem.extend(elements)
        start_elem = ET.SubElement(range_elem, NS('sbol', 'start'))
        start_elem.text = str(self.start)
        end_elem = ET.SubElement(range_elem, NS('sbol', 'end'))
        end_elem.text = str(self.end)
        return range_elem

class Cut(Location):
    """
    Specifies a region between two discrete positions in a Sequence
    """
    def __init__(self,
                 identity,
                 at,
                 **kwargs):
        super().__init__(identity, **kwargs)
        self.at = at

    def _as_rdf_xml(self, ns):
        elements = super()._as_rdf_xml(ns)
        cut_elem = ET.Element(NS('sbol', 'Cut'),
                                attrib={NS('rdf', 'about'): self.rdf_identity})
        cut_elem.extend(elements)
        at_elem = ET.SubElement(cut_elem, NS('sbol', 'at'))
        at_elem.text = self.at
        return cut_elem


class GenericLocation(Location):
    """
    Specifies regions with different encoding properties and potentially nonlinear structure
    """
    def __init__(self,
                 identity,
                 **kwargs):
        super().__init__(identity, **kwargs)

    def _as_rdf_xml(self, ns):
        elements = super()._as_rdf_xml(ns)
        generic_elem = ET.Element(NS('sbol', 'GenericLocation'),
                                  attrib={NS('rdf', 'about'): self.rdf_identity})
        generic_elem.extend(elements)
        return generic_elem
