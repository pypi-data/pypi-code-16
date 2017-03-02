#!/usr/bin/env python
# -*- coding: utf-8 -*-
# XXX Update Docstring
"""
pyFuckery - constants.py
Created on 2/12/17.


"""
# Stdlib


# Brainfuck tokens
SYM_PTR_INC = '>'
SYM_PTR_DEC = '<'
SYM_DATA_INC = '+'
SYM_DATA_DEC = '-'
SYM_IO_OUTPUT = '.'
SYM_IO_INPUT = ','
SYM_JMP_FWD = '['
SYM_JMP_BACKWARD = ']'

SYM_PROGRAM = 'program'
SYM_LOOP = 'loop'
SYM_ACTIONS = 'actions'
SYM_EXPRESSIONS = 'expression'

# Default VM configuration
DEFAULT_MEMORY_SIZE = 30000
MEMORY_MIN_VALUE = 0
MEMORY_MAX_VALUE = 255

# EBNF Grammer for Brainfuck

IGNORE_REGEX = '\{}\{}\{}\{}\{}\{}\{}\{}'.format(SYM_PTR_DEC,
                                                 SYM_PTR_INC,
                                                 SYM_DATA_DEC,
                                                 SYM_DATA_INC,
                                                 SYM_IO_INPUT,
                                                 SYM_IO_OUTPUT,
                                                 SYM_JMP_FWD,
                                                 SYM_JMP_BACKWARD)

# Credit where credit is due - largely influenced by from
# https://webcache.googleusercontent.com/search?q=cache:cdkXLzIKMA0J:https://groups.google.com/a/cdglabs.org/d/topic
# /ohm/Jvwx1jvPOqY+&cd=8&hl=en&ct=clnk&gl=us
# which was inspired by https://www.researchgate.net/publication/255592935_Implementing_Brainfuck_in_COLA_Version_2
GRAMMER = r'''

{program}: {expression}*

{loop}: JMP_FWD {expression}* JMP_BCK

{actions}: PTR_DEC | PTR_INC | DATA_DEC | DATA_INC | IO_INPUT | IO_OUTPUT

{expression}: {actions} | {loop}

PTR_DEC: "{ptr_dec}"
PTR_INC: "{ptr_inc}"
DATA_DEC: "{data_dec}"
DATA_INC: "{data_inc}"
IO_INPUT: "{io_input}"
IO_OUTPUT: "{io_output}"
JMP_FWD: "{jmp_forward}"
JMP_BCK: "{jmp_backwards}"
COMMENT.ignore: /[^{ignore_chars}]+/
'''.format(ptr_inc=SYM_PTR_INC,
           ptr_dec=SYM_PTR_DEC,
           data_dec=SYM_DATA_DEC,
           data_inc=SYM_DATA_INC,
           io_input=SYM_IO_INPUT,
           io_output=SYM_IO_OUTPUT,
           jmp_forward=SYM_JMP_FWD,
           jmp_backwards=SYM_JMP_BACKWARD,
           ignore_chars=IGNORE_REGEX,
           program=SYM_PROGRAM,
           expression=SYM_EXPRESSIONS,
           loop=SYM_LOOP,
           actions=SYM_ACTIONS
           )
