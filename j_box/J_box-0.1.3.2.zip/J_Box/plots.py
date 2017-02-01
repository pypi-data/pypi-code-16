from collections import namedtuple
from pprint import pprint as pp
from math import floor

def Stem(Data,Multiplier):
    #Data must be a single array, the multiplier is for the LHS of the plot.
    Stem = namedtuple('Stem', 'data, leafdigits')
     
    data0 = Stem(Data,
                 Multiplier)
     
    def format_stem(stem):
        d = []
        interval = int(10**int(stem.leafdigits))
        for data in sorted(stem.data):
            data = int(floor(data))
            stm, lf = divmod(data,interval)
            d.append( (int(stm), int(lf)) )
        stems, leafs = list(zip(*d))
        stemwidth = max(len(str(x)) for x in stems)
        leafwidth = max(len(str(x)) for x in leafs)
        laststem, out = min(stems) - 1, []
        for s,l in d:
            while laststem < s:
                laststem += 1
                out.append('\n%*i |' % ( stemwidth, laststem))
            out.append(' %0*i' % (leafwidth, l))
        out.append('\n\nKey:\n Stem multiplier: %i\n X | Y  =>  %i*X+Y\n'
                   % (interval, interval))
        return ''.join(out)

    return format_stem(data0)