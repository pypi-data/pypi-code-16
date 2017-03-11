"""
Module provides the realization of Z/p where p is prime.
To see how it can be used - look at the package module "example"
"""

class Zp:
    def __init__(self, p, check=False):
        check and Zp._check_prime(p)
        self.p = p
        
    def __call__(self, val):
        return Zp.Element(val, self.p)
        
    def __getitem__(self, val):
        return Zp.Element(val, self.p)
        
    def __len__(self):
        return self.p
    
    def __iter__(self):
        elements = (self(i) for i in range(self.p))
        return elements
    
    def __reversed__(self):
        elements = (self(i) for i in range(self.p)[::-1])
        return elements
        
    def __str__(self):
        return 'Z/%d' % self.p
    
    def __repr__(self):
        return 'Z/%d' % self.p
    
    def get_elements(self):
        elements = [self(i) for i in range(self.p)]
        return tuple(elements)
    
    @staticmethod
    def _check_prime(p):
        if p <= 1:
            raise Exception('p should be prime')
        for i in range(2, (p**0.5) + 1):
            if p % i == 0:
                raise Exception('p should be prime')
    
    
    class Element:
        def __init__(self, val, p):
            self.p = p
            self.val = val % self.p

        def __eq__(self, other):
            return self.val == other.val

        def __ne__(self, other):
            return self.val != other.val

        def __add__(self, other):
            return Zp.Element(self.val + other.val, self.p)

        def __sub__(self, other):
            return Zp.Element(self.val - other.val, self.p)

        def __mul__(self, other):
            return Zp.Element(self.val * other.val, self.p)

        def __truediv__(self, other):
            return self * ~other

        def __pow__(self, other):
            if other >= 0:
                return Zp.Element(self.val ** other, self.p)
            else:
                return ~Zp.Element(self.val ** (-other), self.p)

        def __invert__(self):
            if self.val == 0:
                raise Exception('no invert for 0')
            for e in range(self.p):
                if Zp.Element(e, self.p) * self == Zp.Element(1, self.p):
                    return Zp.Element(e, self.p)

        def __repr__(self):
            return str(self.val)
        
        def __str__(self):
            return str(self.val)

        def __int__(self):
            return self.val
