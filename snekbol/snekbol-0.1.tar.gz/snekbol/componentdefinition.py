from lxml import etree as ET

from rdflib import Namespace, URIRef, Literal, RDF, RDFS, BNode
import validators

from .identified import TopLevel
from .sequence import Sequence
from .types import *
from .namespaces import SBOL, NS


class ComponentDefinition(TopLevel):
    """
    The ComponentDefinition class represents the structural entities of a biological design
    """

    def __init__(self,
                 identity,
                 types=[],
                 topology_type=None,
                 strand_type=None,
                 roles=[],
                 sequences=[],
                 components=[],
                 sequence_annotations=[],
                 sequence_constraints=[],
                 **kwargs):
        super().__init__(identity, **kwargs)

        self._types = []
        self._roles = []
        self._sequences = []
        self._components = []
        self._sequence_annotations = []
        self._sequence_constraints = []

        self.roles = roles
        self.sequences = sequences
        self.components = components
        self.sequence_annotations = sequence_annotations
        self.sequence_constraints = sequence_constraints

        if len(types) == 0:
            self.types = ['DNA']
        else:
            self.types = types

        if topology_type is not None:
            self.types.append(topology_type)
        elif types is None and 'DNA' not in types:
            self.types.append('linear')

        if 'DNA' in types or 'RNA' in types:
            if strand_type is not None:
                self.types.append(strand_type)
            elif strand_type is None and 'DNA' in types:
                self.types.append('double-stranded')
            elif strand_type is None and 'RNA' in types:
                self.types.append('single-stranded')

    def __str__(self):
        return 'ComponentDefinition: {}'.format(self.identity)

    @property
    def types(self):
        return self._types

    @types.setter
    def types(self, value):
        if not isinstance(value, list):
            raise Exception('Must provide a list of types')
        types = checktype(value, VALID_COMPONENT_TYPES, is_list=True)
        self._types = types

    @property
    def roles(self):
        return self._roles

    @roles.setter
    def roles(self, value):
        if not isinstance(value, list):
            raise Exception('Must provide a list of roles')
        roles = checktype(value, ROLES, is_list=True)
        self._roles = roles

    @property
    def sequences(self):
        return self._sequences

    @sequences.setter
    def sequences(self, value):
        if not isinstance(value, list):
            raise Exception('Must provide a list of sequences')
        self._sequences = value

    def participate(self, participant):
        """
        Add component as a participant in a biochemical reaction
        """
        pass

    def _as_rdf_xml(self, ns):
        elements = super()._as_rdf_xml(ns)
        component_definition = ET.Element(NS('sbol', 'ComponentDefinition'),
                                          attrib={NS('rdf', 'about'): self.rdf_identity})
        component_definition.extend(elements)

        for r in self.roles:
            component_definition.append(ET.Element(NS('sbol', 'role'),
                                        attrib={NS('rdf', 'resource'): r}))
        for t in self.types:
            component_definition.append(ET.Element(NS('sbol', 'type'),
                                        attrib={NS('rdf', 'resource'): t}))

        for c in sorted(self.components, key=lambda x: x.identity):
            component_container = ET.Element(NS('sbol', 'component'))
            component_container.append(c._as_rdf_xml(ns))
            component_definition.append(component_container)
        for s in sorted(self.sequence_annotations, key=lambda x: x.identity):
            component_definition.append(s._as_rdf_xml(ns))
        for s in sorted(self.sequence_constraints, key=lambda x: x.identity):
            component_definition.append(s._as_rdf_xml(ns))
        for s in sorted(self.sequences, key=lambda x: x.identity):
            component_definition.append(ET.Element(NS('sbol', 'sequence'),
                                                   attrib={NS('rdf', 'resource'):
                                                           s._get_identity(ns)}))
        return component_definition
