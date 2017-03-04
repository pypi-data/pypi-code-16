#!/usr/bin/env python
# coding=utf-8
"""
Mal Runtime environment.
"""
import malpy.parser


class Runner:
    """
    This is a runtime environment.
    It sets memory on instantiation and zeros the registers.
    """
    def __init__(self, memory):
        self.memory = memory
        self.registers = [0 for _ in range(16)]
        self.pc = 0
        self.evaluate = {
            'MOVE': self._move,
            'MOVEI': self._movei,
            'LOAD': self._load,
            'STORE': self._store,
            'ADD': self._add,
            'INC': self._inc,
            'SUB': self._sub,
            'DEC': self._dec,
            'MUL': self._mul,
            'DIV': self._div,
            'BEQ': self._beq,
            'BLT': self._blt,
            'BGT': self._bgt,
            'BR': self._br,
            'END': self._end
        }

    def run(self, program):
        """
        Runs an instruction set on a loaded memory and cleared register
        :param program: Either the instruction list or text.
                        It will be parsed if it is text.
        :return: Memory contents
        """
        inst = []

        if isinstance(program, str):
            p = malpy.parser.Parser()
            inst = p.parse(program)
        elif isinstance(program, list):
            inst = program

        halt = False
        while not halt:
            opcode, operands = inst[self.pc]
            halt = self.evaluate[opcode](operands)
            self.pc += 1

        self.registers = [0 for _ in range(16)]
        return self.memory

    def _move(self, ops):
        if ops[0].startswith('R') and ops[1].startswith('R'):
            self.registers[int(ops[1][1:], 16)] = \
                self.registers[int(ops[0][1:], 16)]
            return False
        return True

    def _movei(self, ops):
        if ops[0].startswith('V') and ops[1].startswith('R'):
            self.registers[int(ops[1][1:], 16)] = int(ops[0][1:])
            return False
        return True

    def _load(self, ops):
        if ops[0].startswith('R') and ops[1].startswith('R'):
            self.registers[int(ops[1][1:], 16)] = \
                self.memory[self.registers[int(ops[0][1:], 16)]]
            return False
        return True

    def _store(self, ops):
        if ops[0].startswith('R') and ops[1].startswith('R'):
            self.memory[self.registers[int(ops[1][1:], 16)]] = \
                self.registers[int(ops[0][1:], 16)]

            return False
        return True

    def _add(self, ops):
        if ops[0].startswith('R') and ops[1].startswith('R') and \
                ops[2].startswith('R'):
            self.registers[int(ops[2][1:], 16)] = \
                self.registers[int(ops[0][1:], 16)] + \
                self.registers[int(ops[1][1:], 16)]
            return False
        return True

    def _inc(self, ops):
        if ops[0].startswith('R'):
            self.registers[int(ops[0][1:], 16)] += 1
            return False
        return True

    def _sub(self, ops):
        if ops[0].startswith('R') and ops[1].startswith('R') and \
                ops[2].startswith('R'):
            self.registers[int(ops[2][1:], 16)] = \
                self.registers[int(ops[0][1:], 16)] - \
                self.registers[int(ops[1][1:], 16)]
            return False
        return True

    def _dec(self, ops):
        if ops[0].startswith('R'):
            self.registers[int(ops[0][1:], 16)] -= 1

    def _mul(self, ops):
        if ops[0].startswith('R') and ops[1].startswith('R') and \
                ops[2].startswith('R'):
            self.registers[int(ops[2][1:], 16)] = \
                self.registers[int(ops[0][1:], 16)] * \
                self.registers[int(ops[1][1:], 16)]
            return False
        return True

    def _div(self, ops):
        if ops[0].startswith('R') and ops[1].startswith('R') and \
                ops[2].startswith('R'):
            self.registers[int(ops[2][1:], 16)] = \
                int(self.registers[int(ops[0][1:], 16)] //
                    self.registers[int(ops[1][1:], 16)])
            return False
        return True

    def _bgt(self, ops):
        if ops[0].startswith('R') and ops[1].startswith('R') and \
                ops[2].startswith('L'):
            if self.registers[int(ops[0][1:], 16)] > \
              self.registers[int(ops[1][1:], 16)]:
                self.pc = int(ops[2][1:])
            return False
        return True

    def _blt(self, ops):
        if ops[0].startswith('R') and ops[1].startswith('R') and \
                ops[2].startswith('L'):
            if self.registers[int(ops[0][1:], 16)] < \
              self.registers[int(ops[1][1:], 16)]:
                self.pc = int(ops[2][1:]) - 1
            return False
        return True

    def _beq(self, ops):
        if ops[0].startswith('R') and ops[1].startswith('R') and \
                ops[2].startswith('L'):
            if self.registers[int(ops[0][1:], 16)] == \
              self.registers[int(ops[1][1:], 16)]:
                self.pc = int(ops[2][1:]) - 1
            return False
        return True

    def _br(self, ops):
        if ops[0].startswith('L'):
            self.pc = int(ops[0][1:]) - 1
            return False
        return True

    def _end(self, _):
        return True
