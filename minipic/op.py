from register import WREG

def _operand_reg(cpu, f, a):
    if a == 1:
        addr = (cpu.data[BSR].get() << 8) | f
    else:
        addr = f if f < 0x80 else (0x0f00 | f)
    return cpu.data[addr]

def _result_reg(cpu, operand_reg, d):
    return cpu.data[WREG] if d == 0 else operand_reg


class Op:
    """ Abstract class of operation of MC """
    SIZE = 2
    def execute(self, cpu):
        raise NotImplementedError()

class NOP(Op):
    """ No operation """
    def execute(self, cpu):
        cpu.pc.inc(self.SIZE)

class MOVLW(Op):
    """ Move constant to WREG """
    def __init__(self, k):
        self.k = k
    def execute(self, cpu):
        cpu.data[WREG].put(self.k)
        cpu.pc.inc(self.SIZE)

class MOVWF(Op):
    """ Mov WREG to 'f' """
    def __init__(self, f, a):
        self.f = f
        self.a = a
    def execute(self, cpu):
        wreg_value = cpu.data[WREG].get()
        dest = _operand_reg(cpu, self.f, self.a)
        dest.put(wreg_value) 
        cpu.pc.inc(self.SIZE)

class BTG(Op):
    """ Inverse bit in 'f' """
    def __init__(self, f, b, a):
        self.f = f
        self.b = b
        self.a = a
    def execute(self, cpu):
        reg = _operand_reg(cpu, self.f, self.a)
        reg[self.a] ^= 1
        cpu.pc.inc(self.SIZE)

class BTFSC(Op):
    """ Test bit and skip next instruction if it's equal 0 """
    def __init__(self, f, b, a):
        self.f = f
        self.b = b
        self.a = a
    def execute(self, cpu):
        reg = _operand_reg(cpu, self.f, self.a)
        if reg[self.b] == 0:
            cpu.pc.inc(2)
        cpu.pc.inc(self.SIZE)

class CALL(Op):
    """ Goto subroutine in all range of memory """
    SIZE = 4
    def __init__(self, n, s):
        self.n = n
        self.s = s
    def execute(self, cpu):
        cpu.stack.push(cpu.pc.value + 4)
        cpu.pc.value = self.n << 1
        if self.s == 1:
            cpu.stack.ws = cpu.data[WREG].get()
            cpu.stack.statuss = cpu.data[STATUS].get()
            cpu.stack.bsrs = cpu.data[BSR].get()

class DECFSZ(Op):
    """ Decrement 'f', skip next instruction if result is equal 0 """
    def __init__(self, f, d, a):
        self.f = f
        self.d = d
        self.a = a
    def execute(self, cpu):
        src = _operand_reg(cpu, self.f, self.a)
        dest = _result_reg(cpu, src, self.d)
        result = src.get() - 1
        if result == 0:
            cpu.pc.inc(2)
        dest.put(result)
        cpu.pc.inc(self.SIZE)

class GOTO(Op):
    """ Go to specific address """
    SIZE = 4
    def __init__(self, k):
        self.k = k
    def execute(self, cpu):
        cpu.pc.value = self.k << 1

class RETURN(Op):
    """ Return from subroutine """
    SIZE = 1
    def __init__(self, s):
        self.s = s
    def execute(self, cpu):
        cpu.pc.value = cpu.stack.pop()
        if self.s == 1:
            cpu.data[WREG].set(pic.stack.ws)
            cpu.data[STATUS].set(pic.stack.statuss)
            cpu.data[BSR].set(pic.stack.bsrs)














# bitmasks of flags
#N, OV, Z, DC, C = 0b10000, 0b01000, 0b00100, 0b00010, 0b00001

#def _add(cpu, resAddr, arg1, arg2):
    #"""Internal procedure that performs addition 'arg1' and 'arg2' and saving result by address 'resAddr'
    #This operation affects C, DC, Z, OV, N flags
    #cpu: core of PIC18F
    #resAddr: address of saving result
    #arg1: first argument of operation
    #arg2: second argument of operation
    #"""
    #result = arg1 + arg2

    #carry = (result & 0x100) >> 8
    #set_bits = carry
    #decCarry = (((arg1 & 0xf) + (arg2 & 0xf)) & 0x10) >> 4
    #set_specificbits |= decCarry << 1
    #if result & 0xff == 0:
        #set_bits |= Z
    #signCarry = (((arg1 & 0x7f) + (arg2 & 0x7f)) & 0x80) >> 7
    #set_bits |= (signCarry ^ carry) << 3
    #sign = (result & 0x80) >> 7
    #set_bits |= sign << 4

    #cpu.data[resAddr] = result & 0xff
    #cpu.affectStatusBits(0x1f, set_bits)

#def _and(cpu, resAddr, arg1, arg2):
    #"""Internal procedure that performs bitwise conjuction 'arg1' with 'arg2' and saving result by address 'resAddr'
    #This operation affects Z and N flags
    #cpu: core of PIC18F
    #resAddr: address of result
    #arg1: first argument of operation
    #arg2: second argument of operation
    #"""
    #result = arg1 & arg2
    #set_bits = 0
    #if result == 0:
        #set_bits |= Z
    #if result & 0x80 > 0:
        #set_bits |= N
    #cpu.data[resAddr] = result
    #cpu.affectStatusBits(N | Z, set_bits)

