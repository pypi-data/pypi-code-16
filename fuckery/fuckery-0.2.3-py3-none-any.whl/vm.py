#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
pyFuckery - vm.py
Created on 2/12/17.

VM Defiition to execute brainfuck programs which have been parsed into lark.Tree objects.
"""
# Stdlib
import argparse
import hashlib
import logging
import sys

# Custom Code
from fuckery.constants import DEFAULT_MEMORY_SIZE
from fuckery.constants import SYM_ACTIONS
from fuckery.constants import SYM_DATA_DEC
from fuckery.constants import SYM_DATA_INC
from fuckery.constants import SYM_EXPRESSIONS
from fuckery.constants import SYM_IO_INPUT
from fuckery.constants import SYM_IO_OUTPUT
from fuckery.constants import SYM_LOOP
from fuckery.constants import SYM_PROGRAM
from fuckery.constants import SYM_PTR_DEC
from fuckery.constants import SYM_PTR_INC
from fuckery.exc import ExitCondition
from fuckery.exc import VMError
from fuckery.memory import Storage
from fuckery.parser import parse_program
# Third Party Code
from lark import Tree

log = logging.getLogger(__name__)


class VirtualMachine(object):
    """
    This is the brainfuck VM.  You can drop this into programs that need a brainfuck VM, such as a module you don't
    want a coworker to ever easily maintain, or a really cruel programming based game.
    """
    def __init__(self,
                 memory_size: int = DEFAULT_MEMORY_SIZE,
                 loop_detection: bool = False):
        """
        Init function for the VM.

        :param memory_size: Number of memory cells to instantiate.
        :param loop_detection: Enables loop detection if this evaluates to True.  This is very costly from a
        computation perspective, so use it wisely.
        """
        self.data_pointer = 0
        self._memory_size = memory_size
        self.memory = Storage(n=memory_size)
        self.loop_detection = loop_detection
        self.stream_in = sys.stdin
        self.stream_out = sys.stdout
        self.sym2func = {
            SYM_DATA_DEC: self.dec_data_value,
            SYM_DATA_INC: self.inc_data_value,
            SYM_IO_INPUT: self.io_input,
            SYM_IO_OUTPUT: self.io_output,
            SYM_PTR_DEC: self.dec_data_ptr,
            SYM_PTR_INC: self.inc_data_ptr,
            }

    @property
    def current_value(self) -> int:
        """
        Property which represents the data value the current memory address points too.

        :return:
        """
        return self.memory.get(self.data_pointer)

    @property
    def state_hash(self) -> str:
        """
        MD5 representing the state of the system.  It is a hash of the memory and the current data pointer.

        Note - Computing this frequently can be expensive to do with a large memory section,
        as the memory section is serialized via json.dumps() prior to hashing.

        :return:
        """
        s = self.memory.mem_hash + str(self.data_pointer)
        ret = hashlib.md5(s.encode()).hexdigest()
        return ret

    def inc_data_ptr(self) -> None:
        """
        Increments the data pointer by 1.

        :return: None
        """
        temp = self.data_pointer + 1
        if temp not in self.memory:
            raise VMError('Invalid memory address: {}'.format(temp))
        self.data_pointer = temp

    def dec_data_ptr(self) -> None:
        """
        Decrements the data pointer by 1.

        :return: None
        """
        temp = self.data_pointer - 1
        if temp not in self.memory:
            raise VMError('Invalid memory address: {}'.format(temp))
        self.data_pointer = temp

    def inc_data_value(self) -> None:
        """
        Increments the value pointed to by the data pointer by 1.
        This wraps at 255, back to zero.

        :return: None
        """
        v = self.memory.get(self.data_pointer)
        v = (v + 1) % 256
        self.memory.set(addr=self.data_pointer, value=v)

    def dec_data_value(self) -> None:
        """
        Decrements the value pointed to by the data pointer by 1.
        This wraps at zero, back to 255.

        :return: None
        """
        v = self.memory.get(self.data_pointer)
        v = (v - 1) % 256
        self.memory.set(addr=self.data_pointer, value=v)

    def io_output(self) -> None:
        """
        Writes the current value, after casting it via chr(), to self.stream_out.

        :return: None
        """
        v = self.current_value
        s = chr(v)
        # Ducktyping stream_out
        self.stream_out.write(s)

    def io_input(self) -> None:
        """
        Reads a single character from self.stream_in.

        If self.stream_in is sys.stdin (default value), it will prompt the user for a string and record the FIRST
        byte of that string.  Otherwise, it will attempt to read 1 byte from the stream_in buffer.

        Empty inputs have no effect on the state of the system.

        :return: None
        """
        self.memory.set(addr=self.data_pointer, value=0)
        try:
            if self.stream_in is sys.stdin:  # pragma: no cover
                v = input('>')
                v = v[0]
            else:
                v = self.stream_in.read(1)
            v = ord(v)
        except (TypeError, IndexError):
            return
        except KeyboardInterrupt:
            raise ExitCondition('Keyboard error - exiting.')
        else:
            self.memory.set(addr=self.data_pointer, value=v)

    def run(self, tree: Tree) -> None:
        """
        Walk a Brainfuck AST and execute the program contained in the AST.

        This function is recursive, so its possible for a deeply nested program to hit the Python interpreter recursion
        limit, but if your brainfuck does that, kudos to you.

        :param tree: Parsed brainfuck program.
        :return:
        """
        # XXX This is a manual tree parsing.  Can we do better with a lark Transformer?
        if tree.data == SYM_PROGRAM:
            log.debug('Program entry point.')
            for t in tree.children:
                self.run(t)
            return
        if tree.data == SYM_ACTIONS:
            token = tree.children[0]
            func = self.sym2func.get(token)
            func()
            return
        if tree.data == SYM_EXPRESSIONS:
            for i, t in enumerate(tree.children):
                # log.debug('Executing command #{} - {}'.format(i, repr(t)))
                self.run(tree=t)
            return
        if tree.data == SYM_LOOP:
            sh = ''
            if self.loop_detection:
                sh = self.state_hash
            while self.current_value != 0:
                for t in tree.children:
                    if isinstance(t, Tree):
                        self.run(tree=t)
                if self.loop_detection:
                    if self.state_hash == sh:
                        raise VMError('Infinite loop detected - no change in memory during loop execution!')
                    sh = self.state_hash
            return
        raise NotImplementedError('Unknown tree type seen: {}'.format(tree.data))  # pragma: no cover

    def parse_and_run(self, program: str) -> None:
        """
        Parse and run a brainfuck program.

        :param program: String representing a brainfuck program.
        :return: None
        """
        t = parse_program(s=program)
        self.run(tree=t)


# noinspection PyMissingOrEmptyDocstring
def main(options):  # pragma: no cover
    if not options.verbose:
        logging.disable(logging.DEBUG)
    log.info('Executing "Hello World!"')
    s = '++++++++[>++++[>++>+++>+++>+<<<<-]>+>+>->>+[<]<-]>>.>---.+++++++..+++.>>.<-.<.+++.------.--------.>>+.>++.'
    t = parse_program(s=s)
    vm = VirtualMachine()
    vm.run(tree=t)
    sys.exit(0)


# noinspection PyMissingOrEmptyDocstring
def makeargpaser():  # pragma: no cover
    parser = argparse.ArgumentParser(description="Run a simple hello world program.")
    parser.add_argument('-v', '--verbose', dest='verbose', default=False, action='store_true',
                        help='Enable verbose output')
    return parser


def _main():  # pragma: no cover
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s [%(levelname)s] %(message)s [%(filename)s:%(funcName)s]')
    p = makeargpaser()
    opts = p.parse_args()
    main(opts)


if __name__ == '__main__':  # pragma: no cover
    _main()
