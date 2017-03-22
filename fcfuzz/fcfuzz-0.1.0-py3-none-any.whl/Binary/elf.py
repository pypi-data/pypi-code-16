#!/usr/bin/env python3
# @nullp0inter, python 3 version of nullelf utility
# This project seeks to extend the use of functionality to include other python 3
# utilities allowing more lenient use of modules.

import os
import pty
import struct
import logging
import textwrap
import subprocess


## ---------------[ Exceptions ] ------------------- ##

class FileTypeError(Exception):
    '''
        Exception raised when the path points to a file that is not an ELF.
        
        Attributes:
            path -- The file path used in trying to open the file
            message -- Explanation of the error
    '''

    def __init__(self, path, messsage):
        self.path = path
        self.message = message

## ----------------[ ELF Class ] --------------------##


def get_raw(filepath):
    with open(filepath,'rb') as f:
        return f.read()

class elf:
    '''ELF
       This module aims to handle and process ELF binaries. Intended functionality
       includes identifying key information such as entry, endianness, bitness, 
       target architecture, target ABI (if applicable), among other things.
        
       Additionally I hope to add hooks to the program to allow for interactive
       access to the ELF via python interface.

       Default constructor expects the path to the file but the does exist a class
       method for initializing from raw binary data obtained from running
       `open(<file>,'rb').read()`.
       
       Attributes:
            arch -- The target architecture
    
       >>> e = elf('/bin/true')
       [+] Opened '/bin/true' and parsed successfully.
       >>>

    '''

    def __init__(self, path):
        logging.info('elf object initialized from path')
        raw_bytes = get_raw(path)
        
        logging.debug('Path: \'' + path + '\'')

        if(raw_bytes[0:4] != b'\x7fELF'):
            logging.warning('The provided file is not a valid ELF!')
            logging.warning('Returning \'None\'')
            logging.debug('Header is: ' + str(raw_bytes[0:4]))
            return None
        else:
            self.abi        = self._get_abi(raw_bytes)
            self.arch       = self._get_arch(raw_bytes)
            self.bitness    = self._get_bitness(raw_bytes)
            self.endianness = self._get_endianness(raw_bytes)
            self.entry      = self._get_entry(raw_bytes)
            self.path       = path
            self.e_type     = self._get_etype(raw_bytes) 
            self.e_phoff    = self._get_phoff(raw_bytes)
            self.e_phentsize    = self._get_phentrysize(raw_bytes)
            self.raw_bytes  = raw_bytes
            print("[+] Opened '" + path + "' and parsed successfully.")