#def _ior(cpu, resAddr, arg1, arg2):
    #"""Internal procedure for bitwise disjunction between 'arg1' and 'arg2' and saving result by address 'resAddr'
    #This operation affects Z and N flags
    #cpu: core of PIC18F
    #resAddr: address for result
    #arg1: first argument
    #arg2: second argument
    #"""
    #result = arg1 | arg2
    #set_bits = 0
    #if result == 0:
        #set_bits |= Z
    #if result & 0x80 > 0:
        #set_bits |= N
    #cpu.data[resAddr] = result
    #cpu.affectStatusBits(N | Z, set_bits)

#def _xor(cpu, resAddr, arg1, arg2):
    #"""Internal procedure for exclusive disjunction between 'arg1' and 'arg2' and saving result in memory cell by address 'resAddr'
    #This operation affects Z and N flags
    #cpu: core of PIC18F
    #resAddr: address for result
    #arg1: first argument
    #arg2: second argument
    #"""
    #result = arg1 ^ arg2
    #set_bits = 0
    #if result == 0:
        #set_bits |= Z
    #if result & 0x80 > 0:
        #set_bits |= N
    #cpu.data[resAddr] = result
    #cpu.affectStatusBits(N | Z, set_bits)

#########################################
## Byte oriented commands with registers
#########################################
#def addwf(cpu, f, d, a):
    #"""Add WREG with 'f'
    #affect C, DC, Z, OV, N
    #cpu: core of PIC18F
    #f: part of register address of second term of sum
    #d: flag specifying direction of saving result (if d = 0 then result is saved in WREG else in register by address defined 'f')
    #a: flag specifying address of second term of sum (if a = 1 then address defined BSR else fast access bank is used)
    #"""
    #if a == 1:
        #argAddr = (cpu.bsr << 8) | f
    #else:
        #argAddr = f if f < 0x80 else (0xf00 | f)
    #resAddr = argAddr if d == 1 else WREG
    #_add(cpu, resAddr, pic.wreg, pic.data[argAddr])

#addwf.size = 2


#def addwfc(cpu, f, d, a):
    #"""Add WREG with 'f' and with bit C
    #affect C, DC, Z, OV, N
    #cpu: core of PIC18F
    #f: part of register address of second term of sum
    #d: flag specifying direction of saving result (if d = 0 then result is saved in WREG else in register by address defined 'f')
    #a: flag specifying address of second term of sum (if a = 1 then address defined BSR else fast access bank is used)
    #"""
    #if a == 1:
        #argAddr = (cpu.bsr << 8) | f
    #else:
        #argAddr = f if f < 0x80 else (0xf00 | f)
    #carryFlag = cpu.status & C
    #arg1, arg2 = cpu.wreg, pic.data[argAddr]
    #result = arg1 + arg2 + carryFlag

    #carry = (result & 0x100) >> 8
    #set_bits = carry
    #decCarry = (((arg1 & 0xf) + (arg2 & 0xf) + carryFlag) & 0x10) >> 4
    #set_bits |= decCarry << 1
    #if result & 0xff == 0:
        #set_bits |= Z
    #signCarry = (((arg1 & 0x7f) + (arg2 & 0x7f) + carryFlag) & 0x80) >> 7
    #set_bits |= (signCarry ^ carry) << 3
    #sign = (result & 0x80) >> 7
    #set_bits |= sign << 4

    #resAddr = WREG if d == 0 else argAddr
    #cpu.data[resAddr] = result & 0xff
    #cpu.affectStatusBits(0x1f, set_bits)
 
#addwfc.size = 2


#def andwf(cpu, f, d, a):
    #"""Conjunction between WREG and 'f'
    #affect Z, N
    #cpu: core of PIC18F
    #f: part of register address of second term of conjunction
    #d: flag specifying direction of saving result (if d = 0 then result is saved in WREG else in register by address defined 'f')
    #a: flag specifying address of second term of conjuction (if a = 1 then address defined BSR else fast access bank is used)
    #"""
    #if a == 1:
        #argAddr = (cpu.bsr << 8) | f
    #else:
        #argAddr = f if f < 0x80 else (0xf00 | f)
    #resAddr = WREG if d == 0 else argAddr
    #_and(cpu, resAddr, pic.wreg, pic.data[argAddr]) 
    
#andwf.size = 2


#def clrf(cpu, f, a):
    #"""Clear register 'f'
    #affect Z
    #cpu: core of PIC18F
    #f: part of register address
    #a: flag specifying register address (if a = 1 then address defined BSR else fast access bank is used)
    #"""
    #if a == 1:
        #argAddr = (cpu.bsr << 8) | f
    #else:
        #argAddr = f if f < 0x80 else (0xf00 | f)
    #cpu.data[argAddr] = 0
    #cpu.affectStatusBits(Z, Z)

#clrf.size = 2


#def comf(cpu, f, d, a):
    #"""Inverse register 'f'
    #affect Z, N
    #cpu: core of PIC18F
    #f: part of register address
    #d: flag specifying direction of saving result (if d = 0 then result is saved in WREG else in register by address defined 'f')
    #a: flag specifying register address (if a = 1 then address is defined with BSR else fast access bank is used)
    #"""
    #if a == 1:
        #argAddr = (cpu.bsr << 8) | f
    #else:
        #argAddr = f if f < 0x80 else (0xf00 | f)
    #resAddr = WREG if d == 0 else argAddr

    #result = ~cpu.data[argAddr] & 0xff
    #set_bits = 0
    #if result == 0:
        #set_bits |= Z
    #if result & 0x80 > 0:
        #set_bits |= N
    #cpu.data[resAddr] = result
    #cpu.affectStatusBits(N | Z, set_bits)

