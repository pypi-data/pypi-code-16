import collections

class Vertex(collections.namedtuple('Vertex', ['id', 'type', 'properties'])):
    __slots__ = ()

    def __str__(self):
        properties = ''
        if self.properties is not None:
            properties = str(self.properties)
        return '(' + str(self.id) + ':' + str(self.type) + properties + ')'

    def __new__(cls, id, type, properties=None):
        return super(Vertex, cls).__new__(cls, id, type, properties)


class Edge:
    def __init__(self, from_vertex, rel, to_vertex, properties=None):
        self.from_vertex = from_vertex
        self.rel = rel
        self.to_vertex = to_vertex
        self.properties = properties

    def __str__(self):
        properties = ''
        if self.properties is not None:
            properties = str(self.properties)
        return (str(self.from_vertex) + '-[:' + str(self.rel) + properties +
                ']->' + str(self.to_vertex))


class Property(collections.namedtuple('Property', ['datatype', 'value'])):
    __slots__ = ()

    def __str__(self):
        return str(self.datatype) + ' = ' + str(self.value)
