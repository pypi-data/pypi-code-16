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

    def select(self, *selected):
        coll = ElementsCollection()
        for sel in selected:
            coll[sel] = self[sel]
        return coll


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


def boxplot(data, scl, loc, width):
    raw_prc = utils.prctiles(data)
    raw_prc = utils.clip(raw_prc, scl)
    p0, p25, p50, p75, p100 = [scl(p) for p in raw_prc]

    output = ElementsCollection()
    for points in ((p0, p25), (p75, p100)):
        output['whiskers'].append(
            svgwrite.shapes.Line(*utils.vpoints(loc, points)))

    output['box'].append(
        svgwrite.shapes.Rect(
            insert=(loc-0.5*width, min(p25, p75)),
            size=(width, abs(p75-p25))))

    output['median'].append(
        svgwrite.shapes.Line(
            *utils.hpoints(p50, [loc-.5*width, loc+.5*width])))

    return output


def legend(names2colors, loc, step, size):
    output = ElementsCollection()
    x, y = loc
    for name, color in names2colors.items():
        output['fields'].append(
            svgwrite.shapes.Rect(insert=(x, y),
                                 size=(size, size),
                                 fill=color))
        output['labels'].append(
            svgwrite.text.Text(name,
                               insert=(x+2*size, y),
                               alignment_baseline='middle'))
        y += step
    return output