#comf.size = 2


#def cpfseq(cpu, f, a):
    #"""Compare WREG and 'f'; skip next instuction if they are equal
    #cpu: core of PIC18F
    #f: part of register address
    #a: flag specifying register address (if a = 1 then address is defined with BSR else fast access bank is used)
    #"""
    #if a == 1:
        #argAddr = (cpu.bsr << 8) | f
    #else:
        #argAddr = f if f < 0x80 else (0xf00 | f)
    #if cpu.data[argAddr] == pic.wreg:
        #cpu.incPC(2)

#cpfseq.size = 2


#def cpfsgt(cpu, f, a):
    #"""Compare WREG and 'f'; if WREG > 'f' then skip next instruction
    #cpu: core of PIC18F
    #f: part of register address
    #a: flag specifying register address (if a = 1 then address is defined with BSR else fast access bank is used)
    #"""
    #if a == 1:
        #argAddr = (cpu.bsr << 8) | f
    #else:
        #argAddr = f if f < 0x80 else (0xf00 | f)
    #if cpu.data[argAddr] < pic.wreg:
        #cpu.incPC(2)

#cpfsgt.size = 2


#def cpfslt(cpu,f, a):
    #"""Compare WREG and 'f'; if WREG < 'f' then skip next instruction
    #cpu: core of PIC18F
    #f: part of register address
    #a: flag specifying register address (if a = 1 then address is defined with BSR else fast access bank is used)
    #"""
    #if a == 1:
        #argAddr = (cpu.bsr << 8) | f
    #else:
        #argAddr = f if f < 0x80 else (0xf00 | f)
    #if cpu.data[argAddr] > pic.wreg:
        #cpu.incPC(2)

#cpfslt.size = 2


#def decf(cpu, f, d, a):
    #"""Decrement 'f'
    #affect C, DC, Z, OV, N flags
    #cpu: core of PIC18F
    #f: part of argument register address
    #d: flag specifying direction of saving result (if d = 0 then result is saved in WREG else in register by address defined 'f')
    #a: flag specifying register address (if a = 1 then address is defined with BSR else fast access bank is used)
    #"""
    #if a == 1:
        #argAddr = (cpu.bsr << 8) | f
    #else:
        #argAddr = f if f < 0x80 else (0xf00 | f)
    #resAddr = WREG if d == 0 else argAddr

    #arg = cpu.data[argAddr]
    #result = arg - 1
    #set_bits = 0
    #if arg != 0:
        #set_bits |= C
    #if (arg & 0xf) != 0:
        #set_bits |= DC
    #if result == 0:
        #set_bits |= Z
    #if result == 0x7f:
        #set_bits |= OV
    #if result & 0x80 > 0:
        #set_bits |= N
    #cpu.data[resAddr] = result & 0xff
    #cpu.affectStatusBits(0x1f, set_bits)

#decf.size = 2


#def decfsz(cpu, f, d, a):
    #"""Decrement 'f'; skip next instruction if result is equal zero
    #cpu: core of PIC18F
    #f: part of argument register address
    #d: flag specifying direction of saving result (if d = 0 then result is saved in WREG else in register by address defined 'f')
    #a: flag specifying register address (if a = 1 then address is defined with BSR else fast access bank is used)
    #"""
    #if a == 1:
        #argAddr = (cpu.bsr << 8) | f
    #else:
        #argAddr = f if f < 0x80 else (0xf00 | f)
    #resAddr = WREG if d == 0 else argAddr

    #result = cpu.data[argAddr] - 1
    #if result == 0:
        #cpu.incPC(2)
    #cpu.data[resAddr] = result & 0xff

#decf.size = 2


#def dcfsnz(cpu, f, d, a):
    #"""Decrement 'f'; skip next instruction if result is not equal zero
    #cpu: core of PIC18F
    #f: part of argument register address
    #d: flag specifying direction of saving result (if d = 0 then result is saved in WREG else in register by address defined 'f')
    #a: flag specifying register address (if a = 1 then address is defined with BSR else fast access bank is used)
    #"""
    #if a == 1:
        #argAddr = (cpu.bsr << 8) | f
    #else:
        #argAddr = f if f < 0x80 else (0xf00 | f)
    #resAddr = WREG if d == 0 else argAddr

    #result = cpu.data[argAddr] - 1
    #if result != 0:
        #cpu.incPC(2)
    #cpu.data[resAddr] = result & 0xff

#dcfsnz.size = 2


#def incf(cpu, f, d, a):
    #"""Increment 'f'
    #affect C, DC, Z, OV, N flags
    #cpu: core of PIC18F
    #f: part of argument register address
    #d: flag specifying direction of saving result (if d = 0 then result is saved in WREG else in register by address defined 'f')
    #a: flag specifying register address (if a = 1 then address is defined with BSR else fast access bank is used)
    #"""
    #if a == 1:
        #argAddr = (cpu.bsr << 8) | f
    #else:
        #argAddr = f if f < 0x80 else (0xf00 | f)
    #resAddr = WREG if d == 0 else argAddr

    #arg = cpu.data[argAddr]
    #result = arg + 1
    #set_bits = 0
    #if arg == 0xff:
        #set_bits |= C
    #if (arg & 0xf) == 0xf:
        #set_bits |= DC
    #if (result & 0xff) == 0:
        #set_bits |= Z
    #if result == 0x80:
        #set_bits |= OV
    #if result & 0x80 > 0:
        #set_bits |= N
    #cpu.data[resAddr] = result & 0xff
    #cpu.affectStatusBits(0x1f, set_bits)

