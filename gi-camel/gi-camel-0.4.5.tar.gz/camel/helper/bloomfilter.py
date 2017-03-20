import math
from bitarray import bitarray

def calculate_bloomfilter_size(sample_size, error_rate):
    n = sample_size
    p = error_rate
    m = math.ceil((n*math.log(p)) / math.log(1.0 / (math.pow(2.0, math.log(2.0)))))
    k = round(math.log(2.0) * m / n)
    return m, k


class Bloomfilter:
    def __init__(self, size, hash_count):
        self.size = size
        self.hash_count = hash_count
        self.bit_array = bitarray(size)
        self.bit_array.setall(0)


    def add(self, t):
        for seed in range(self.hash_count):
            result = hash((seed, t)) % self.size
            self.bit_array[result] = 1


    def lookup(self, t):
        for seed in range(self.hash_count):
            result = hash((seed, t)) % self.size
            if self.bit_array[result] == 0:
                return False
        return True
