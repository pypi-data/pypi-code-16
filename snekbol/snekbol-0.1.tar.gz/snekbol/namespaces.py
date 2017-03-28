from rdflib import Namespace

SBOL = Namespace('http://sbols.org/v2#')
PROV = Namespace('http://www.w3.org/ns/prov#')

XML_NS = {
    'sbol': 'http://sbols.org/v2#',
    'prov': 'http://www.w3.org/ns/prov#',
    'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
    'dcterms': 'http://purl.org/dc/terms/',
}

# Valid elements that can be used in an SBOL file
VALID_ENTITIES = [
    'rdf:type',
    'sbol:persistentIdentity',
    'sbol:displayId',
    'sbol:version',
    'prov:wasDerivedFrom',
    'dcterms:title',
    'dcterms:description',
    'sbol:Sequence',
    'sbol:sequence',
    'sbol:elements',
    'sbol:encoding',
    'sbol:ComponentDefinition',
    'sbol:type',
    'sbol:role',
    'sbol:Component',
    'sbol:access',
    'sbol:definition',
    'sbol:mapsTo',
    'sbol:roleIntegration',
    'sbol:MapsTo',
    'sbol:refinement',
    'sbol:remote',
    'sbol:local',
    'sbol:SequenceAnnotation',
    'sbol:sequenceAnnotation',
    'sbol:location',
    'sbol:Range',
    'sbol:Cut',
    'sbol:GenericLocation',
    'sbol:start',
    'sbol:end',
    'sbol:component',
    'sbol:at',
    'sbol:orientation',
    'sbol:restriction',
    'sbol:subject',
    'sbol:object',
    'sbol:SequenceConstraint',
    'sbol:Model',
    'sbol:source',
    'sbol:language',
    'sbol:framework',
    'sbol:ModuleDefinition',
    'sbol:model',
    'sbol:FunctionalComponent',
    'sbol:functionalComponent',
    'sbol:module',
    'sbol:Module',
    'sbol:interaction',
    'sbol:Interaction',
    'sbol:definition',
    'sbol:access',
    'sbol:direction',
    'sbol:participation',
    'sbol:Participation',
    'sbol:participant',
    'sbol:Collection',
    'sbol:member',
]

def NS(namespace, tag):
    """
    Generate a namespaced tag for use in creation of an XML file
    """
    return '{' + XML_NS[namespace] + '}' + tag
