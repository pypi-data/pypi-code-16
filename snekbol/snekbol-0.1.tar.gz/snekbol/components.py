from lxml import etree as ET

from rdflib import Namespace, URIRef, Literal, RDF, RDFS

from .identified import Identified
from .types import *
from .namespaces import SBOL, NS


class ComponentInstance(Identified):
    """
    Mixin for use in nesting component definitions
    """
    def __init__(self,
                 identity,
                 definition,
                 access,
                 maps_to=[],
                 **kwargs):
        super().__init__(identity, **kwargs)
        self.access = access
        self.definition = definition
        self.maps_to = maps_to

    @property
    def access(self):
        return self._access

    @access.setter
    def access(self, value):
        if value not in ACCESS_TYPES.values():
            try:
                value = ACCESS_TYPES[value]
            except KeyError:
                raise Exception('Must supply a valid access type')
        self._access = value

    def _as_rdf_xml(self, ns):
        elements = super()._as_rdf_xml(ns)
        elements.append(ET.Element(NS('sbol', 'access'),
                                   attrib={NS('rdf', 'resource'): self.access}))
        elements.append(ET.Element(NS('sbol', 'definition'),
                                   attrib={NS('rdf', 'resource'):
                                           self.definition._get_identity(ns)}))
        if self.maps_to is not None:
            for m in self.maps_to:
                elements.append(m._as_rdf_xml(ns))
        return elements

    def _as_rdf_triplets(self, ns):
        triplets = super()._as_rdf_triplets(ns)
        component = self.rdf_identity
        triplets.append((component,
                         SBOL.access,
                         URIRef(self.access)))
        triplets.append((component,
                         SBOL.definition,
                         self.component_definition._get_rdf_identity(ns, postfix='/')))
        if self.maps_to is not None:
            for m in self.maps_to:
                triplets.extend(m._as_rdf_triplets(ns))
        return triplets



class Component(ComponentInstance):
    """
    Compose ComponentDefinition objects into a structural hierarchy
    """
    def __init__(self,
                 identity,
                 definition,
                 access,
                 roles=None,
                 role_integration=None,
                 **kwargs):
        super().__init__(identity,
                         definition,
                         access,
                         **kwargs)
        self.roles = roles
        self.role_integration = role_integration

    def _as_rdf_xml(self, ns):
        elements = super()._as_rdf_xml(ns)
        component = ET.Element(NS('sbol', 'Component'),
                               attrib={NS('rdf', 'about'): self.rdf_identity})
        component.extend(elements)
        if self.roles is not None:
            component.append(ET.Element(NS('sbol', 'roles'),
                                        attrib={NS('rdf', 'resource'): self.roles}))
        if self.role_integration is not None:
            component.append(ET.Element(NS('sbol', 'role_integration'),
                                        attrib={NS('rdf', 'resource'): self.role_integration}))
        return component

    def __str__(self):
        return 'Component: {}'.format(self.identity)


class FunctionalComponent(ComponentInstance):
    """
    An instance of a ComponentDefinition being used as part of a ModuleDefinition
    """
    def __init__(self,
                 identity,
                 definition,
                 access,
                 direction,
                 **kwargs):
        super().__init__(identity,
                         definition,
                         access,
                         **kwargs)
        self.direction = direction
        self.access = access
        self.definition = definition

    def _as_rdf_xml(self, ns):
        elements = super()._as_rdf_xml(ns)
        component = ET.Element(NS('sbol', 'FunctionalComponent'),
                               attrib={NS('rdf', 'about'): self.rdf_identity})
        component.extend(elements)
        component.append(ET.Element(NS('sbol', 'direction'),
                                    attrib={NS('rdf', 'resource'): self.direction}))
        return component


class MapsTo(Identified):
    """
    Provide relationship data between ComponentDefinition and ModuleDefinition objects
    """
    def __init__(self,
                 identity,
                 local,
                 remote,
                 refinement,
                 **kwargs):
        super().__init__(identity, **kwargs)
        self.local = local
        self.remote = remote
        self.refinement = refinement

    @property
    def refinement(self):
        return self._refinement

    @refinement.setter
    def refinement(self, value):
        self._refinement = checktype(value, REFINEMENT_TYPES)

    def _as_rdf_xml(self, ns):
        elements = super()._as_rdf_xml(ns)
        map_to = ET.Element(NS('sbol', 'MapsTo'))
        map_to.append(ET.Element(NS('sbol', 'local'),
                                 attrib={NS('rdf', 'resource'): self.local.identity}))
        map_to.append(ET.Element(NS('sbol', 'remote'),
                                 attrib={NS('rdf', 'resource'): self.remote.identity}))
        map_to.append(ET.Element(NS('sbol', 'refinement'),
                                 attrib={NS('rdf', 'resource'): self.refinement}))
        return map_to
