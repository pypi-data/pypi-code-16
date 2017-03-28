from lxml import etree as ET

from .identified import TopLevel, GenericTopLevel
from .namespaces import NS


class Collection(TopLevel):
    """
    Groups together a set of TopLevel objects that have something in common
    """
    def __init__(self,
                 identity,
                 members=[],
                 **kwargs):
        super().__init__(identity, **kwargs)
        self.members = members

    @property
    def members(self):
        return self._members

    @members.setter
    def members(self, value):
        if not isinstance(value, list):
            raise Exception('Must provide a list of TopLevel objects')
        self._members = value

    def _as_rdf_xml(self, ns):
        elements = super()._as_rdf_xml(ns)
        collection = ET.Element(NS('sbol', 'Collection'), attrib={NS('rdf', 'about'):
                                                                  self.rdf_identity})
        collection.extend(elements)
        for m in self.members:
            member = ET.SubElement(collection, NS('sbol', 'member'),
                                   attrib={NS('rdf', 'resource'): m._get_identity(ns)})
        return collection
