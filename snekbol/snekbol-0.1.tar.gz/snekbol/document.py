from urllib.parse import urljoin
from pprint import pprint
from lxml import etree as ET

from rdflib import Graph, Namespace, URIRef, Literal, RDF
from rdflib.namespace import DCTERMS, split_uri

import validators

from .identified import GenericTopLevel
from .namespaces import SBOL, PROV, XML_NS, NS, VALID_ENTITIES
from .componentdefinition import ComponentDefinition
from .components import Component, FunctionalComponent, MapsTo
from .sequence import Sequence, SequenceAnnotation, SequenceConstraint
from .location import Range, Cut, GenericLocation
from .model import Model, Module, ModuleDefinition, Interaction, Participation
from .annotation import QName, Annotation, AnnotationValue, NestedAnnotation
from .collection import Collection

class Document(object):
    """
    Provides a base for creating SBOL documents
    """
    def __init__(self,
                 namespace,
                 validate=True):

        # Don't access directly: use function getter/setters
        self._components = {}
        self._sequences = {}
        self._namespaces = {}
        self._models = {}
        self._modules = {}
        self._collections = {}
        self._annotations = {}

        # Used for looking up functional components when reading
        # in data from a file
        self._functional_component_store = {}
        self._collection_store = {}

        if validators.url(namespace):
            self.document_namespace = namespace
        else:
            raise Exception('Invalid namespace URI')
        self.validate = validate

        # Create a document namesspace for use in RDF serialization
        self.ns = Namespace(self.document_namespace)

    def __str__(self):
        return 'SBOL Document {{{}}}'.format(self.document_namespace)

    def add_namespace(self, namespace, prefix):
        """
        Add a namespace to the document
        """
        pass

    def get_namespaces(self):
        """
        Get all namespaces in the document (inc default)
        """
        pass

    def _to_uri_from_namespace(self, value):
        """
        Take a value and make a URL using the document namespace
        """
        return urljoin(self.document_namespace, value)

    def _append_to_uri(self, uri, value):
        """
        Take an existing URI and append more data to it
        """
        return urljoin(uri, value)

    def add_component_definition(self, definition):
        """
        Add a ComponentDefinition to the document
        """
        # definition.identity = self._to_uri_from_namespace(definition.identity)
        if definition.identity not in self._components.keys():
            self._components[definition.identity] = definition
        else:
            raise ValueError("{} has already been defined".format(definition.identity))

    def remove_component_definition(self, identity):
        """
        Remove a ComponentDefinition from the document
        """
        try:
            self._components.pop(identity)
        except KeyError:
            pass

    def get_component_definition(self, uri):
        """
        Get a ComponentDefintion from the document
        """
        try:
            definition = self._components[uri]
        except KeyError:
            return None
        return definition

    def list_components(self):
        """
        List of all ComponentDefinitions in the document
        """
        return self._components.values()

    def assemble_component(self, into_component, using_components):
        """
        Assemble a list of already defined components into a structual hirearchy
        """
        if not isinstance(using_components, list) or len(using_components) == 0:
            raise Exception('Must supply list of ComponentDefinitions')

        components = []
        sequence_annotations = []
        seq_elements = ''

        for k, c in enumerate(using_components):
            try:
                self._components[c.identity]
            except KeyError:
                raise Exception('Must already have defined ComponentDefinition in document')
            else:
                identity = into_component.identity + '/' + c.identity

                # All components are initially public, this can be changed later
                component = Component(identity,
                                      c,
                                      'public',
                                      display_id=c.identity)
                components.append(component)

                # If there is a sequence on the ComponentDefinition use the first element
                if len(c.sequences) > 0:
                    # Add the sequence to the document
                    self._add_sequence(c.sequences[0])
                    # Get start/end points of sequence
                    start = len(seq_elements) + 1 # The sequence is usually 1 indexed
                    end = start + len(c.sequences[0].elements)
                    # Add to the component sequence element
                    seq_elements += c.sequences[0].elements
                    # Create a Range object to hold seq range
                    range_identity = identity + '_sequence_annotation/range'
                    seq_range = Range(range_identity, start, end, display_id='range')
                    # Create a SequenceAnnotation object to hold the range
                    annot_identity = identity + '_sequence_annotation'
                    seq_annot = SequenceAnnotation(annot_identity,
                                                   component=component,
                                                   locations=[seq_range],
                                                   display_id=c.identity + '_sequence_annotation')
                    sequence_annotations.append(seq_annot)

        if seq_elements != '':
            seq_encoding = using_components[0].sequences[0].encoding
            seq_identity = '{}_sequence'.format(into_component.identity)
            seq = Sequence(seq_identity, seq_elements, encoding=seq_encoding)
            self._add_sequence(seq)
            into_component.sequences.append(seq)

        into_component.components = components
        into_component.sequence_annotations = sequence_annotations

    def _add_sequence(self, sequence):
        """
        Add a Sequence to the document
        """
        if sequence.identity not in self._sequences.keys():
            self._sequences[sequence.identity] = sequence
        else:
            raise ValueError("{} has already been defined".format(sequence.identity))

    def add_model(self, model):
        """
        Add a model to the document
        """
        if model.identity not in self._models.keys():
            self._models[model.identity] = model
        else:
            raise ValueError("{} has already been defined".format(model.identity))

    def remove_model(self, identity):
        """
        Remove a Model from the document
        """
        try:
            self._models.pop(identity)
        except KeyError:
            pass

    def get_model(self, uri):
        """
        Get a Model for the document
        """
        pass

    def add_module_definition(self, module_definition):
        """
        Add a ModuleDefinition to the document
        """
        if module_definition.identity not in self._module_definitions.keys():
            self._module_definitions[module_definition.identity] = module_definition
        else:
            raise ValueError("{} has already been defined".format(module_definition.identity))

    def remove_module_definition(self, identity):
        """
        Remove a ModuleDefinition from the document
        """
        try:
            self._module_definitions.pop(identity)
        except KeyError:
            pass

    def get_module_definition(self, uri):
        """
        Get a ModuleDefinition from the document
        """
        pass

    def find(self, uri):
        """
        Recursivly search document for URI
        """
        pass

    def _get_elements(self, graph, element_type):
        return graph.triples((None, RDF.type, element_type))

    def _get_triplet_value(self, graph, identity, rdf_type):
        """
        Get a value from an RDF triple
        """
        value = graph.value(subject=identity, predicate=rdf_type)
        return value.toPython() if value is not None else value

    def _get_triplet_value_list(self, graph, identity, rdf_type):
        """
        Get a list of values from RDF triples when more than one may be present
        """
        values = []
        for elem in graph.objects(identity, rdf_type):
            values.append(elem.toPython())
        return values

    def _get_rdf_identified(self, graph, identity):
        c = {}
        c['identity'] = identity.toPython() if type(identity) is not str else identity
        c['display_id'] = self._get_triplet_value(graph, identity, SBOL.displayId)
        c['was_derived_from'] = self._get_triplet_value(graph, identity, PROV.wasDerivedFrom)
        c['version'] = self._get_triplet_value(graph, identity, SBOL.version)
        c['description'] = self._get_triplet_value(graph, identity, DCTERMS.description)
        c['name'] = self._get_triplet_value(graph, identity, DCTERMS.title)

        flipped_namespaces = {v: k for k, v in self._namespaces.items()}
        # Get annotations (non top level)
        c['annotations'] = []
        for triple in graph.triples((identity, None, None)):
            namespace, obj = split_uri(triple[1])
            prefix = flipped_namespaces[namespace]
            as_string = '{}:{}'.format(prefix, obj)
            if as_string not in VALID_ENTITIES:
                q_name = QName(namespace=namespace, local_name=obj, prefix=prefix)
                if isinstance(triple[2], URIRef):
                    value = AnnotationValue(uri=triple[2].toPython())
                elif isinstance(triple[2], Literal):
                    value = AnnotationValue(literal=triple[2].toPython())
                else:
                    value = None
                c['annotations'].append(Annotation(q_name=q_name, annotation_value=value))
        return c

    def _read_sequences(self, graph):
        """
        Read graph and add sequences to document
        """
        for e in self._get_elements(graph, SBOL.Sequence):
            identity = e[0]
            c = self._get_rdf_identified(graph, identity)
            c['elements'] = self._get_triplet_value(graph, identity, SBOL.elements)
            c['encoding'] = self._get_triplet_value(graph, identity, SBOL.encoding)
            seq = Sequence(**c)
            self._sequences[identity.toPython()] = seq
            self._collection_store[identity.toPython()] = seq

    def _read_component_definitions(self, graph):
        """
        Read graph and add component defintions to document
        """
        for e in self._get_elements(graph, SBOL.ComponentDefinition):
            identity = e[0]
            # Store component values in dict
            c = self._get_rdf_identified(graph, identity)
            c['roles'] = self._get_triplet_value_list(graph, identity, SBOL.role)
            c['types'] = self._get_triplet_value_list(graph, identity, SBOL.type)
            obj = ComponentDefinition(**c)
            self._components[identity.toPython()] = obj
            self._collection_store[identity.toPython()] = obj

    def _extend_component_definitions(self, graph):
        """
        Read graph and update component definitions with related elements
        """
        for def_uri, comp_def in self._components.items():
            # Store created components indexed for later lookup
            component_index = {}
            identity = URIRef(def_uri)

            # Get components
            for comp in graph.triples((identity, SBOL.component, None)):
                comp_identity = comp[2]
                ci = self._get_rdf_identified(graph, comp_identity)
                ci['maps_to'] = self._get_triplet_value(graph, comp_identity, SBOL.mapTo)
                ci['access'] = self._get_triplet_value(graph, comp_identity, SBOL.access)

                component_comp_def = self._get_triplet_value(graph, comp_identity, SBOL.definition)
                ci['definition'] = self._components[component_comp_def]

                c = Component(**ci)
                component_index[ci['identity']] = c
            self._components[def_uri].components = list(component_index.values())

            # Get sequence annotations
            if (identity, SBOL.sequenceAnnotation, None) in graph:
                find_annotation_using = (identity, SBOL.sequenceAnnotation, None)
            else:
                find_annotation_using = (identity, SBOL.SequenceAnnotation, None)
            sequence_annotations = []
            for seq_annot in graph.triples(find_annotation_using):
                seq_identity = seq_annot[2]
                sa = self._get_rdf_identified(graph, seq_identity)
                component_to_use = self._get_triplet_value(graph, seq_identity, SBOL.component)
                sa['component'] = component_index[component_to_use]
                sa['roles'] = self._get_triplet_value_list(graph, seq_identity, SBOL.role)
                locations = []
                for loc in graph.triples((seq_identity, SBOL.location, None)):
                    loc_identity = loc[2]
                    location = self._get_rdf_identified(graph, loc_identity)
                    location['orientation'] = self._get_triplet_value(graph, loc_identity,
                                                                      SBOL.orientation)
                    location_type = URIRef(self._get_triplet_value(graph, loc_identity, RDF.type))
                    if location_type == SBOL.Range:
                        location['start'] = self._get_triplet_value(graph, loc_identity, SBOL.start)
                        location['end'] = self._get_triplet_value(graph, loc_identity, SBOL.end)
                        locations.append(Range(**location))
                    elif location_type == SBOL.Cut:
                        location['at'] = self._get_triplet_value(graph, loc_identity, SBOL.at)
                        locations.append(Cut(**location))
                    else:
                        locations.append(GenericLocation(**location))
                sa_obj = SequenceAnnotation(locations=locations, **sa)
                sequence_annotations.append(sa_obj)
            self._components[def_uri].sequence_annotations = sequence_annotations

            # Get sequence constraints
            if (identity, SBOL.sequenceConstraint, None) in graph:
                find_constraint_using = (identity, SBOL.sequenceConstraint, None)
            else:
                find_constraint_using = (identity, SBOL.SequenceConstraint, None)
            sequence_constraints = []
            for seq_constraint in graph.triples(find_constraint_using):
                seq_identity = seq_constraint[2]
                sc = self._get_rdf_identified(graph, seq_identity)
                sc['restriction'] = self._get_triplet_value(graph, seq_identity, SBOL.restriction)
                subject_id = self._get_triplet_value(graph, seq_identity, SBOL.subject)
                sc['subject'] = component_index[subject_id]
                object_id = self._get_triplet_value(graph, seq_identity, SBOL.object)
                # Object is a reserved word so call it obj to prevent clashes
                sc['obj'] = component_index[object_id]
                sc_obj = SequenceConstraint(**sc)
                sequence_constraints.append(sc_obj)
            self._components[def_uri].sequence_constraints = sequence_constraints

    def _read_models(self, graph):
        """
        Read graph and add models to document
        """
        for e in self._get_elements(graph, SBOL.Model):
            identity = e[0]
            m = self._get_rdf_identified(graph, identity)
            m['source'] = self._get_triplet_value(graph, identity, SBOL.source)
            m['language'] = self._get_triplet_value(graph, identity, SBOL.language)
            m['framework'] = self._get_triplet_value(graph, identity, SBOL.framework)
            obj = Model(**m)
            self._models[identity.toPython()] = obj
            self._collection_store[identity.toPython()] = obj

    def _read_module_definitions(self, graph):
        """
        Read graph and add module defintions to document
        """
        for e in self._get_elements(graph, SBOL.ModuleDefinition):
            identity = e[0]
            m = self._get_rdf_identified(graph, identity)
            m['roles'] = self._get_triplet_value_list(graph, identity, SBOL.role)
            functional_components = {}
            for func_comp in graph.triples((identity, SBOL.functionalComponent, None)):
                func_identity = func_comp[2]
                fc = self._get_rdf_identified(graph, func_identity)
                definition = self._get_triplet_value(graph, func_identity, SBOL.definition)
                fc['definition'] = self._components[definition]
                fc['access'] = self._get_triplet_value(graph, func_identity, SBOL.access)
                fc['direction'] = self._get_triplet_value(graph, func_identity, SBOL.direction)
                functional_components[func_identity.toPython()] = FunctionalComponent(**fc)
                self._functional_component_store[func_identity.toPython()] = \
                        functional_components[func_identity.toPython()]
            interactions = []
            for inter in graph.triples((identity, SBOL.interaction, None)):
                inter_identity = inter[2]
                it = self._get_rdf_identified(graph, inter_identity)
                it['types'] = self._get_triplet_value_list(graph, inter_identity, SBOL.types)
                participations = []
                for p in graph.triples((inter_identity, SBOL.participation, None)):
                    pc = self._get_rdf_identified(graph, p[2])
                    roles = self._get_triplet_value_list(graph, p[2], SBOL.role)
                    # Need to use one of the functional component created above
                    participant_id = self._get_triplet_value(graph, p[2], SBOL.participant)
                    participant = functional_components[participant_id]
                    participations.append(Participation(roles=roles, participant=participant, **pc))
                interactions.append(Interaction(participations=participations, **it))
            obj = ModuleDefinition(functional_components=functional_components.values(),
                                   interactions=interactions,
                                   **m)
            self._modules[identity.toPython()] = obj
            self._collection_store[identity.toPython()] = obj

    def _extend_module_definitions(self, graph):
        """
        Using collected module definitions extend linkages
        """
        for mod_id in self._modules:
            mod_identity = self._get_triplet_value(graph, URIRef(mod_id), SBOL.module)
            modules = []
            for mod in graph.triples((mod_identity, SBOL.module, None)):
                md = self._get_rdf_identified(graph, mod[2])
                definition_id = self._get_triplet_value(graph, mod[2], SBOL.definition)
                md['definition'] = self._modules[definition_id]
                maps_to = []
                for m in graph.triples((mod[2], SBOL.mapsTo, None)):
                    mt = self._get_rdf_identified(graph, m[2])
                    mt['refinement'] = self._get_triplet_value(graph, m[2], SBOL.refinement)
                    local_id = self._get_triplet_value(graph, m[2], SBOL.local)
                    remote_id = self._get_triplet_value(graph, m[2], SBOL.remote)
                    mt['local'] = self._functional_component_store[local_id]
                    mt['remote'] = self._functional_component_store[remote_id]
                    maps_to.append(MapsTo(**mt))
                modules.append(Module(maps_to=maps_to, **md))
            self._modules[mod_id].modules = modules

    def _read_annotations(self, graph):
        """
        Find any non-defined elements at TopLevel and create annotations
        """
        flipped_namespaces = {v: k for k, v in self._namespaces.items()}
        for triple in graph.triples((None, RDF.type, None)):
            namespace, obj = split_uri(triple[2])
            prefix = flipped_namespaces[namespace]
            as_string = '{}:{}'.format(prefix, obj)
            if as_string not in VALID_ENTITIES:
                identity = triple[0]
                gt = self._get_rdf_identified(graph, identity)
                q_name = QName(namespace=namespace, local_name=obj, prefix=prefix)
                gt['rdf_type'] = q_name
                gt_obj = GenericTopLevel(**gt)
                self._annotations[identity.toPython()] = gt_obj
                self._collection_store[identity.toPython()] = gt_obj

    def _read_collections(self, graph):
        """
        Read graph and add collections to document
        """
        for e in self._get_elements(graph, SBOL.Collection):
            identity = e[0]
            c = self._get_rdf_identified(graph, identity)
            members = []
            # Need to handle other non-standard TopLevel objects first
            for m in graph.triples((identity, SBOL.member, None)):
                members.append(self._collection_store[m[2].toPython()])
            obj = Collection(members=members, **c)
            self._collections[identity.toPython()] = obj

    def read(self, f):
        """
        Read in an SBOL file, replacing current document contents
        """
        g = Graph()
        g.parse(f, format='xml')

        for n in g.namespaces():
            ns = n[1].toPython()
            if not ns.endswith(('#', '/', ':')):
                ns = ns + '/'
            self._namespaces[n[0]] = ns
            # Extend the existing namespaces available
            XML_NS[n[0]] = ns

        self._read_sequences(g)
        self._read_component_definitions(g)
        self._extend_component_definitions(g)
        self._read_models(g)
        self._read_module_definitions(g)
        self._extend_module_definitions(g)
        self._read_annotations(g)
        # Last as this needs all other top level objects created
        self._read_collections(g)

    def append(self, f):
        """
        Read an SBOL file and append contents to current document
        """
        pass

    def _add_to_root(self, root_node, elements):
        for item in elements:
            elem = item._as_rdf_xml(self.ns)
            root_node.append(elem)

    def write(self, f):
        """
        Write an SBOL file from current document contents
        """
        rdf = ET.Element(NS('rdf', 'RDF'), nsmap=XML_NS)

        # TODO: TopLevel Annotations
        sequence_values = sorted(self._sequences.values(), key=lambda x: x.identity)
        self._add_to_root(rdf, sequence_values)
        component_values = sorted(self._components.values(), key=lambda x: x.identity)
        self._add_to_root(rdf, component_values)
        model_values = sorted(self._models.values(), key=lambda x: x.identity)
        self._add_to_root(rdf, model_values)
        module_values = sorted(self._modules.values(), key=lambda x: x.identity)
        self._add_to_root(rdf, module_values)
        collection_values = sorted(self._collections.values(), key=lambda x: x.identity)
        self._add_to_root(rdf, collection_values)
        annotation_values = sorted(self._annotations.values(), key=lambda x: x.identity)
        self._add_to_root(rdf, annotation_values)

        f.write(ET.tostring(rdf,
                            pretty_print=True,
                            xml_declaration=True,
                            encoding='utf-8'))
