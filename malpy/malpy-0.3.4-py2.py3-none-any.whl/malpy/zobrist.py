# coding=utf-8
"""
Mal Runtime Analyzer.
"""
import uuid
import malpy.runner
import malpy.parser


class ZobristAnalyzer:
    """
    This is a runtime memory profiler and analyzer.
    It uses Zobrist hashing to detect possibly cyclic code.
    Due to the small word size and addressable memory allotment,
    Zobrist hashing is a feasible task during runtime.
    """
    def __init__(self, memory):
        self.memory = memory
        self.divZ = False
        self.oob = False
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
        self.cycle = False
        self.state_table = [uuid.uuid4().int for _ in range(5120)]
        changes = self.memory + self.registers
        self.curr_state = 0
        self._zobrist(dict(enumerate(changes)), {})
        self.states = {self.curr_state: self.pc}

    def _zobrist(self, changes, old):
        for idx, change in changes.items()+old.items():
            self.curr_state ^= self.state_table[64*idx+change]

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
        while not any([halt, self.cycle, self.divZ, self.oob]):
            if self.pc >= len(inst):
                self.oob = True
            else:
                opcode, operands = inst[self.pc]
                self.evaluate[opcode](operands)
                if self.pc in self.states.get(self.curr_state, []):
                    self.cycle = True
                else:
                    self.states[self.curr_state] = \
                        self.states.get(self.curr_state, []) + [self.pc]
                    self.pc += 1

        self.registers = [0 for _ in range(16)]
        if not any([self.cycle, self.divZ, self.oob]):
            return self.memory
        else:
            return [self.cycle, self.divZ, self.oob]

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
