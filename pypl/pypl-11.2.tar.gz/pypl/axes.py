import functools
import operator
import svgwrite

from .plots import ElementsCollection


def vaxis(scl, nticks=5, x=0, **specs):
    specs = set_general_defaults(specs, scl)

    return makeaxis('vertical', scl, nticks, x, specs)


def haxis(scl, nticks=5, y=0, **specs):
    specs = set_general_defaults(specs, scl)

    return makeaxis('horizontal', scl, nticks, y, specs)


def set_general_defaults(general_spec, scl):
    d = {
        'tick_size': scl(0) - scl(.01*scl.data_len),
        'ticklabelformat': '{:.2f}'
    }
    d.update(general_spec)
    return d


def get_ticks(scl, nticks):
    raw_ticks = [scl.data_0 + scl.data_len*loc/(nticks-1)
                 for loc in range(nticks)]
    return [scl(loc) for loc in raw_ticks], raw_ticks


def makeaxis(direction, scl, nticks, loc, specs):
    ts = specs['tick_size']
    ticklabelformat = specs['ticklabelformat']
    ticks, raw_ticks = get_ticks(scl, nticks)

    output = ElementsCollection()

    if direction == 'vertical':
        axpoint = partialpoint(x=loc)
        ticpoints = functools.partial(hpoints, locations=[loc, loc+ts])
        tick_labl_loc = partialpoint(x=loc+2*ts)
        label_loc = partialpoint(x=loc+5*ts)
    else:
        axpoint = partialpoint(y=loc)
        ticpoints = functools.partial(vpoints, locations=[loc, loc+ts])
        tick_labl_loc = partialpoint(y=loc+2*ts)
        label_loc = partialpoint(y=loc+5*ts)

    output['line'].append(svgwrite.shapes.Line(axpoint(min(ticks)),
                                               axpoint(max(ticks))))
    if 'label' in specs:
        mticks = functools.reduce(operator.add, ticks)/len(ticks)
        output['label'].append(svgwrite.text.Text(specs['label'],
                                                  label_loc(mticks)))

    for tick, raw_tick in zip(ticks, raw_ticks):
        output['ticks'].append(svgwrite.shapes.Line(*ticpoints(tick)))
        output['ticklabels'].append(
            svgwrite.text.Text(ticklabelformat.format(raw_tick),
                               insert=tick_labl_loc(tick)))

    return output


def hpoints(vpos, locations):
    return [(loc, vpos) for loc in locations]


def vpoints(hpos, locations):
    return [(hpos, loc) for loc in locations]


def partialpoint(x=None, y=None):

    if x is None and y is not None:

        def mkpoint(other):
            return (other, y)

    elif x is not None and y is None:

        def mkpoint(other):
            return (x, other)

    else:

        mkpoint = partialpoint

    return mkpoint