#incf.size = 2


#def incfsz(cpu, f, d, a):
    #"""Increment 'f'; skip next instruction if result is equal zero
    #cpu: core of PIC18F
    #f: part of argument register address
    #d: flag specifying direction of saving result (if d = 0 then result is saved in WREG else in register by address defined 'f')
    #a: flag specifying register address (if a = 1 then address is defined with BSR else fast access bank is used)
    #"""
    #if a == 1:
        #argAddr = (cpu.bsr << 8) | f
    #else:
        #argAddr = f if f < 0x80 else (0xf00 | f)
    #resAddr = WREG if d == 0 else argAddr

    #result = (cpu.data[argAddr] + 1) & 0xff
    #if result == 0:
        #cpu.incPC(2)
    #cpu.data[resAddr] = result

#incfsz.size = 2


#def infsnz(cpu, f, d, a):
    #"""Increment 'f'; skip next instruction if result is not equal zero
    #cpu: core of PIC18F
    #f: part of argument register address
    #d: flag specifying direction of saving result (if d = 0 then result is saved in WREG else in register by address defined 'f')
    #a: flag specifying register address (if a = 1 then address is defined with BSR else fast access bank is used)
    #"""
    #if a == 1:
        #argAddr = (cpu.bsr << 8) | f
    #else:
        #argAddr = f if f < 0x80 else (0xf00 | f)
    #resAddr = WREG if d == 0 else argAddr

    #result = (cpu.data[argAddr] + 1) & 0xff
    #if result != 0:
        #cpu.incPC(2)
    #cpu.data[resAddr] = result

#infsnz.size = 2


#def iorwf(cpu, f, d, a):
    #"""Logic disjunction between WREG and 'f';
    #Flags Z and N are affected
    #cpu: core of PIC18F
    #f: part of argument register address
    #d: flag specifying direction of saving result (if d = 0 then result is saved in WREG else in register by address defined 'f')
    #a: flag specifying register address (if a = 1 then address is defined with BSR else fast access bank is used)
    #"""
    #if a == 1:
        #argAddr = (cpu.bsr << 8) | f
    #else:
        #argAddr = f if f < 0x80 else (0xf00 | f)
    #resAddr = WREG if d == 0 else argAddr
    #_ior(cpu, resAddr, pic.wreg, pic.data[argAddr])

#iorwf.size = 2


#def movf(cpu, f, d, a):
    #"""Move 'f'
    #Flags Z and N are affected
    #cpu: core of PIC18F
    #f: part of argument register address
    #d: flag specifying direction of saving result (if d = 0 then result is saved in WREG else in register by address defined 'f')
    #a: flag specifying register address (if a = 1 then address is defined with BSR else fast access bank is used)
    #"""
    #if a == 1:
        #argAddr = (cpu.bsr << 8) | f
    #else:
        #argAddr = f if f < 0x80 else (0xf00 | f)
    #resAddr = WREG if d == 0 else argAddr
    #cpu.data[resAddr] = pic.data[argAddr]

#movf.size = 2


#def movff(cpu, fs, fd):
    #"""Move source 'fs' to destination 'fd'
    #cpu: core of PIC18F
    #fs: address of source
    #fd: address of destination
    #"""
    #assert fs != PCL and fs != TOSU and fs != TOSH and fs != TOSL
    #cpu.data[fd] = pic.data[fs]

#movff.size = 4


#def movwf(cpu, f, a):
    #"""Move WREG to 'f'
    #cpu: core of PIC18F
    #f: part of argument register address
    #a: flag specifying register address (if a = 1 then address is defined with BSR else fast access bank is used)
    #"""
    #if a == 1:
        #argAddr = (cpu.bsr << 8) | f
    #else:
        #argAddr = f if f < 0x80 else (0xf00 | f)
    #cpu.data[argAddr] = pic.wreg

#movwf.size = 2


#def mulwf(cpu, f, a):
    #"""Multiply WREG and 'f'
    #cpu: core of PIC18F
    #f: part of argument register address
    #a: flag specifying register address (if a = 1 then address is defined with BSR else fast access bank is used)
    #"""
    #if a == 1:
        #argAddr = (cpu.bsr << 8) | f
    #else:
        #argAddr = f if f < 0x80 else (0xf00 | f)
    #result = cpu.wreg * pic.data[argAddr]
    #cpu.prodl = result & 0xff
    #cpu.prodh = (result & 0xff00) >> 8

#mulwf.size = 2


#def negf(cpu, f, a):
    #"""Negative value of 'f'
    #Flags C, DC, Z, OV, N are affected
    #cpu: core of PIC18F
    #f: part of argument register address
    #a: flag specifying register address (if a = 1 then address is defined with BSR else fast access bank is used)
    #"""
    #if a == 1:
        #argAddr = (cpu.bsr << 8) | f
    #else:
        #argAddr = f if f < 0x80 else (0xf00 | f)

    #result = (~cpu.data[argAddr] + 1) & 0xff
    #set_bits = 0
    #if result & 0x80 > 0:
        #set_bits |= N
    #if result == 0:
        #set_bits |= (C | Z)
    #if result & 0xf == 0:
        #set_bits |= DC
    #if result == 0x80:
        #set_bits |= OV
    #cpu.data[argAddr] = result
    #cpu.affectStatusBits(0x1f, set_bits)

