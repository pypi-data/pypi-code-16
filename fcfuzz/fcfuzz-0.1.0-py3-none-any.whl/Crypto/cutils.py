#!/usr/bin/env python3

'''
The cutils module is a crypto math oriented module containing
methods that are useful in cryptography and cryptanalysis. These
include things like gcd, extended gcd (extended euclidean), the
modular inverse and more.

'''

# Suite of tools for cryptographic math
# first iteration is non-optimized, will optimize as I go

# custom exception for modular inverses
class modInverseException(Exception):
    '''
        Simple expandable exception that is raised
        when trying to find the modular inverse where
        one does not exist.
    '''
    pass

def gcd(a,b):
    '''
        Finds the greatest common factor between two given numbers,
        a and b.
    '''
    if a == 0: return b
    return gcd(b%a, a)

def egcd(a,b):
    '''
        Runs the extended euclidean algorithm to determine x and y 
        such that ax + by = gcd(a,b)

        In RSA this is helpful for determining e and, given all
        information, d as well.
    '''
    if a == 0: return (b, 0, 1)
    g,y,x = egcd(b % a, a)
    return (g, x - (b // a) * y, y)

def modinv(a, m):
    '''
        Determines if the modular inverse a^(-1) mod m exists and
        returns it if it does.
    '''
    g, x, y = egcd(a, m)
    if g != 1:
        raise modInverseExceeption('Modular inverse does not exist')
    else:
        return x % m

def totient(n):
    '''
        This function attempts to find the totient of a given number
        n by making use of the gcd function. This works fairly well
        for smaller numbers however it will take longer for larger
        numbers in practice.

        The totient of a number is the count of numbers below itself
        with which it is co-prime (share a gcd of 1).
    '''
    result = 1
    for i in range(2,n):
        if gcd(n,i) == 1: result += 1
    return result

def prim_factorize(n, v=False):
    '''
        A very non-optimized factorization attempt on a given
        number n. Ideally this will return a list of all factors
        of n however it is very slow and can be assumed to be
        non-feasible for factoring numbers over 100 bits
    '''
    factors = []
    for i in range(1,int(n/2)):
        
        # Non-verbose mode, default: simply add each factor, do not print
        if v is False:
            if (n%i) == 0:
                factors.append(i)
        
        # Verbose mode: print each factor as its added
        if v is True:
            if (n%i) == 0:
                factors.append(i)
                print(i)
    return factors
    # Note, I am going to implement some slightly improved methods later