##=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=[ INTERNAL ]=-=-=-=-=-=-=-=-=-=-=-=-=-=##
   
    ## INTERNAL :: get the size of each program header table entry
    def _get_phentrysize(self, raw_bytes):
        if (self.bitness.find('32')):
            phentsize_bytes = raw_bytes[0x2c:0x2e]
            phentsize = int(phentsize_bytes.hex(),16)
            return phentsize
        elif (self.bitness.find('64')):
            phentsize_bytes = raw_bytes[0x36:0x38]
            phentsize = int(phentsize_bytes.hex(),16)
            return phentsize
        else:
            logging.warning('Failed to find bitness, returning None')
            return None

    ## INTERNAL :: get the program header table offset
    def _get_phoff(self, raw_bytes):
        if (self.bitness.find('32')):
            phoff_bytes = raw_bytes[0x1c:0x20]
            
            # convert to readable '0x...' format
            # with endian fix for readability
            phoff = '0x' + phoff_bytes.hex()
            phoff = str(struct.pack('<I',int(phoff,16)))
            logging.debug('Got phoff of [32 bit]: ' + phoff)
            return phoff
        
        elif (self.bitness.find('64')):
            phoff_bytes = raw_bytes[0x20:0x28]
            
            # String and big endian conversion
            phoff = '0x' + phoff_bytes.hex()
            phoff = str(struct.pack('<Q',int(phoff,16)))
            logging.debug('Got phoff of [64 bit]: ' + phoff)
            return phoff
        else:
            logging.warning('Failed to detect bitness, returning None')
            return None

    ## INTERNAL :: return the e_type field
    def _get_etype(self, raw_bytes):
        type_byte = raw_bytes[0x10]
        return {
            0x01 : 'Relocatable',
            0x02 : 'Executeable',
            0x03 : 'Shared',
            0x04 : 'Core',
        }.get(type_byte, None)

    ## INTERNAL :: return the architecture
    def _get_arch(self, raw_bytes):
        arch_byte = raw_bytes[0x12]
        logging.debug('Arch byte [0x12] is: ' + str(arch_byte))
        return {
            0x02 : 'SPARC',
            0x03 : 'x86',
            0x08 : 'MIPS',
            0x14 : 'PowerPC',
            0x28 : 'ARM',         # This is 32-bit ARM
            0x2a : 'SuperH',      # I've never even heard of this one
            0x32 : 'IA64',
            0x3e : 'x86_64',      # This is 64-bit Intel architecture
            0xb7 : 'AArch64',     # This is 64-bit ARM
        }.get(arch_byte, None)

    ## INTERNAL :: return the bitness
    def _get_bitness(self, raw_bytes):
        bitness_byte = raw_bytes[0x04]
        logging.debug('Bitness byte [0x04] is: ' + str(bitness_byte))
        return {
            0x01 : '32 bit',
            0x02 : '64 bit',
        }.get(bitness_byte, None)

    ## INTERNAL :: return the target ABI
    def _get_abi(self, raw_bytes):
        abi_byte = raw_bytes[0x07]
        logging.debug('ABI byte [0x07] is: ' + str(abi_byte))
        return {
	    0x00 : 'System V',
            0x01 : 'HP-UX',
            0x02 : 'NetBSD',
            0x03 : 'Linux',
            0x06 : 'Solaris',
            0x07 : 'AIX',
            0x08 : 'IRIX',
            0x09 : 'FreeBSD',
            0x0c : 'OpenBSD',
            0x0d : 'OpenVMS',
            0x0e : 'NonStop Kernel',
            0x0f : 'AROS',
            0x10 : 'Fenix OS',
            0x11 : 'CloudABI',
            0x54 : 'Sortix',
        }.get(abi_byte, None)
    
    ## INTERNAL :: return the endianness
    def _get_endianness(self, raw_bytes):
        endian_byte = raw_bytes [0x05]
        logging.debug('Endian byte [0x05] is: ' + str(endian_byte))
        return {
            0x01 : 'Little Endian (LSB)',
            0x02 : 'Big Endian (MSB)',
        }.get(endian_byte, None)

    ## INTERNAL :: return the program entry point
    def _get_entry(self, raw_bytes):
        if (self.bitness == '32 bit'):
            entry_string_raw = raw_bytes[0x18:0x1b]
            logging.debug('Raw entry point is [32 bit]: ' + str(entry_string_raw))
            entry = self._to_address(entry_string_raw)
            return entry

        elif (self.bitness == '64 bit'):
            entry_string_raw = raw_bytes[0x18:0x1f]
            logging.debug('Raw entry point is [64 bit]: '
                         + str(entry_string_raw))
            entry = self._to_address(entry_string_raw)
            entry = self.endian_convert('b',entry)
            return entry
       
        else:
            logging.warning('Bitness not correctly identified, unable to determine'
                            + ' entry. Returning None.')
            return None
    
    ## Convert string of bytes to address format
    def _to_address(self, s):
        address = '0x' + str(s.hex())
        logging.debug('Got address of: ' + address)
        logging.debug('Address has int value of: ' + str(int(address,16)))
        return address

    ## Fixes the entry string to conform to the correct endianness
    def endian_convert(self,opt,s):
        s = s.lower()
        if (opt == 'big' or opt == 'b'):
            if (self.bitness == "32 bit"):
                entry =  '0x' + str(struct.pack("<I", int(s,16)).hex())
                logging.debug(textwrap.dedent('''\
                    Converted from 32 bit to LSB: 0x{0}
                '''.format(entry)))

            else:
                entry = '0x' + str(struct.pack("<Q", int(s,16)).hex())
                logging.debug(textwrap.dedent('''\
                    Converted from 64 bit to LSB: 0x{0}
                '''.format(entry)))

            return entry
        
        elif (opt == 'little' or opt == 'l'):
            if (self.bitness == "32 bit"):
                entry = '0x' + str(struct.pack('>I', int(s,16)).hex())
                logging.debug(textwrap.dedent( '''\
                    Converted from 32 bit to MSB: {0}
                '''.format(entry)))
            

        else:
            logging.debug('The value of opt is: ' + opt)
            logging.warning(textwrap.dedent('''\
                Improper usage: This function converts a provided hex string of
                the form '0x<value>' to an endianness of the callers choosing
                '''))
            return None
    
##=============================[ ptable Stuff ]=================================##

##=============================[ Public Stuff ]=================================##
    def interactive(self):
        pty.spawn(self.path)
    
    def info(self):
        print(textwrap.dedent('''\
        ==================================================
        =-----------------ELF Information:---------------=
        ==================================================
        ..................................................\
        '''))
        print('[path]:{:.>43}'.format(self.path))
        print('[abi]:{:_>43}*'.format(self.abi))
        print('[arch]:{:.>43}'.format(self.arch))
        print('[bitness]:{:_>40}'.format(self.bitness))
        print('[endianness]:{:.>37}'.format(self.endianness))
        print('[entry]:{:.>42}'.format(self.entry))
        print('[e_type]:{:.>41}'.format(self.e_type))
        print('[e_phoff]:{:.>40}'.format(self.e_phoff))
        print('[e_phentsize]:{:.>35}'.format(self.e_phentsize))
        print(textwrap.dedent('''\
        ..................................................
        ==================================================
        = *Most ELF files leave this field at 0x00 which =
        =  denotes System V, so this field _may_ not be  =
        =  accurate. ABI is included for completeness    =
        ==================================================
        '''))
        return

    def brute_eip():
        pass 
