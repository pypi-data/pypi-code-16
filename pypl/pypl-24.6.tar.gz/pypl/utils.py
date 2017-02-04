
def lims2len(lims):
    return lims[1] - lims[0]


def prctiles(data, p=(0, .25, .5, .75, 1)):
    n = len(data)
    indices = (int((n-1)*p_) for p_ in sorted(p))
    return [data[i] for i in indices]


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