#negf.size = 2


#def rlcf(cpu, f, d, a):
    #"""Left shift with carry
    #Flags C, Z, N are affects
    #cpu: core of PIC18F
    #f: part of argument register address
    #d: flag specifying direction of saving result (if d = 0 then result is saved in WREG else in register by address defined 'f')
    #a: flag specifying register address (if a = 1 then address is defined with BSR else fast access bank is used)
    #"""
    #if a == 1:
        #argAddr = (cpu.bsr << 8) | f
    #else:
        #argAddr = f if f < 0x80 else (0xf00 | f)
    #resAddr = WREG if d == 0 else argAddr

    #result = cpu.data[argAddr] << 1
    #result |= cpu.status & C
    #set_bits = (result & 0x100) >> 8
    #if result & 0xff == 0:
        #set_bits |= Z
    #if result & 0x80 > 0:
        #set_bits |= N

    #cpu.data[resAddr] = result & 0xff
    #cpu.affectStatusBits(C | Z | N, set_bits)

#rlcf.size = 2


#def rlncf(cpu, f, d, a):
    #"""Left shift without carry
    #Flags Z, N are affects
    #cpu: core of PIC18F
    #f: part of argument register address
    #d: flag specifying direction of saving result (if d = 0 then result is saved in WREG else in register by address defined 'f')
    #a: flag specifying register address (if a = 1 then address is defined with BSR else fast access bank is used)
    #"""
    #if a == 1:
        #argAddr = (cpu.bsr << 8) | f
    #else:
        #argAddr = f if f < 0x80 else (0xf00 | f)
    #resAddr = WREG if d == 0 else argAddr

    #result = cpu.data[argAddr] << 1
    #result |= (result >> 8)
    #set_bits = 0
    #if result & 0xff == 0:
        #set_bits |= Z
    #if result & 0x80 > 0:
        #set_bits |= N

    #cpu.data[resAddr] = result & 0xff
    #cpu.affectStatusBits(Z | N, set_bits)

#rlncf.size = 2


#def rrcf(cpu, f, d, a):
    #"""Right shift with carry
    #Flags C, Z, N are affects
    #cpu: core of PIC18F
    #f: part of argument register address
    #d: flag specifying direction of saving result (if d = 0 then result is saved in WREG else in register by address defined 'f')
    #a: flag specifying register address (if a = 1 then address is defined with BSR else fast access bank is used)
    #"""
    #if a == 1:
        #argAddr = (cpu.bsr << 8) | f
    #else:
        #argAddr = f if f < 0x80 else (0xf00 | f)
    #resAddr = WREG if d == 0 else argAddr

    #arg = cpu.data[argAddr]
    #set_bits = arg & 0x1
    #result = (arg >> 1) | ((cpu.status & C) << 7)
    #if result & 0xff == 0:
        #set_bits |= Z
    #if result & 0x80 > 0:
        #set_bits |= N

    #cpu.data[resAddr] = result
    #cpu.affectStatusBits(C | Z | N, set_bits)

#rrcf.size = 2


#def rrncf(cpu, f, d, a):
    #"""Right shift without carry
    #Flags Z, N are affects
    #cpu: core of PIC18F
    #f: part of argument register address
    #d: flag specifying direction of saving result (if d = 0 then result is saved in WREG else in register by address defined 'f')
    #a: flag specifying register address (if a = 1 then address is defined with BSR else fast access bank is used)
    #"""
    #if a == 1:
        #argAddr = (cpu.bsr << 8) | f
    #else:
        #argAddr = f if f < 0x80 else (0xf00 | f)
    #resAddr = WREG if d == 0 else argAddr

    #arg = cpu.data[argAddr]
    #arg |= ((arg & 0b1) << 8)
    #result = arg >> 1
    #set_bits = 0
    #if result & 0xff == 0:
        #set_bits |= Z
    #if result & 0x80 > 0:
        #set_bits |= N

    #cpu.data[resAddr] = result
    #cpu.affectStatusBits(Z | N, set_bits)

#rrncf.size = 2


#def setf(cpu, f, a):
    #"""Set all bits of 'f'
    #cpu: core of PIC18F
    #f: part of argument register address
    #a: flag specifying register address (if a = 1 then address is defined with BSR else fast access bank is used)
    #"""
    #if a == 1:
        #argAddr = (cpu.bsr << 8) | f
    #else:
        #argAddr = f if f < 0x80 else (0xf00 | f)
    #cpu.data[argAddr] = 0xff

#setf.size = 2


#def subfwb(cpu, f, d, a):
    #"""Substitute 'f' from WREG with borrow
    #Flags Z, N, OV, DC, C are affects
    #cpu: core of PIC18F
    #f: part of argument register address
    #d: flag specifying direction of saving result (if d = 0 then result is saved in WREG else in register by address defined 'f')
    #a: flag specifying register address (if a = 1 then address is defined with BSR else fast access bank is used)
    #"""
    #if a == 1:
        #argAddr = (cpu.bsr << 8) | f
    #else:
        #argAddr = f if f < 0x80 else (0xf00 | f)
    #resAddr = WREG if d == 0 else argAddr

    #arg1 = cpu.wreg
    #arg2 = (-cpu.data[argAddr]) & 0xff
    #arg3 = 0 if (cpu.status & C == 1) else 0xff
    #result = arg1 + arg2 + arg3

    #set_bits = 0
    #if result & 0xf00 > 0:
        #set_bits |= C
    #if ((arg1 & 0xf) + (arg2 & 0xf) + (arg3 & 0xf)) & 0xf0 > 0:
        #set_bits |= DC
    #if result & 0xff == 0:
        #set_bits |= Z
    #carryIntoSign = ((arg1 & 0x7f) + (arg2 & 0x7f) + (arg3 & 0x7f)) & 0x80
    #if ((result & 0x100) ^ (carryIntoSign << 1)) > 0:
        #set_bits |= OV
    #if result & 0x80 > 0:
        #set_bits |= N

    #cpu.data[resAddr] = result & 0xff
    #cpu.affectStatusBits(0x1f, set_bits)

