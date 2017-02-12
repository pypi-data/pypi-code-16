###############################################################################
## 
## bitlist.py
##
##   Minimal Python library for working with little-endian list representation
##   of bit strings.
##
##   Web:     github.com/lapets/bitlist
##   Version: 0.0.2.0
##
##

###############################################################################
##

# A BitListError is a general-purpose catch-all for any usage error.
class BitListError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class bitlist():
    def __init__(self, arg = 0):
        self.bits = list(reversed([int(b) for b in (arg if type(arg) is str else "{0:b}".format(arg))]))

    def __len__(self):
        return len(self.bits)

    def __getitem__(self, i):
        return self.bits[i] if i < len(self) else 0

    def __setitem__(self, i, b):
        self.bits = [(self[j] if j != i else b) for j in range(0, max(i+1,len(self)))]

    def __int__(self):
        return int("".join(reversed([str(b) for b in self.bits])), 2)

    def __str__(self):
        return "bitlist('" + "".join(list(reversed([str(b) for b in self.bits]))) + "')"

    def __repr__(self):
        return str(self)

##eof