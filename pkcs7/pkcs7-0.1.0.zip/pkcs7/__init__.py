#!/usr/bin/env python

import os
import sys

__version__ = "0.1.0"
__version_info__ = ( 0, 1, 0)


class PKCS7Encoder(object):
    '''
    RFC 2315: PKCS#7 page 21
    Some content-encryption algorithms assume the
    input length is a multiple of k octets, where k > 1, and
    let the application define a method for handling inputs
    whose lengths are not a multiple of k octets. For such
    algorithms, the method shall be to pad the input at the
    trailing end with k - (l mod k) octets all having value k -
    (l mod k), where l is the length of the input. In other
    words, the input is padded at the trailing end with one of
    the following strings:
             01 -- if l mod k = k-1
            02 02 -- if l mod k = k-2
                        .
                        .
                        .
          k k ... k k -- if l mod k = 0
    The padding can be removed unambiguously since all input is
    padded and no padding string is a suffix of another. This
    padding method is well-defined if and only if k < 256;
    methods for larger k are an open issue for further study.
    but we have the value
    '''
    def __init__(self, k=16):
        assert(k <= 256)
        assert(k > 1)
        self.__klen = k

    def __decode_inner(self,text):
        '''
        Remove the PKCS#7 padding from a text string
        '''
        nl = len(text)
        val = ord(text[-1])
        if nl > self.__klen:
            raise Exception('inner error len(%d) > %d'%(nl,self.__klen))

        # now check whether the code is the same
        delval = 0
        if val > 0 and val < self.__klen:
            delval = 1
            for i in range(val):
                curval = ord(text[nl-i-1])
                if curval != val:
                    delval=0
                    break
        if delval > 0:
            l = nl - val
        else:
            l = nl
        return text[:l]

    ## @param text The padded text for which the padding is to be removed.
    # @exception ValueError Raised when the input padding is missing or corrupt.
    def decode(self, text):
        dectext = ''
        if len(text) > self.__klen:
            i = 0
            while i < len(text):
                clen = len(text) - i
                if clen > self.__klen:
                    clen = self.__klen
                curtext = text[i:(i+clen)]
                dectext += self.__decode_inner(curtext)
                i += clen
        else:
            dectext = self.__decode_inner(text)
        return dectext

    def get_bytes(self,text):
        outbytes = []
        for c in text:
            outbytes.append(ord(c))
        return outbytes

    def get_text(self,inbytes):
        s = ''
        for i in inbytes:
            s += chr((i % 256))
        return s

    def __encode_inner(self,text):
        '''
        Pad an input string according to PKCS#7
        if the real text is bits same ,just expand the text
        '''
        totallen = len(text)
        passlen = 0
        enctext = ''
        #logging.info('all text (%s)'%(self.get_bytes(text)))
        while passlen < totallen:
            curlen = self.__klen
            if curlen > (totallen - passlen):
                curlen = (totallen - passlen)
            curtext = text[passlen:(passlen+curlen)]
            #logging.info('[%d] curtext (%s)'%(passlen,self.get_bytes(curtext)))
            val = ord(curtext[-1])
            addval = 0
            #logging.info('val %d curlen %d'%(val,curlen))
            if curlen == self.__klen and val > 0 and val < self.__klen:
                addval = 1
                for i in range(val):                    
                    curval = ord(curtext[curlen-i-1])
                    #logging.info('[%d]curval %d'%((-i),curval))
                    if curval != val:
                        addval = 0
                        break
            if addval != 0:
                passlen += (curlen - 1)
                enctext += curtext[:(curlen - 1)]
                enctext += chr(1)                
            else:
                if curlen < self.__klen:
                    enctext += curtext
                    for _ in range(self.__klen - curlen):
                        enctext += chr(self.__klen - curlen)
                else:
                    enctext += curtext
                passlen += curlen
            #logging.info('passlen %d'%(passlen))
        return enctext

    ## @param text The text to encode.
    def encode(self, text):
        return self.__encode_inner(text)