#subfwb.size = 2


#def subwf(cpu, f, d, a):
    #"""Substitute WREG from 'f'
    #Flags Z, N, OV, DC, C are affects
    #cpu: core of PIC18F
    #f: part of argument register address
    #d: flag specifying direction of saving result (if d = 0 then result is saved in WREG else in register by address defined 'f')
    #a: flag specifying register address (if a = 1 then address is defined with BSR else fast access bank is used)
    #"""
    #if a == 1:
        #argAddr = (cpu.bsr << 8) | f
    #else:
        #argAddr = f if f < 0x80 else (0xf00 | f)
    #resAddr = WREG if d == 0 else argAddr

    #arg1, arg2 = cpu.data[argAddr], (~pic.wreg + 1) & 0xff
    #result = arg1 + arg2

    #set_bits = 0
    #if result & 0x100 > 0:
        #set_bits |= C
    #if ((arg1 & 0xf) + (arg2 & 0xf)) & 0x10 > 0:
        #set_bits |= DC
    #if result & 0xff == 0:
        #set_bits |= Z
    #if (arg1 & 0x80 == arg2 & 0x80) and (arg1 & 0x80 != result & 0x80):
        #set_bits |= OV
    #if result & 0x80 > 0:
        #set_bits |= N

    #cpu.data[resAddr] = result & 0xff
    #cpu.affectStatusBits(0x1f, set_bits)

#subwf.size = 2


#def subwfb(cpu, f, d, a):
    #"""Substitute WREG from 'f' with borrow
    #Flags Z, N, OV, DC, C are affects
    #cpu: core of PIC18F
    #f: part of argument register address
    #d: flag specifying direction of saving result (if d = 0 then result is saved in WREG else in register by address defined 'f')
    #a: flag specifying register address (if a = 1 then address is defined with BSR else fast access bank is used)
    #"""
    #if a == 1:
        #argAddr = (cpu.bsr << 8) | f
    #else:
        #argAddr = f if f < 0x80 else (0xf00 | f)
    #resAddr = WREG if d == 0 else argAddr

    #arg1 = cpu.data[argAddr]
    #arg2 = (-cpu.wreg) & 0xff
    #arg3 = 0 if (cpu.status & C == 1) else 0xff
    #result = arg1 + arg2 + arg3

    #set_bits = 0
    #if result & 0xf00 > 0:
        #set_bits |= C
    #if ((arg1 & 0xf) + (arg2 & 0xf) + (arg3 & 0xf)) & 0xf0 > 0:
        #set_bits |= DC
    #if result & 0xff == 0:
        #set_bits |= Z
    #carryIntoSign = ((arg1 & 0x7f) + (arg2 & 0x7f) + (arg3 & 0x7f)) & 0x80
    #if ((result & 0x100) ^ (carryIntoSign << 1)) > 0:
        #set_bits |= OV
    #if result & 0x80 > 0:
        #set_bits |= N

    #cpu.data[resAddr] = result & 0xff
    #cpu.affectStatusBits(0x1f, set_bits)

#subwfb.size = 2


#def swapf(cpu, f, d, a):
    #"""Exchange nibbles in 'f'
    #cpu: core of PIC18F
    #f: part of argument register address
    #d: flag specifying direction of saving result (if d = 0 then result is saved in WREG else in register by address defined 'f')
    #a: flag specifying register address (if a = 1 then address is defined with BSR else fast access bank is used)
    #"""
    #if a == 1:
        #argAddr = (cpu.bsr << 8) | f
    #else:
        #argAddr = f if f < 0x80 else (0xf00 | f)
    #resAddr = WREG if d == 0 else argAddr

    #arg = cpu.data[argAddr]
    #nibble1, nibble2 = arg & 0xf, (arg & 0xf0) >> 4
    #cpu.data[resAddr] = (nibble1 << 4) | nibble2

#swapf.size = 2


#def tstfsz(cpu, f, a):
    #"""Test 'f', skip next instruction if it's equal 0
    #cpu: core of PIC18F
    #f: part of argument register address
    #a: flag specifying register address (if a = 1 then address is defined with BSR else fast access bank is used)
    #"""
    #if a == 1:
        #argAddr = (cpu.bsr << 8) | f
    #else:
        #argAddr = f if f < 0x80 else (0xf00 | f)
    #if cpu.data[argAddr] == 0:
        #cpu.incPC(2)

#tstfsz.size = 2


#def xorwf(cpu, f, d, a):
    #"""Logical exclusive OR between WREG and 'f'
    #Flags Z and N are affected
    #f: part of argument register address
    #d: flag specifying direction of saving result (if d = 0 then result is saved in WREG else in register by address defined 'f')
    #a: flag specifying register address (if a = 1 then address is defined with BSR else fast access bank is used)
    #"""
    #if a == 1:
        #argAddr = (cpu.bsr << 8) | f
    #else:
        #argAddr = f if f < 0x80 else (0xf00 | f)
    #resAddr = argAddr if d == 1 else WREG
    #_xor(cpu, resAddr, pic.wreg, pic.data[argAddr])

