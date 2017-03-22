#!/usr/bin/env python

from nullelf import elf

# This is the wrong way to call
#e = elf('/home/nullp0inter/Documents/Github/fcfuzz/basic_buffer_overflow/bl10_sf_nsp')

raw_bytes = open('/home/nullp0inter/Documents/Github/fcfuzz/basic_buffer_overflow/bl10_sf_nsp','rb').read()

e = elf(raw_bytes)
