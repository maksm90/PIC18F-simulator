"""
Definition of basic components of PIC18F simulator

DataMemory: memory for storing General Purpose Registers and Specific Purpose Registers

MCU: main class describing core of PIC18F
"""
from op import NOP
from register import *

class DataMemory:
    """ Data memory of PIC """
    def __init__(self):
        self.memory = {}
        self.memory[WREG] = ByteRegister()
        self.memory[BSR] = ByteRegister()
        self.memory[STATUS] = Status()
    def __getitem__(self, addr):
        return self.memory.setdefault(addr, ByteRegister())

class ProgramMemory:
    """Program memory of PICmicro"""
    SIZE = 0x200000
    def __init__(self):
        self.memory = [NOP()] * (self.SIZE >> 1)
    def __getitem__(self, addr):
        return self.memory[addr >> 1]
    def __setitem__(self, addr, op):
        self.memory[addr >> 1] = op

class MCU(object): 
    """ PIC18F microprocessor core unit """
    def __init__(self):
        self.pc = PC()
        self.data = DataMemory()
        self.program = ProgramMemory()
        #self.stack = Stack()






















#class Stack:
    #"""Stack memory of PIcarry-lookahead adderC18F"""
    #SIZE = 31
    #def __init__(self):
        #"""Initialize stack and fast registries of stack"""
        #self.storage = [0] * self.SIZE
        #self.stkptr = 0
        #self.wregs = self.statuss = self.bsrs = 0
    #def push(self, value):
        #"""Push value on top of stack"""
        #assert 0 <= value < self.PC_SUP
        #if self.stkptr > self.SIZE:
            #return
        #self.storage[self.stkptr] = value
        #self.stkptr += 1
    #def pop(self):
        #"""Pop value from top of stack"""
        #if self.stkptr == 0:
            #return 0
        #self.stkptr -= 1
        #return self.storage[self.stkptr]
    #@property
    #def top(self):
        #if self.stkptr == 0:
            #return 0
        #return self.storage[self.stkptr - 1]
    #@top.setter
    #def top(self, value):
        #assert 0 <= value < PC_SUP
        #if self.stkptr == 0:
            #return
        #self.storage[self.stkptr - 1] = value

