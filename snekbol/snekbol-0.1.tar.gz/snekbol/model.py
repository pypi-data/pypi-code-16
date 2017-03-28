from lxml import etree as ET

from .identified import Identified, TopLevel
from .types import *
from .namespaces import NS
from .components import FunctionalComponent


class Model(TopLevel):
    """
    Serve as a placeholder for an external computational model and provide additional meta-data
    """
    def __init__(self,
                 identity,
                 source,
                 language,
                 framework,
                 **kwargs):
        super().__init__(identity, **kwargs)
        self.source = source
        self.language = language
        self.framework = framework

    def _as_rdf_xml(self, ns):
        elements = super()._as_rdf_xml(ns)
        model = ET.Element(NS('sbol', 'Model'), attrib={NS('rdf', 'about'): self.rdf_identity})
        model.extend(elements)
        source = ET.SubElement(model, NS('sbol', 'source'), attrib={NS('rdf', 'resource'):
                                                                    self.source})
        language = ET.SubElement(model, NS('sbol', 'language'), attrib={NS('rdf', 'resource'):
                                                                        self.language})
        framework = ET.SubElement(model, NS('sbol', 'framework'), attrib={NS('rdf', 'resource'):
                                                                          self.framework})
        return model


class ModuleDefinition(TopLevel):
    """
    Represents a grouping of structural and functional entities in a biological design
    """
    def __init__(self,
                 identity,
                 roles=[],
                 modules=[],
                 functional_components=[],
                 interactions=[],
                 models=[],
                 **kwargs):
        super().__init__(identity, **kwargs)
        self.roles = roles
        self.modules = modules
        self.functional_components = functional_components
        self.interactions = interactions
        self.models = models

    def _as_rdf_xml(self, ns):
        elements = super()._as_rdf_xml(ns)
        module = ET.Element(NS('sbol', 'ModuleDefinition'), attrib={NS('rdf', 'about'):
                                                                    self.rdf_identity})
        module.extend(elements)
        for r in self.roles:
            role = ET.SubElement(module, NS('sbol', 'role'), attrib={NS('rdf', 'resource'): r})
        for m in self.models:
            model = ET.SubElement(module, NS('sbol', 'model'), attrib={NS('rdf', 'resource'):
                                                                       m._get_identity(ns)})
        for f in self.functional_components:
            func_comp = ET.SubElement(module, NS('sbol', 'functionalComponent'))
            func_comp.append(f._as_rdf_xml(ns))
        for m in self.modules:
            mod = ET.SubElement(module, NS('sbol', 'module'))
            mod.append(m._as_rdf_xml(ns))
        for i in self.interactions:
            interaction = ET.SubElement(module, NS('sbol', 'interaction'))
            interaction.append(i._as_rdf_xml(ns))
        return module


class Module(Identified):
    """
    Represents the usage or occurrence of a ModuleDefinition within a larger design
    """
    def __init__(self,
                 identity,
                 definition,
                 maps_to=[],
                 **kwargs):
        super().__init__(identity, **kwargs)
        self.definition = definition
        self.maps_to = maps_to

    def _as_rdf_xml(self, ns):
        elements = super()._as_rdf_xml(ns)
        module = ET.Element(NS('sbol', 'Module'), attrib={NS('rdf', 'about'): self.rdf_identity})
        module.extend(elements)
        definition = ET.SubElement(module, NS('sbol', 'definition'),
                                   attrib={NS('rdf', 'resource'):
                                           self.definition._get_identity(ns)})
        for m in self.maps_to:
            map_to = ET.SubElement(module, NS('sbol', 'mapsTo'))
            map_to.append(m._as_rdf_xml(ns))
        return module


class Interaction(Identified):
    """
    Describes how FunctionalComponents of a ModuleDefinition are intended to work together
    """
    def __init__(self,
                 identity,
                 types,
                 participations=[],
                 **kwargs):
        super().__init__(identity, **kwargs)
        self.types = types
        self.participations = participations

    def _as_rdf_xml(self, ns):
        elements = super()._as_rdf_xml(ns)
        interaction = ET.Element(NS('sbol', 'Interaction'),
                                 attrib={NS('rdf', 'about'): self.rdf_identity})
        for t in self.types:
            tp = ET.SubElement(interaction, NS('sbol', 'type'), attrib={NS('rdf', 'resource'): t})
        for p in self.participations:
            pt = ET.SubElement(interaction, NS('sbol', 'participation'))
            pt.append(p._as_rdf_xml(ns))
        return interaction


class Participation(Identified):
    """
    Represents how a particular FunctionalComponent behaves in its parent Interaction
    """
    def __init__(self,
                 identity,
                 roles,
                 participant,
                 **kwargs):
        super().__init__(identity, **kwargs)
        self.roles = roles
        self.participant = participant

    @property
    def roles(self):
        return self._roles

    @roles.setter
    def roles(self, value):
        if not isinstance(value, list):
            raise Exception('Must provide a list of roles')
        self._roles = checktype(value, ROLES, is_list=True)

    @property
    def participant(self):
        return self._participant

    @participant.setter
    def participant(self, value):
        if not isinstance(value, FunctionalComponent):
            raise Exception('Must provide a FunctionalComponent instance')
        self._participant = value

    def _as_rdf_xml(self, ns):
        elements = super()._as_rdf_xml(ns)
        participation = ET.Element(NS('sbol', 'Participation'),
                                 attrib={NS('rdf', 'about'): self.rdf_identity})
        participation.extend(elements)
        for r in self.roles:
            rl = ET.SubElement(participation, NS('sbol', 'role'),
                               attrib={NS('rdf', 'resource'): r})
        participant = ET.SubElement(participation, NS('sbol', 'participant'),
                                    attrib={NS('rdf', 'resource'):
                                            self.participant._get_identity(ns)})
        return participation
