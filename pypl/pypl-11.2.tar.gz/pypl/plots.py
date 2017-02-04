import itertools
import svgwrite
from collections import defaultdict


class ElementsCollection(defaultdict):

    def __init__(self):
        super(ElementsCollection, self).__init__(list)

    @property
    def elements(self):
        return list(itertools.chain(*[val for val in self.values()]))

    def attr(self, key, value):
        for e in self.elements:
            e.attribs[key] = value
        return self


def scatterplot(x, y, colors, cycle=True):
    output = ElementsCollection()
    n = max(len(x), len(y))

    if cycle:
        x = itertools.cycle(x)
        y = itertools.cycle(y)
        colors = itertools.cycle(colors)

    for _, x_, y_, col in zip(range(n), x, y, colors):
        output['points'].append(svgwrite.shapes.Circle((x_, y_), fill=col))

    return output
