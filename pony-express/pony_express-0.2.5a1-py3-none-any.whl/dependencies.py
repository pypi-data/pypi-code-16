class Requirement(object):
    def __init__(self, json_decoded):
        self.invalid = False
        try:
            del json_decoded['DEPENDENCIES']
        except KeyError:
            pass

        self.__dict__ = json_decoded

    def __eq__(self, other):
        return self.__hash__() == other.__hash__()

    def __lt__(self, other):
        return str(self) < str(other)

    def __hash__(self):
        return hash(str(self))

    def __repr__(self):
        return str(self.NAME)

    def __str__(self):
        text_val = "{ "
        meta_request = self.meta_request()
        keylist = list(meta_request.keys())
        keylist.sort()

        text_val += str(keylist[0]) + ":" + str(meta_request[keylist[0]])

        for k in keylist[1:]:
            text_val += ", " + str(k) + ":" + str(meta_request[k])

        text_val += " }"

        return text_val


    def perfect_match(self, other):
        for x in [prop for prop in self.__dict__ if prop in other.__dict__]:
            if self.__dict__[x] != other.__dict__[x]:
                print ("unmatched " + x)
                return False
        return True

    def alternative(self, other):
        return self.NAME == other.NAME

    def meta_request(self):
        stripped = dict (self.__dict__)
        try:
            del stripped['TEST']
        except KeyError:
            pass

        try:
            del stripped['_id']
        except KeyError:
            pass

        try:
            del stripped['parent']
        except KeyError:
            pass

        try:
            del stripped['package']
        except KeyError:
            pass

        return stripped


def make_direct( meta_request, parent=None ):
    requirements = [Requirement(r) for r  in meta_request]
    if parent:
        for r in requirements:
            r.parent = parent

    return requirements

def dot_graph(requirements):
    graph = "\ndigraph {\n"
    for r in [r for r in requirements if not hasattr(r, "parent")]:
        graph += "  \"" + repr(r) + "\"\n"

    graph += "\n"

    for r in [r for r in requirements if hasattr(r, "parent")]:
        graph += "  \"" + repr(r) + "\" -> \"" + repr(r.parent) + "\"\n"

    graph += "}"
    return graph
