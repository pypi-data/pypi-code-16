#!/usr/bin/env python

import string

def rot(plaintext, key, strip=True):
    '''
        runs the caesar cipher on the given plaintext by rotating
        key spaces.

        This version forces singular case and will ignore numbers,
        symbols, and punctuation as proper caesar ciphers only 
        work on alphabetic words.

        By default this function strips leading and trailing spaces.
        If this behavior is not desired, a third parameter of False
        can be provided to the function call
    '''
    cipher_parts = []           # Container to hold the results
    parts = plaintext.split(' ')    # Split phrases into words

    # Loop over every part and actually run the rotations    
    for part in parts:
        part = part.upper() # ensure singular case for all letters
        cipher = ''         # empty string to store rotated result

        # Go over each character in the part
        for char in part:
            
            # letters:
            if char in string.ascii_uppercase:
                l = len(string.ascii_uppercase)
                index = string.ascii_uppercase.find(c)
                new_index = (index + key) % l
                cipher += string.ascii_uppercase[new_index]

            # not a letter:
            else:
                cipher += char

        cipher_parts.append(cipher)
    
    # Assemble the ciphertext
    ciphertext = ''
    for part in cipher_parts:
        cipher += part
        cipher += ' '
    
    if strip: return cipher = cipher.strip()
    else: return cipher

def roti(plaintext, key, strip=True):
    '''
        runs a caesar cipher on the given plaintext by rotating
        key spaces.

        Do note that caesar cipher traditionally only accounts
        for the 26 letters of the alphabet whereas this function
        accounts for letters as well. Additionally, this version
        treats uppercase and lowercase seperately so A+2 = C and
        a+2 = c (case of rotation matches original case).

        By default this function strips leading and trailing spaces.
        If this behavior is not desired, a third parameter of False
        can be provided to the function call
    '''
    
    cipher_parts = []
    parts = plaintext.split(' ')
    for part in parts: 
        cipher = ''

        # iterate over the parts
        for c in part:
            # lower case
            if c in string.ascii_lowercase:
                l = len(string.ascii_lowercase)
                index = string.ascii_lowercase.find(c)
                new_index = (index + key) % l
                cipher += string.ascii_lowercase[new_index]
           
            # upper case
            if c in string.ascii_uppercase:
                l = len(string.ascii_uppercase)
                index = string.ascii_uppercase.find(c)
                new_index = (index + key) % l
                cipher += string.ascii_uppercase[new_index]

            # symbols
            if c in string.punctuation:
                l = len(string.punctuation)
                index = string.punctuation.find(c)
                new_index = (index + key) % l
                cipher += string.punctuation[new_index]

            # numbers
            if c in string.digits:
                l = len(string.digits)
                index = string.digits.find(c)
                new_index = (index + key) % l
                cipher += string.digits[new_index]
        
        cipher_parts.append(cipher)

    cipher = ''
    for part in cipher_parts:
        cipher += part
        cipher += ' '

    if strip: return cipher.strip()
    else: return cipher
