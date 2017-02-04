import itertools
import svgwrite
from collections import defaultdict

from . import utils


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


def boxplot(data, loc, width):
    p0, p25, p50, p75, p100 = utils.prctiles(data)

    output = ElementsCollection()
    for points in ((p0, p25), (p75, p100)):
        output['whiskers'].append(
            svgwrite.shapes.Line(*utils.vpoints(loc, points)))

    output['box'].append(
        svgwrite.shapes.Rect(
            insert=(loc-0.5*width, 25),
            size=(width, p75-p25)))

    output['median'].append(
        svgwrite.shapes.Line(
            *utils.hpoints(p50, [loc-.5*width, loc+.5*width])))

    return output