#xorwf.size = 2


###################################################
## Bit oriented operations with registries
###################################################
#def bcf(cpu, f, b, a):
    #"""Reset bit in 'f'
    #cpu: core of PIC18F
    #f: part of argument register address
    #b: number of bit to be reset
    #a: flag specifying register address (if a = 1 then address is defined with BSR else fast access bank is used)
    #"""
    #if a == 1:
        #argAddr = (cpu.bsr << 8) | f
    #else:
        #argAddr = f if f < 0x80 else (0xf00 | f)
    #cpu.data[argAddr] &= ~(1 << b)

#bcf.size = 2


#def bsf(cpu, f, b, a):
    #"""Set bit in 'f'
    #cpu: core of PIC18F
    #f: part of argument register address
    #b: number of bit to be set
    #a: flag specifying register address (if a = 1 then address is defined with BSR else fast access bank is used)
    #"""
    #if a == 1:
        #argAddr = (cpu.bsr << 8) | f
    #else:
        #argAddr = f if f < 0x80 else (0xf00 | f)
    #cpu.data[argAddr] |= (1 << b)

#bsf.size = 2


#def btfsc(cpu, f, b, a):
    #"""Test bit; skip next instruction if it's equal '0'
    #cpu: core of PIC18F
    #f: part of argument register address
    #b: number of bit for testing
    #a: flag specifying register address (if a = 1 then address is defined with BSR else fast access bank is used)
    #"""
    #if a == 1:
        #argAddr = (cpu.bsr << 8) | f
    #else:
        #argAddr = f if f < 0x80 else (0xf00 | f)
    #bit = (cpu.data[argAddr] >> b) & 0x01
    #if bit == 0:
        #cpu.incPC(2)

#btfsc.size = 2


#def btfss(cpu, f, b, a):
    #"""Test bit; skip next instruction if it's equal '1'
    #cpu: core of PIC18F
    #f: part of argument register address
    #b: number of bit for testing
    #a: flag specifying register address (if a = 1 then address is defined with BSR else fast access bank is used)
    #"""
    #if a == 1:
        #argAddr = (cpu.bsr << 8) | f
    #else:
        #argAddr = f if f < 0x80 else (0xf00 | f)
    #bit = (cpu.data[argAddr] >> b) & 0x01
    #if bit == 1:
        #cpu.incPC(2)

#btfss.size = 2


#def btg(cpu, f, b, a):
    #"""Inverse bit in 'f'
    #cpu: core of PIC18F
    #f: part of argument register address
    #b: number of bit for testing
    #a: flag specifying register address (if a = 1 then address is defined with BSR else fast access bank is used)
    #"""
    #if a == 1:
        #argAddr = (cpu.bsr << 8) | f
    #else:
        #argAddr = f if f < 0x80 else (0xf00 | f)
    #arg = cpu.data[argAddr]
    #cpu.data[argAddr] = (arg | (1 << b)) & ~(arg & (1 << b))

#btg.size = 2


##############################################
## Control instructions
##############################################
#def bc(cpu, n):
    #"""Branch if carry
    #cpu: core of PIC18F
    #n: number of jumps (instructions in both directions)
    #"""
    #if (cpu.status & C) > 0:
        #cpu.incPC(2*n)

#bc.size = 2


#def bn(cpu, n):
    #"""Branch if negative result
    #cpu: core of PIC18F
    #n: number of jumps (instructions in both directions)
    #"""
    #if (cpu.status & N) > 0:
        #cpu.incPC(2*n)

#bn.size = 2


#def bnc(cpu, n):
    #"""Branch if not carry
    #cpu: core of PIC18F
    #n: number of jumps (instructions in both directions)
    #"""
    #if (cpu.status & C) == 0:
        #cpu.incPC(2*n)

#bnc.size = 2


#def bnn(cpu, n):
    #"""Branch if not negative result
    #cpu: core of PIC18F
    #n: number of jumps (instructions in both directions)
    #"""
    #if (cpu.status & N) == 0:
        #cpu.incPC(2*n)

#bnn.size = 2


#def bnov(cpu, n):
    #"""Branch if not overflow
    #cpu: core of PIC18F
    #n: number of jumps (instructions in both directions)
    #"""
    #if (cpu.status & OV) == 0:
        #cpu.incPC(2*n)

#bnov.size = 2


#def bnz(cpu, n):
    #"""Branch if not zero
    #cpu: core of PIC18F
    #n: number of jumps (instructions in both directions)
    #"""
    #if (cpu.status & Z) == 0:
        #cpu.incPC(2*n)

#bnz.size = 2


#def bov(cpu, n):
    #"""Branch if overflow
    #cpu: core of PIC18F
    #n: number of jumps (instructions in both directions)
    #"""
    #if (cpu.status & OV) > 0:
        #cpu.incPC(2*n)

#bov.size = 2


#def bra(cpu, n):
    #"""Unconditional branch
    #cpu: core of PIC18F
    #n: number of jumps (instructions in both directions)
    #"""
    #cpu.incPC(2*n)

#bra.size = 2


#def bz(cpu, n):
    #"""Branch if zero
    #cpu: core of PIC18F
    #n: number of jumps (instructions in both directions)
    #"""
    #if (cpu.status & Z) > 0:
        #cpu.incPC(2*n)

