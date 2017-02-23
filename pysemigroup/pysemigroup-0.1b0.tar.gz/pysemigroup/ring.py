class RingMatrix(object):
    def __repr__(self):
        return str(self.data)
    def __hash__(self):
        return hash(tuple(sorted(self._hash_data.items())))
    def is_idempotent(self):
        return (self == (self*self))
    def diagonal(self):
        data = {}
        if not(self.dimension[0] == self.dimension[1]):
            raise ValueError("Diagonal are only for square matrix")
        for x in self.dimension[0]:
            data[(x,0)] = self.data[(x,x)]
        return RingMatrix((self.dimension[0],(0,)),data,self.ring)
    def projection(self,proj):
        for x in self.data:
            if self.data[x] in proj:
                self.data[x] = proj[self.data[x]]
            
    def __init__(self,dimension,data,ring):        
        self.dimension = dimension
        self.data = data
        self.ring = buchiRing
        self._hash_data = {}
        for x in self.data:
            self._hash_data[x] = str(self.data[x]) 
    def __mul__(self,other):
        if not (self.dimension[1] == other.dimension[0]):
            raise ValueError("Dimensions mismatch for matrix product")
        if not (self.ring == other.ring):
            raise ValueError("Matrix should be on the same ring")
        dimension=(self.dimension[0],other.dimension[1])
        data = {}
        for x in dimension[0]:
            for y in dimension[1]:
                data[(x,y)] = self.ring.get_zero() 
                for k in self.dimension[1]:
                    data[(x,y)] += self.data[(x,k)]*other.data[(k,y)]                                     
        return RingMatrix(dimension,data, self.ring)
    def __eq__(self,other):
        return hash(self)==hash(other)

class buchiRing(object):
    def __hash__(self):
        return hash(str(self))
    def __eq__(self,other):
        return (hash(self)==hash(other))
    def __repr__(self):
        return "B:"+str(self.value)
    def __init__(self,value):
        if value in [0,1,'-oo']:
            self.value = value
        else:
            raise ValueError(str(value)+"is an incorrect Buchi-ring value")

    def __add__(self,other):
        if self.value == '-oo':
            return buchiRing(other.value)
        if other.value == '-oo':
            return buchiRing(self.value)
        return buchiRing(max(self.value,other.value))
    def __mul__(self,other):
        if ((self.value == "-oo") or (other.value == "-oo")):
            return buchiRing("-oo")
        else:
            return buchiRing(max(self.value,other.value))
    @staticmethod
    def get_zero():
        return buchiRing('-oo')

    @staticmethod
    def get_one():
        return buchiRing(1)
