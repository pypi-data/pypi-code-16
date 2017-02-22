"""Constant definitions used by the framework."""
from rdflib import Literal
from rdflib.namespace import RDF, OWL
from six import string_types


# Default tag to use as a language tag for literal assigments of text strings
DEFAULT_LANGUAGE_TAG = "en"

# These are all the Python types which are considered valid to be used directly
# as assigments on Literal properties (of type rdfs:Literal)
LITERAL_PRIMITIVE_TYPES = string_types + (
    Literal,
    int,
    float,
    bool,
)

COMMON_PROPERTY_URIS = (
    OWL.AnnotationProperty,
    OWL.AsymmetricProperty,
    OWL.DatatypeProperty,
    OWL.DeprecatedProperty,
    OWL.FunctionalProperty,
    OWL.InverseFunctionalProperty,
    OWL.IrreflexiveProperty,
    OWL.ObjectProperty,
    OWL.OntologyProperty,
    OWL.ReflexiveProperty,
    OWL.SymmetricProperty,
    OWL.TransitiveProperty,
    RDF.Property,
)
