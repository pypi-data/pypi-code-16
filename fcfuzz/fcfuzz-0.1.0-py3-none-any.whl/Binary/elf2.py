#!/usr/bin/env python

# nullp0inter
# This module handles elfs and processing the relevant information

import os
import sys
import subprocess
import nullproc_handler

def get_raw_bytes(filepath):
    f = open(filepath,'rb')
    raw_bytes = f.read()
    f.close()
    return raw_bytes

class elf:
    '''elf
        This module aims to handle processing of ELF binaries. Functionality
        includes attempting to divine target architecture, divining endianness,
        divining bit-ness, and any other relevant features I think of along the
        way.

        In order to use the module correctly, please pass it the read in RAW BYTES
        of a binary file. This is done as follows for /bin/true (example):
        
        >>> f = open('/bin/true','rb')
        >>> raw_bytes = f.read()
        >>> f.close()
        >>> e = elf(raw_bytes)
        >>> arch = e.arch()
    '''
    
    def __init__(self, raw_bytes):
        
        self.isELF = True

        try:
            if raw_bytes[0:4] != "\x7fELF":
                raise IOError
        except IOError:
            print '!! FileTypeError :: The provided file is not an ELF. This module'
            print 'is designed solely with ELF files in mind. It will not work for'
            print 'PE files and the like. For PE32, use the PE32 module provided.' 
            print 'raw_bytes[0:4] is: ' + raw_bytes[0:4]    
            self.isELF = False
            
        self.arch = self._get_arch(raw_bytes)
        self.ABI = self._get_ABI(raw_bytes)
        self.endianness = self._get_endianness(raw_bytes)
        self.bitness = self._get_bitness(raw_bytes)


    ## Internal Function to act as switch(x) on ABI byte 
    def _switch_targABI(self, target_byte):
        return {
            '\x00' : 'System V',
            '\x01' : 'HP-UX',
            '\x02' : 'NetBSD',
            '\x03' : 'Linux',
            '\x06' : 'Solaris',
            '\x07' : 'AIX',
            '\x08' : 'IRIX',
            '\x09' : 'FreeBSD',
            '\x0c' : 'OpenBSD',
            '\x0d' : 'OpenVMS',
            '\x0e' : 'NonStop Kernel',
            '\x0f' : 'AROS',
            '\x10' : 'Fenix OS',
            '\x11' : 'CloudABI',
            '\x54' : 'Sortix',
        }.get(target_byte, None)

    ## Internal Function to act as switch(x) on arch byte
    def _switch_arch(self, arch_byte):
        return {
            '\x02' : 'SPARC',
            '\x03' : 'x86',
            '\x08' : 'MIPS',
            '\x14' : 'PowerPC',
            '\x28' : 'ARM',			# ARM 32
            '\x2a' : 'SuperH',
            '\x32' : 'IA64',
            '\x3e' : 'x86-64',
            '\xb7' : 'AArch64',			# ARM 64
        }.get(arch_byte, None)
   
    ## Internal function determines ELFs target architecture
    def _get_arch(self, raw_bytes):

        arch_byte = raw_bytes[0x12]
        arch = self._switch_arch(arch_byte)	 

        if arch == None:
            print 'ArchMatchError :: Unexpected error has occured and the'
            print 'architecture cannot be determined. The ELF might be'
            print 'corrupt or vary from the specs.'
            return None 
        
        return arch

    ## Internal function attempts to determine target ABI
    def _get_ABI(self, raw_bytes):
        abi_byte = raw_bytes[0x07]
        abi = self._switch_targABI(abi_byte)

        if abi == None:
            print 'ABIMatchFailure :: Unexpected error has occured and the ABI'
            print 'cannot be determined. The ELF might be corrupt or vary from'
            print 'the specs.'
            return None

        return abi
    
    ## Internal function attempts to determine endianness of target binary
    def _get_endianness(self, raw_bytes):
        end_byte = raw_bytes[0x05]
        return {
            '\x01' : 'Little Endian',
            '\x02' : 'Big Endian',
        }.get(end_byte, None)

    ## Internal function to determine target bitness (32 v 64)
    def _get_bitness(self, raw_bytes):
        bitness_byte = raw_bytes[0x04]
        return {
            '\x01' : '32bit',
            '\x02' : '64bit',
        }.get(bitness_byte, None)   # Naturally returns None if not valid ELF
    
    ## Internal function to determine program entry point
    ## NOTE: Entry point is NOT main
    def _get_entry(self, raw_bytes):
        print 'TODO'

    # Displays the collective information in a (hopefully) neat fashion
    def info(self):

        if(self.isELF):
            print '::ELF Information::'
            print 'Architecture: \t\t'  + self.arch
            print 'Bitness: \t\t'       + self.bitness
            print 'Endianness: \t\t'    + self.endianness
            print 'Target ABI: \t\t'    + self.ABI
            print '\n::NOTE::'
            print 'Standard ELF practice places the byte 0x00 in the ABI slot.'
            print 'This means a target ABI of "System V" may not be entirely'
            print 'accurate and the compiler simply omitted the relevant info.'
            
        else:
            print 'Bytes indicate file is NOT an ELF binary'
