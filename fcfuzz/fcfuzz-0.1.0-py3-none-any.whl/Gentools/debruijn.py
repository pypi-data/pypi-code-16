#!/usr/bin/env python3
import sys
import string
import itertools

def cyclic(strlen, chunklen=3):
    return "".join("".join(x) for x in itertools.islice(itertools.product(string.ascii_uppercase,
	            repeat=chunklen), 1, strlen//chunklen))

def tcyclic(strlen, chunklen=4):
    return "".join("".join(x) for x in itertools.islice(itertools.permutations(string.ascii_letters,
                    strlen), strlen//chunklen))

def cyclic_find(seq):
    seq_len = 4000
    fseq = cyclic(seq_len)
    index = fseq.find(seq)
    while not index:
        if (seq_len) > 10000:
            break
        seq_len *= 2
        fseq = cyclic(seq_len)
        index = fseq.find(seq)
    
    if not index:
        print('Error? Index not found')
        return None
    else:
        print('Index:',index)
        return index

if __name__ == '__main__':
    plen = int(sys.argv[1])
    print('Generating pattern of length:',plen)
    pattern = cyclic(plen)
    print(pattern)
    print('To run a find, use a script or interactive')
