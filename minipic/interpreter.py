"""
Interpreter of machine codes definition
"""
from picmicro import PICmicro

class Interpreter:
    def __init__(self):
        self.cpu = PICmicro()
    def step(self):
        current_op = self.cpu.program[self.cpu.pc]
        current_op.execute(self.cpu)
        self.cpu.pc.inc(current_op.SIZE)
