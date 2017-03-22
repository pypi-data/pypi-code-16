#!/usr/bin/env python3

import fcfuzz.Crypto.cutils as cutils

def solve_d(e, p, q):
    '''
        Given p, q, and e this will solve for the private
        exponent, d. If p and q are not known this cannot
        be done and requires alternative work to be done
        to find d through some other exploit or for p and
        q to be found and supplied.
    '''
   
    phi = (p-1) * (q-1)
    d = cutils.modinv(e, phi)
    if d:
        print('Found d')
        print('Int:', d)
        print('Hex:', hex(d))
    else:
        print('Failed to find d, something went wrong')