#bz.size = 2


#def call(cpu, n, s):
    #"""Goto subroutine in all range of memory:
        #* return address (PC + 4) is saved in stack
        #* if s = 1 then WREG, STATUS, BSR is saved in fast access registers
        #* PC<20:1> is uploaded into the stack
    #"""
    #pass

#call.size = 4


#def clrwdt(cpu):
    #"""Reset watcdog"""
    #pass

#def daw(cpu):
    #"""Decimal correction of WREG"""
    #pass

#def goto(cpu, n):
    #"""Goto to address"""
    #pass

#def nop(cpu):
    #"""No operation"""
    #pass

#def pop(cpu):
    #"""Read the top of stack TOS"""
    #pass

#def push(cpu):
    #"""Record into the top of stack TOS"""
    #pass

#def rcall(cpu, n):
    #"""Short branch to subroutine"""
    #pass

#def reset(cpu):
    #"""Program reset"""
    #pass

#def retfie(cpu, s):
    #"""Return from subroutine with permit of interruption"""
    #pass

#def retlw(cpu, k):
    #"""Return from subroutine with loading of WREG"""
    #pass

#def return_(cpu, s):
    #"""Return from subroutine"""
    #pass

#def sleep(cpu):
    #"""Goto sleep mode"""
    #pass

#############################################
## Operations with constants
#############################################
#def addlw(cpu, k):
    #"""Add WREG with constant 'k'
    #affect C, DC, Z, OV, N
    #cpu: core of PIC18F
    #k: constant value to be added
    #"""
    #_add(cpu, WREG, pic.wreg, k)

#addlw.size = 2

#def andlw(cpu, k):
    #"""Logical conjunction WREG with constant 'k'
    #affect Z and N
    #cpu: core of PIC18F
    #k: constant value
    #"""
    #_and(cpu, WREG, pic.wreg, k)

#def iorlw(cpu, k):
    #"""Logical disjunction WREG with constant 'k'
    #affect Z and N
    #cpu: core of PIC18F
    #k: constant value
    #"""
    #_ior(cpu, WREG, pic.wreg, k)

#def lfsr(cpu, f, k):
    #"""Put constant value (12 bit) to FSR (2 words)
    #cpu: core of PIC18F
    #f: number of FSR register (0-3)
    #k: constant value (12 bit)
    #"""
    #if f == 0:
        #cpu.fsr0l = k & 0xff
        #cpu.fsr0h = (k & 0x0f00) >> 8
    #elif f == 1:
        #cpu.fsr1l = k & 0xff
        #cpu.fsr1h = (k & 0x0f00) >> 8
    #elif f == 2:
        #cpu.fsr2l = k & 0xff
        #cpu.fsr2h = (k & 0x0f00) >> 8

#def movlb(cpu, k):
    #"""Move constant value to BSR<3:0>
    #cpu: core of PIC18F
    #k: constant value (0-0x0f)
    #"""
    #cpu.bsr = k

#def movlw(cpu, k):
    #"""Move constant to WREG
    #cpu: core of PIC18F
    #k: constant value
    #"""
    #cpu.wreg = k

#def mullw(cpu, k):
    #"""Multiplication constant value with WREG
    #cpu: core of PIC18F
    #k: constant value
    #"""
    #result = cpu.wreg * k
    #cpu.prodl = result & 0xff
    #cpu.prodh = (result & 0xff00) >> 8

#def retlw(cpu, k):
    #"""Return from subroutine with loading WREG
    #cpu: core of PIC18F
    #k: constant value
    #"""
    #pass

#def sublw(cpu, k):
    #"""Substitute WREG from constant value
    #affect C, DC, Z, OV, N flags
    #cpu: core of PIC18F
    #k: constant value
    #"""
    #arg = (~cpu.wreg + 1) & 0xff
    #result = k + arg

    #set_bits = 0
    #if result & 0x100 > 0:
        #set_bits |= C
    #if ((k & 0xf) + (arg & 0xf)) & 0x10 > 0:
        #set_bits |= DC
    #if result & 0xff == 0:
        #set_bits |= Z
    #if (k & 0x80 == arg & 0x80) and (arg & 0x80 != result & 0x80):
        #set_bits |= OV
    #if result & 0x80 > 0:
        #set_bits |= N

    #cpu.wreg = result & 0xff
    #cpu.affectStatusBits(0x1f, set_bits)

#def xorlw(cpu, k):
    #"""Logical exclusive dijunction between constant and WREG
    #affect Z and N flags
    #cpu: core of PIC18F
    #k: constant value
    #"""
    #_xor(cpu, WREG, pic.wreg, k)
    
##############################################
## Operations: data memory <-> program memory
##############################################

#def tblrd_ask(cpu):
    #"""Table read"""
    #pass

#def tblrd_ask_plus(cpu):
    #"""Table read with post-increment"""
    #pass

#def tblrd_ask_minus(cpu):
    #"""Table read with post-decrement"""
    #pass

#def tblrd_plus_ask(cpu):
    #"""Table read with pred-increment"""
    #pass

#def tblwt_ask(cpu):
    #"""Table write"""
    #pass

#def tblwt_ask_plus(cpu):
    #"""Table write with post-increment"""
    #pass

#def tblwt_ask_minus(cpu):
    #"""Table write with post-decrement"""
    #pass

#def tblwt_plus_ask(cpu):
    #"""Table write with pred-increment"""
    #pass
