from lxml import etree as ET

from .identified import Identified
from .namespaces import NS


class QName(object):
    def __init__(self,
                 namespace,
                 local_name,
                 prefix=None):
        self.namespace = namespace
        self.local_name = local_name
        self.prefix = prefix


class Annotation(object):
    def __init__(self,
                 q_name,
                 annotation_value,
                 annotations=[]):
        self.q_name = q_name
        self.value = annotation_value

    def _as_rdf_xml(self, ns):
        annotation = ET.Element(NS(self.q_name.prefix, self.q_name.local_name))
        self.value._as_rdf_xml(ns, annotation)
        return annotation


class AnnotationValue(object):
    def __init__(self,
                 literal=None,
                 uri=None,
                 annotations=[]):
        self.literal = literal
        self.uri = uri
        self.annotations = annotations

    def _as_rdf_xml(self, ns, annotation):
        if self.uri is not None:
            annotation.set(NS('rdf', 'resource'), self.uri)
        elif len(self.annotations) > 0:
            for na in self.annotations:
                annotation.append(na._as_rdf_xml(ns))
        else:
            annotation.text = self.literal


class NestedAnnotation(object):
    def __init__(self,
                 nested_q_name,
                 nested_uri,
                 annotations=[]):
        self.nested_q_name = nested_q_name
        self.nested_uri = nested_uri
        self.annotations = annotations

    def _as_rdf_xml(self, ns):
        nested_annotation = ET.Element(NS(self.nested_q_name.prefix,
                                          self.nested_q_name.local_name),
                                       attrib={NS('rdf', 'about'): self.nested_uri})
        for an in self.annotations:
            nested_annotation.append(an._as_rdf_xml(ns))
        return nested_annotation
