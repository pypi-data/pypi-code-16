# -*- coding: utf-8 -*-
"""
Created on Wed Dec 28 08:40:38 2016

@author: doarni
"""

import binascii as basc
import os


def cipher(txt):
    hex = basc.hexlify(txt.encode())  
    return basc.b2a_hex(hex)

def decipher(data):
    hex = basc.a2b_hex(data)
    return str(basc.unhexlify(hex), 'ascii')
 
def build_cipher_file():
    import json
    
    dict = {}
    
    value1 = str(cipher(input(decipher(b'35353733363537323665363136643635') + ' ')), 'ascii')
    value2 = str(cipher(input(decipher(b'35303631373337333737366637323634') + ' ')), 'ascii')
    value3 = str(cipher(input(decipher(b'3438366637333734') + ' ')), 'ascii')

    dict['data'] = {'value1': value1, 'value2': value2, 'value3': value3}
    
    os.system('cls')    
    
    print('Writing file')
    with open(os.path.dirname(os.path.realpath(__file__)) + '\\postgres_data.json', 'w')as fp:
        json.dump(dict, fp, sort_keys=False, indent=5)
    print('Complete')

if __name__ == '__main__':
    
    import argparse
    
    parser = argparse.ArgumentParser(description = 'Simpler Hex Cipher')
    parser.add_argument('-e','--encrypt', nargs=1, help='encypt string to hex', required=False)
    parser.add_argument('-d','--decrypt', nargs=1, help='decypt hex to string', required=False)
    parser.add_argument('-cf','--create-cipherfile', action='store_true', help='create a new cipher file', required=False)

    args = vars(parser.parse_args())
    if args['encrypt']:
        os.system('cls')
        print(cipher(args['encrypt'][0]))

    if args['decrypt']:
        os.system('cls')        
        print(decipher(args['decrypt'][0]))      
        
    if args['create_cipherfile']:
        os.system('cls')        
        build_cipher_file()