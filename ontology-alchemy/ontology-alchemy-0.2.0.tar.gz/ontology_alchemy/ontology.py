from rdflib import Graph
from rdflib.util import guess_format
from six import string_types

from ontology_alchemy.builder import OntologyBuilder


class Ontology(object):

    def __init__(self, namespace, graph, base_uri=None, **kwargs):
        """
        Initialize an ontology given a namespace.
        A namespace encapsulates the full hierarchy of types and inheritance relations
        described by the ontology.

        """
        self.__dict__.update(namespace)
        self.__graph__ = graph
        self.__terms__ = list(namespace.keys())
        self.__uri__ = base_uri

    @classmethod
    def load(cls, file_or_filename, format=None):
        """
        Materialize ontology into Python class hierarchy from a given
        file-like object or a filename.

        :param file_or_filename - file-like object or local filesystem path to file
            containing ontology definition in one of the supported formats.
        :param format - the format ontology is serialized in.
            For list of currently supported formats (based on RDFlib which is used under the hood)
            see: http://rdflib.readthedocs.io/en/565/plugin_parsers.html
        :returns instance of the `Ontology` object which encompasses the ontology namespace
            for all created objects and types.

        """
        graph = Graph()
        if isinstance(file_or_filename, string_types):
            # Load from given filename
            if not format:
                format = guess_format(file_or_filename)
            graph.parse(file_or_filename, format=format)
        else:
            # Load from file-like buffer
            if not format:
                raise RuntimeError("Must supply format argument when not loading from a filename")
            graph.parse(file_or_filename, format=format)

        builder = OntologyBuilder(graph)
        namespace = builder.build_namespace()

        return cls(namespace, graph=graph, base_uri=builder.base_uri)

    def rdf_statements(self):
        """
        Return a generator expression iterating over all RDF statements encompassed in the ontology graph.

        """
        return self.__graph__.triples((None, None, None))
