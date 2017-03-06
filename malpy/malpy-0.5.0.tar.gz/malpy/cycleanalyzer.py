# coding=utf-8
"""Mal Runtime environment with code cycle analyzing.

"""
import uuid

import malpy.actionrunner


class CycleAnalyzer(malpy.actionrunner.ActionRunner):
    """ This is a runtime memory profiler and analyzer.

    It uses Zobrist hashing to detect possibly cyclic code.
    Due to the small word size and addressable memory allotment,
    Zobrist hashing is a feasible task during runtime.

    """
    def __init__(self):
        self.__jit = {
            'MOVE': lambda ops: self._zobrist(
                {ops[1] + 64: self.registers[ops[0]]},
                {ops[1] + 64: self.registers[ops[1]]}
            ),
            'MOVEI': lambda ops: self._zobrist(
                {ops[1] + 64: ops[0]},
                {ops[1] + 64: self.registers[ops[1]]}
            ),
            'LOAD': lambda ops: self._zobrist(
                {ops[1] + 64: self.memory[self.registers[ops[0]]]},
                {ops[1] + 64: self.registers[ops[1]]}
            ),
            'STORE': lambda ops: self._zobrist(
                {self.registers[ops[1]]: self.registers[ops[0]]},
                {self.registers[ops[1]]: self.memory[self.registers[ops[1]]]}
            ),
            'ADD': lambda ops: self._zobrist(
                {ops[2] + 64: (self.registers[ops[0]] +
                               self.registers[ops[1]]) % 64},
                {ops[2] + 64: self.registers[ops[2]]}
            ),
            'INC': lambda ops: self._zobrist(
                {ops[0] + 64: (self.registers[ops[0]] + 1) % 64},
                {ops[0] + 64: self.registers[ops[0]]}
            ),
            'SUB': lambda ops: self._zobrist(
                {ops[2] + 64: (self.registers[ops[0]] -
                               self.registers[ops[1]] + 64) % 64},
                {ops[2] + 64: self.registers[ops[2]]}
            ),
            'DEC': lambda ops: self._zobrist(
                {ops[0] + 64: (self.registers[ops[0]] + 63) % 64},
                {ops[0] + 64: self.registers[ops[0]]}
            ),
            'MUL': lambda ops: self._zobrist(
                {ops[2] + 64: (self.registers[ops[0]] *
                               self.registers[ops[1]]) % 64},
                {ops[2] + 64: self.registers[ops[2]]}
            ),
            'DIV': lambda ops:
                self._zobrist(
                    {ops[2] + 64: (self.registers[ops[0]] //
                                   self.registers[ops[1]]) % 64},
                    {ops[2] + 64: self.registers[ops[2]]}
                ) if ops[1] != 0 else self._zobrist({}, {}),
        }

        super(CycleAnalyzer, self).__init__(self.__jit)
        self.memory = [0] * 64
        self.cycle = False
        self.state_table = [uuid.uuid4().int for _ in range(5120)]
        changes = self.memory + self.registers
        self.curr_state = 0
        self._zobrist(dict(enumerate(changes)), {})
        self.states = {}

    def _zobrist(self, changes, old):
        for idx, change in list(changes.items())+list(old.items()):
            self.curr_state ^= self.state_table[64*idx+change]

    def reset(self):
        """Resets the memory, registers and program counter.

        """
        super(CycleAnalyzer, self).reset()
        self.cycle = False
        self.curr_state = 0
        changes = self.memory + self.registers
        self._zobrist(dict(enumerate(changes)), {})
        self.states = {}

    def run(self, program, memory):
        """Runs an instruction set on a loaded memory and cleared register

        Args:
            program (list[list[str, list[str]]]): Instruction 'AST'.

            memory (list[int]): The memory contents used to run the program.

        Returns:
             list[int]: The memory contents

        """
        self.memory = memory
        while not any([self.halt, self.cycle,
                       self.flags.div_by_zero,
                       self.flags.out_of_bounds,
                       self.flags.bad_operand]):
            if self.program_counter >= len(program):
                self.flags.out_of_bounds = True
            else:
                opcode, operands = program[self.program_counter]
                self.evaluate[opcode](operands)
                if self.program_counter \
                        in self.states.get(self.curr_state, []):
                    print(self.states)
                    self.cycle = True
                else:
                    self.states[self.curr_state] = \
                        self.states.get(self.curr_state, []) \
                        + [self.program_counter]
                    self.program_counter += 1
        if not any([self.cycle,
                    self.flags.div_by_zero,
                    self.flags.out_of_bounds,
                    self.flags.bad_operand]):
            return self.memory
        else:
            return [self.cycle,
                    self.flags.div_by_zero,
                    self.flags.out_of_bounds,
                    self.flags.bad_operand]
