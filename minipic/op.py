import picmicro

def _operand_reg(cpu, f, a):
    if a == 1:
        addr = (cpu.data[BSR].get() << 8) | f
    else:
        addr = f if f < 0x80 else (0x0f00 | f)
    return cpu.data[addr]

class Op:
    """ Abstract class of operation of MC """
    SIZE = 2
    def execute(self, cpu):
        raise NotImplementedError()

class NOP(Op):
    """ No operation """
    def execute(self, cpu):
        pass

class MOVLW(Op):
    """ Move constant to WREG """
    def __init__(self, k):
        self.k = k
    def execute(self, cpu):
        cpu.data[picmicro.WREG].put(self.k)

class MOVWF(Op):
    """ Mov WREG to 'f' """
    def __init__(self, f, a):
        self.f = f
        self.a = a
    def execute(self, cpu):
        wreg_value = cpu.data[picmicro.WREG].get()
        dest = _operand_reg(cpu, self.f, self.a)
        dest.put(wreg_value) 

class BTG(Op):
    """ Inverse bit in 'f' """
    def __init__(self, f, b, a):
        self.f = f
        self.b = b
        self.a = a
    def execute(self, cpu):
        reg = _operand_reg(cpu, self.f, self.a)
        reg[self.a] ^= 1

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





















# bitmasks of flags
#N, OV, Z, DC, C = 0b10000, 0b01000, 0b00100, 0b00010, 0b00001

#def _add(pic, resAddr, arg1, arg2):
    #"""Internal procedure that performs addition 'arg1' and 'arg2' and saving result by address 'resAddr'
    #This operation affects C, DC, Z, OV, N flags
    #pic: core of PIC18F
    #resAddr: address of saving result
    #arg1: first argument of operation
    #arg2: second argument of operation
    #"""
    #result = arg1 + arg2

    #carry = (result & 0x100) >> 8
    #set_bits = carry
    #decCarry = (((arg1 & 0xf) + (arg2 & 0xf)) & 0x10) >> 4
    #set_bits |= decCarry << 1
    #if result & 0xff == 0:
        #set_bits |= Z
    #signCarry = (((arg1 & 0x7f) + (arg2 & 0x7f)) & 0x80) >> 7
    #set_bits |= (signCarry ^ carry) << 3
    #sign = (result & 0x80) >> 7
    #set_bits |= sign << 4

    #pic.data[resAddr] = result & 0xff
    #pic.affectStatusBits(0x1f, set_bits)

#def _and(pic, resAddr, arg1, arg2):
    #"""Internal procedure that performs bitwise conjuction 'arg1' with 'arg2' and saving result by address 'resAddr'
    #This operation affects Z and N flags
    #pic: core of PIC18F
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
    #pic.data[resAddr] = result
    #pic.affectStatusBits(N | Z, set_bits)

#def _ior(pic, resAddr, arg1, arg2):
    #"""Internal procedure for bitwise disjunction between 'arg1' and 'arg2' and saving result by address 'resAddr'
    #This operation affects Z and N flags
    #pic: core of PIC18F
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
    #pic.data[resAddr] = result
    #pic.affectStatusBits(N | Z, set_bits)

#def _xor(pic, resAddr, arg1, arg2):
    #"""Internal procedure for exclusive disjunction between 'arg1' and 'arg2' and saving result in memory cell by address 'resAddr'
    #This operation affects Z and N flags
    #pic: core of PIC18F
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
    #pic.data[resAddr] = result
    #pic.affectStatusBits(N | Z, set_bits)

#########################################
## Byte oriented commands with registers
#########################################
#def addwf(pic, f, d, a):
    #"""Add WREG with 'f'
    #affect C, DC, Z, OV, N
    #pic: core of PIC18F
    #f: part of register address of second term of sum
    #d: flag specifying direction of saving result (if d = 0 then result is saved in WREG else in register by address defined 'f')
    #a: flag specifying address of second term of sum (if a = 1 then address defined BSR else fast access bank is used)
    #"""
    #if a == 1:
        #argAddr = (pic.bsr << 8) | f
    #else:
        #argAddr = f if f < 0x80 else (0xf00 | f)
    #resAddr = argAddr if d == 1 else WREG
    #_add(pic, resAddr, pic.wreg, pic.data[argAddr])

#addwf.size = 2


#def addwfc(pic, f, d, a):
    #"""Add WREG with 'f' and with bit C
    #affect C, DC, Z, OV, N
    #pic: core of PIC18F
    #f: part of register address of second term of sum
    #d: flag specifying direction of saving result (if d = 0 then result is saved in WREG else in register by address defined 'f')
    #a: flag specifying address of second term of sum (if a = 1 then address defined BSR else fast access bank is used)
    #"""
    #if a == 1:
        #argAddr = (pic.bsr << 8) | f
    #else:
        #argAddr = f if f < 0x80 else (0xf00 | f)
    #carryFlag = pic.status & C
    #arg1, arg2 = pic.wreg, pic.data[argAddr]
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
    #pic.data[resAddr] = result & 0xff
    #pic.affectStatusBits(0x1f, set_bits)
 
#addwfc.size = 2


#def andwf(pic, f, d, a):
    #"""Conjunction between WREG and 'f'
    #affect Z, N
    #pic: core of PIC18F
    #f: part of register address of second term of conjunction
    #d: flag specifying direction of saving result (if d = 0 then result is saved in WREG else in register by address defined 'f')
    #a: flag specifying address of second term of conjuction (if a = 1 then address defined BSR else fast access bank is used)
    #"""
    #if a == 1:
        #argAddr = (pic.bsr << 8) | f
    #else:
        #argAddr = f if f < 0x80 else (0xf00 | f)
    #resAddr = WREG if d == 0 else argAddr
    #_and(pic, resAddr, pic.wreg, pic.data[argAddr]) 
    
#andwf.size = 2


#def clrf(pic, f, a):
    #"""Clear register 'f'
    #affect Z
    #pic: core of PIC18F
    #f: part of register address
    #a: flag specifying register address (if a = 1 then address defined BSR else fast access bank is used)
    #"""
    #if a == 1:
        #argAddr = (pic.bsr << 8) | f
    #else:
        #argAddr = f if f < 0x80 else (0xf00 | f)
    #pic.data[argAddr] = 0
    #pic.affectStatusBits(Z, Z)

#clrf.size = 2


#def comf(pic, f, d, a):
    #"""Inverse register 'f'
    #affect Z, N
    #pic: core of PIC18F
    #f: part of register address
    #d: flag specifying direction of saving result (if d = 0 then result is saved in WREG else in register by address defined 'f')
    #a: flag specifying register address (if a = 1 then address is defined with BSR else fast access bank is used)
    #"""
    #if a == 1:
        #argAddr = (pic.bsr << 8) | f
    #else:
        #argAddr = f if f < 0x80 else (0xf00 | f)
    #resAddr = WREG if d == 0 else argAddr

    #result = ~pic.data[argAddr] & 0xff
    #set_bits = 0
    #if result == 0:
        #set_bits |= Z
    #if result & 0x80 > 0:
        #set_bits |= N
    #pic.data[resAddr] = result
    #pic.affectStatusBits(N | Z, set_bits)

#comf.size = 2


#def cpfseq(pic, f, a):
    #"""Compare WREG and 'f'; skip next instuction if they are equal
    #pic: core of PIC18F
    #f: part of register address
    #a: flag specifying register address (if a = 1 then address is defined with BSR else fast access bank is used)
    #"""
    #if a == 1:
        #argAddr = (pic.bsr << 8) | f
    #else:
        #argAddr = f if f < 0x80 else (0xf00 | f)
    #if pic.data[argAddr] == pic.wreg:
        #pic.incPC(2)

#cpfseq.size = 2


#def cpfsgt(pic, f, a):
    #"""Compare WREG and 'f'; if WREG > 'f' then skip next instruction
    #pic: core of PIC18F
    #f: part of register address
    #a: flag specifying register address (if a = 1 then address is defined with BSR else fast access bank is used)
    #"""
    #if a == 1:
        #argAddr = (pic.bsr << 8) | f
    #else:
        #argAddr = f if f < 0x80 else (0xf00 | f)
    #if pic.data[argAddr] < pic.wreg:
        #pic.incPC(2)

#cpfsgt.size = 2


#def cpfslt(pic,f, a):
    #"""Compare WREG and 'f'; if WREG < 'f' then skip next instruction
    #pic: core of PIC18F
    #f: part of register address
    #a: flag specifying register address (if a = 1 then address is defined with BSR else fast access bank is used)
    #"""
    #if a == 1:
        #argAddr = (pic.bsr << 8) | f
    #else:
        #argAddr = f if f < 0x80 else (0xf00 | f)
    #if pic.data[argAddr] > pic.wreg:
        #pic.incPC(2)

#cpfslt.size = 2


#def decf(pic, f, d, a):
    #"""Decrement 'f'
    #affect C, DC, Z, OV, N flags
    #pic: core of PIC18F
    #f: part of argument register address
    #d: flag specifying direction of saving result (if d = 0 then result is saved in WREG else in register by address defined 'f')
    #a: flag specifying register address (if a = 1 then address is defined with BSR else fast access bank is used)
    #"""
    #if a == 1:
        #argAddr = (pic.bsr << 8) | f
    #else:
        #argAddr = f if f < 0x80 else (0xf00 | f)
    #resAddr = WREG if d == 0 else argAddr

    #arg = pic.data[argAddr]
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
    #pic.data[resAddr] = result & 0xff
    #pic.affectStatusBits(0x1f, set_bits)

#decf.size = 2


#def decfsz(pic, f, d, a):
    #"""Decrement 'f'; skip next instruction if result is equal zero
    #pic: core of PIC18F
    #f: part of argument register address
    #d: flag specifying direction of saving result (if d = 0 then result is saved in WREG else in register by address defined 'f')
    #a: flag specifying register address (if a = 1 then address is defined with BSR else fast access bank is used)
    #"""
    #if a == 1:
        #argAddr = (pic.bsr << 8) | f
    #else:
        #argAddr = f if f < 0x80 else (0xf00 | f)
    #resAddr = WREG if d == 0 else argAddr

    #result = pic.data[argAddr] - 1
    #if result == 0:
        #pic.incPC(2)
    #pic.data[resAddr] = result & 0xff

#decf.size = 2


#def dcfsnz(pic, f, d, a):
    #"""Decrement 'f'; skip next instruction if result is not equal zero
    #pic: core of PIC18F
    #f: part of argument register address
    #d: flag specifying direction of saving result (if d = 0 then result is saved in WREG else in register by address defined 'f')
    #a: flag specifying register address (if a = 1 then address is defined with BSR else fast access bank is used)
    #"""
    #if a == 1:
        #argAddr = (pic.bsr << 8) | f
    #else:
        #argAddr = f if f < 0x80 else (0xf00 | f)
    #resAddr = WREG if d == 0 else argAddr

    #result = pic.data[argAddr] - 1
    #if result != 0:
        #pic.incPC(2)
    #pic.data[resAddr] = result & 0xff

#dcfsnz.size = 2


#def incf(pic, f, d, a):
    #"""Increment 'f'
    #affect C, DC, Z, OV, N flags
    #pic: core of PIC18F
    #f: part of argument register address
    #d: flag specifying direction of saving result (if d = 0 then result is saved in WREG else in register by address defined 'f')
    #a: flag specifying register address (if a = 1 then address is defined with BSR else fast access bank is used)
    #"""
    #if a == 1:
        #argAddr = (pic.bsr << 8) | f
    #else:
        #argAddr = f if f < 0x80 else (0xf00 | f)
    #resAddr = WREG if d == 0 else argAddr

    #arg = pic.data[argAddr]
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
    #pic.data[resAddr] = result & 0xff
    #pic.affectStatusBits(0x1f, set_bits)

#incf.size = 2


#def incfsz(pic, f, d, a):
    #"""Increment 'f'; skip next instruction if result is equal zero
    #pic: core of PIC18F
    #f: part of argument register address
    #d: flag specifying direction of saving result (if d = 0 then result is saved in WREG else in register by address defined 'f')
    #a: flag specifying register address (if a = 1 then address is defined with BSR else fast access bank is used)
    #"""
    #if a == 1:
        #argAddr = (pic.bsr << 8) | f
    #else:
        #argAddr = f if f < 0x80 else (0xf00 | f)
    #resAddr = WREG if d == 0 else argAddr

    #result = (pic.data[argAddr] + 1) & 0xff
    #if result == 0:
        #pic.incPC(2)
    #pic.data[resAddr] = result

#incfsz.size = 2


#def infsnz(pic, f, d, a):
    #"""Increment 'f'; skip next instruction if result is not equal zero
    #pic: core of PIC18F
    #f: part of argument register address
    #d: flag specifying direction of saving result (if d = 0 then result is saved in WREG else in register by address defined 'f')
    #a: flag specifying register address (if a = 1 then address is defined with BSR else fast access bank is used)
    #"""
    #if a == 1:
        #argAddr = (pic.bsr << 8) | f
    #else:
        #argAddr = f if f < 0x80 else (0xf00 | f)
    #resAddr = WREG if d == 0 else argAddr

    #result = (pic.data[argAddr] + 1) & 0xff
    #if result != 0:
        #pic.incPC(2)
    #pic.data[resAddr] = result

#infsnz.size = 2


#def iorwf(pic, f, d, a):
    #"""Logic disjunction between WREG and 'f';
    #Flags Z and N are affected
    #pic: core of PIC18F
    #f: part of argument register address
    #d: flag specifying direction of saving result (if d = 0 then result is saved in WREG else in register by address defined 'f')
    #a: flag specifying register address (if a = 1 then address is defined with BSR else fast access bank is used)
    #"""
    #if a == 1:
        #argAddr = (pic.bsr << 8) | f
    #else:
        #argAddr = f if f < 0x80 else (0xf00 | f)
    #resAddr = WREG if d == 0 else argAddr
    #_ior(pic, resAddr, pic.wreg, pic.data[argAddr])

#iorwf.size = 2


#def movf(pic, f, d, a):
    #"""Move 'f'
    #Flags Z and N are affected
    #pic: core of PIC18F
    #f: part of argument register address
    #d: flag specifying direction of saving result (if d = 0 then result is saved in WREG else in register by address defined 'f')
    #a: flag specifying register address (if a = 1 then address is defined with BSR else fast access bank is used)
    #"""
    #if a == 1:
        #argAddr = (pic.bsr << 8) | f
    #else:
        #argAddr = f if f < 0x80 else (0xf00 | f)
    #resAddr = WREG if d == 0 else argAddr
    #pic.data[resAddr] = pic.data[argAddr]

#movf.size = 2


#def movff(pic, fs, fd):
    #"""Move source 'fs' to destination 'fd'
    #pic: core of PIC18F
    #fs: address of source
    #fd: address of destination
    #"""
    #assert fs != PCL and fs != TOSU and fs != TOSH and fs != TOSL
    #pic.data[fd] = pic.data[fs]

#movff.size = 4


#def movwf(pic, f, a):
    #"""Move WREG to 'f'
    #pic: core of PIC18F
    #f: part of argument register address
    #a: flag specifying register address (if a = 1 then address is defined with BSR else fast access bank is used)
    #"""
    #if a == 1:
        #argAddr = (pic.bsr << 8) | f
    #else:
        #argAddr = f if f < 0x80 else (0xf00 | f)
    #pic.data[argAddr] = pic.wreg

#movwf.size = 2


#def mulwf(pic, f, a):
    #"""Multiply WREG and 'f'
    #pic: core of PIC18F
    #f: part of argument register address
    #a: flag specifying register address (if a = 1 then address is defined with BSR else fast access bank is used)
    #"""
    #if a == 1:
        #argAddr = (pic.bsr << 8) | f
    #else:
        #argAddr = f if f < 0x80 else (0xf00 | f)
    #result = pic.wreg * pic.data[argAddr]
    #pic.prodl = result & 0xff
    #pic.prodh = (result & 0xff00) >> 8

#mulwf.size = 2


#def negf(pic, f, a):
    #"""Negative value of 'f'
    #Flags C, DC, Z, OV, N are affected
    #pic: core of PIC18F
    #f: part of argument register address
    #a: flag specifying register address (if a = 1 then address is defined with BSR else fast access bank is used)
    #"""
    #if a == 1:
        #argAddr = (pic.bsr << 8) | f
    #else:
        #argAddr = f if f < 0x80 else (0xf00 | f)

    #result = (~pic.data[argAddr] + 1) & 0xff
    #set_bits = 0
    #if result & 0x80 > 0:
        #set_bits |= N
    #if result == 0:
        #set_bits |= (C | Z)
    #if result & 0xf == 0:
        #set_bits |= DC
    #if result == 0x80:
        #set_bits |= OV
    #pic.data[argAddr] = result
    #pic.affectStatusBits(0x1f, set_bits)

#negf.size = 2


#def rlcf(pic, f, d, a):
    #"""Left shift with carry
    #Flags C, Z, N are affects
    #pic: core of PIC18F
    #f: part of argument register address
    #d: flag specifying direction of saving result (if d = 0 then result is saved in WREG else in register by address defined 'f')
    #a: flag specifying register address (if a = 1 then address is defined with BSR else fast access bank is used)
    #"""
    #if a == 1:
        #argAddr = (pic.bsr << 8) | f
    #else:
        #argAddr = f if f < 0x80 else (0xf00 | f)
    #resAddr = WREG if d == 0 else argAddr

    #result = pic.data[argAddr] << 1
    #result |= pic.status & C
    #set_bits = (result & 0x100) >> 8
    #if result & 0xff == 0:
        #set_bits |= Z
    #if result & 0x80 > 0:
        #set_bits |= N

    #pic.data[resAddr] = result & 0xff
    #pic.affectStatusBits(C | Z | N, set_bits)

#rlcf.size = 2


#def rlncf(pic, f, d, a):
    #"""Left shift without carry
    #Flags Z, N are affects
    #pic: core of PIC18F
    #f: part of argument register address
    #d: flag specifying direction of saving result (if d = 0 then result is saved in WREG else in register by address defined 'f')
    #a: flag specifying register address (if a = 1 then address is defined with BSR else fast access bank is used)
    #"""
    #if a == 1:
        #argAddr = (pic.bsr << 8) | f
    #else:
        #argAddr = f if f < 0x80 else (0xf00 | f)
    #resAddr = WREG if d == 0 else argAddr

    #result = pic.data[argAddr] << 1
    #result |= (result >> 8)
    #set_bits = 0
    #if result & 0xff == 0:
        #set_bits |= Z
    #if result & 0x80 > 0:
        #set_bits |= N

    #pic.data[resAddr] = result & 0xff
    #pic.affectStatusBits(Z | N, set_bits)

#rlncf.size = 2


#def rrcf(pic, f, d, a):
    #"""Right shift with carry
    #Flags C, Z, N are affects
    #pic: core of PIC18F
    #f: part of argument register address
    #d: flag specifying direction of saving result (if d = 0 then result is saved in WREG else in register by address defined 'f')
    #a: flag specifying register address (if a = 1 then address is defined with BSR else fast access bank is used)
    #"""
    #if a == 1:
        #argAddr = (pic.bsr << 8) | f
    #else:
        #argAddr = f if f < 0x80 else (0xf00 | f)
    #resAddr = WREG if d == 0 else argAddr

    #arg = pic.data[argAddr]
    #set_bits = arg & 0x1
    #result = (arg >> 1) | ((pic.status & C) << 7)
    #if result & 0xff == 0:
        #set_bits |= Z
    #if result & 0x80 > 0:
        #set_bits |= N

    #pic.data[resAddr] = result
    #pic.affectStatusBits(C | Z | N, set_bits)

#rrcf.size = 2


#def rrncf(pic, f, d, a):
    #"""Right shift without carry
    #Flags Z, N are affects
    #pic: core of PIC18F
    #f: part of argument register address
    #d: flag specifying direction of saving result (if d = 0 then result is saved in WREG else in register by address defined 'f')
    #a: flag specifying register address (if a = 1 then address is defined with BSR else fast access bank is used)
    #"""
    #if a == 1:
        #argAddr = (pic.bsr << 8) | f
    #else:
        #argAddr = f if f < 0x80 else (0xf00 | f)
    #resAddr = WREG if d == 0 else argAddr

    #arg = pic.data[argAddr]
    #arg |= ((arg & 0b1) << 8)
    #result = arg >> 1
    #set_bits = 0
    #if result & 0xff == 0:
        #set_bits |= Z
    #if result & 0x80 > 0:
        #set_bits |= N

    #pic.data[resAddr] = result
    #pic.affectStatusBits(Z | N, set_bits)

#rrncf.size = 2


#def setf(pic, f, a):
    #"""Set all bits of 'f'
    #pic: core of PIC18F
    #f: part of argument register address
    #a: flag specifying register address (if a = 1 then address is defined with BSR else fast access bank is used)
    #"""
    #if a == 1:
        #argAddr = (pic.bsr << 8) | f
    #else:
        #argAddr = f if f < 0x80 else (0xf00 | f)
    #pic.data[argAddr] = 0xff

#setf.size = 2


#def subfwb(pic, f, d, a):
    #"""Substitute 'f' from WREG with borrow
    #Flags Z, N, OV, DC, C are affects
    #pic: core of PIC18F
    #f: part of argument register address
    #d: flag specifying direction of saving result (if d = 0 then result is saved in WREG else in register by address defined 'f')
    #a: flag specifying register address (if a = 1 then address is defined with BSR else fast access bank is used)
    #"""
    #if a == 1:
        #argAddr = (pic.bsr << 8) | f
    #else:
        #argAddr = f if f < 0x80 else (0xf00 | f)
    #resAddr = WREG if d == 0 else argAddr

    #arg1 = pic.wreg
    #arg2 = (-pic.data[argAddr]) & 0xff
    #arg3 = 0 if (pic.status & C == 1) else 0xff
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

    #pic.data[resAddr] = result & 0xff
    #pic.affectStatusBits(0x1f, set_bits)

#subfwb.size = 2


#def subwf(pic, f, d, a):
    #"""Substitute WREG from 'f'
    #Flags Z, N, OV, DC, C are affects
    #pic: core of PIC18F
    #f: part of argument register address
    #d: flag specifying direction of saving result (if d = 0 then result is saved in WREG else in register by address defined 'f')
    #a: flag specifying register address (if a = 1 then address is defined with BSR else fast access bank is used)
    #"""
    #if a == 1:
        #argAddr = (pic.bsr << 8) | f
    #else:
        #argAddr = f if f < 0x80 else (0xf00 | f)
    #resAddr = WREG if d == 0 else argAddr

    #arg1, arg2 = pic.data[argAddr], (~pic.wreg + 1) & 0xff
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

    #pic.data[resAddr] = result & 0xff
    #pic.affectStatusBits(0x1f, set_bits)

#subwf.size = 2


#def subwfb(pic, f, d, a):
    #"""Substitute WREG from 'f' with borrow
    #Flags Z, N, OV, DC, C are affects
    #pic: core of PIC18F
    #f: part of argument register address
    #d: flag specifying direction of saving result (if d = 0 then result is saved in WREG else in register by address defined 'f')
    #a: flag specifying register address (if a = 1 then address is defined with BSR else fast access bank is used)
    #"""
    #if a == 1:
        #argAddr = (pic.bsr << 8) | f
    #else:
        #argAddr = f if f < 0x80 else (0xf00 | f)
    #resAddr = WREG if d == 0 else argAddr

    #arg1 = pic.data[argAddr]
    #arg2 = (-pic.wreg) & 0xff
    #arg3 = 0 if (pic.status & C == 1) else 0xff
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

    #pic.data[resAddr] = result & 0xff
    #pic.affectStatusBits(0x1f, set_bits)

#subwfb.size = 2


#def swapf(pic, f, d, a):
    #"""Exchange nibbles in 'f'
    #pic: core of PIC18F
    #f: part of argument register address
    #d: flag specifying direction of saving result (if d = 0 then result is saved in WREG else in register by address defined 'f')
    #a: flag specifying register address (if a = 1 then address is defined with BSR else fast access bank is used)
    #"""
    #if a == 1:
        #argAddr = (pic.bsr << 8) | f
    #else:
        #argAddr = f if f < 0x80 else (0xf00 | f)
    #resAddr = WREG if d == 0 else argAddr

    #arg = pic.data[argAddr]
    #nibble1, nibble2 = arg & 0xf, (arg & 0xf0) >> 4
    #pic.data[resAddr] = (nibble1 << 4) | nibble2

#swapf.size = 2


#def tstfsz(pic, f, a):
    #"""Test 'f', skip next instruction if it's equal 0
    #pic: core of PIC18F
    #f: part of argument register address
    #a: flag specifying register address (if a = 1 then address is defined with BSR else fast access bank is used)
    #"""
    #if a == 1:
        #argAddr = (pic.bsr << 8) | f
    #else:
        #argAddr = f if f < 0x80 else (0xf00 | f)
    #if pic.data[argAddr] == 0:
        #pic.incPC(2)

#tstfsz.size = 2


#def xorwf(pic, f, d, a):
    #"""Logical exclusive OR between WREG and 'f'
    #Flags Z and N are affected
    #f: part of argument register address
    #d: flag specifying direction of saving result (if d = 0 then result is saved in WREG else in register by address defined 'f')
    #a: flag specifying register address (if a = 1 then address is defined with BSR else fast access bank is used)
    #"""
    #if a == 1:
        #argAddr = (pic.bsr << 8) | f
    #else:
        #argAddr = f if f < 0x80 else (0xf00 | f)
    #resAddr = argAddr if d == 1 else WREG
    #_xor(pic, resAddr, pic.wreg, pic.data[argAddr])

#xorwf.size = 2


###################################################
## Bit oriented operations with registries
###################################################
#def bcf(pic, f, b, a):
    #"""Reset bit in 'f'
    #pic: core of PIC18F
    #f: part of argument register address
    #b: number of bit to be reset
    #a: flag specifying register address (if a = 1 then address is defined with BSR else fast access bank is used)
    #"""
    #if a == 1:
        #argAddr = (pic.bsr << 8) | f
    #else:
        #argAddr = f if f < 0x80 else (0xf00 | f)
    #pic.data[argAddr] &= ~(1 << b)

#bcf.size = 2


#def bsf(pic, f, b, a):
    #"""Set bit in 'f'
    #pic: core of PIC18F
    #f: part of argument register address
    #b: number of bit to be set
    #a: flag specifying register address (if a = 1 then address is defined with BSR else fast access bank is used)
    #"""
    #if a == 1:
        #argAddr = (pic.bsr << 8) | f
    #else:
        #argAddr = f if f < 0x80 else (0xf00 | f)
    #pic.data[argAddr] |= (1 << b)

#bsf.size = 2


#def btfsc(pic, f, b, a):
    #"""Test bit; skip next instruction if it's equal '0'
    #pic: core of PIC18F
    #f: part of argument register address
    #b: number of bit for testing
    #a: flag specifying register address (if a = 1 then address is defined with BSR else fast access bank is used)
    #"""
    #if a == 1:
        #argAddr = (pic.bsr << 8) | f
    #else:
        #argAddr = f if f < 0x80 else (0xf00 | f)
    #bit = (pic.data[argAddr] >> b) & 0x01
    #if bit == 0:
        #pic.incPC(2)

#btfsc.size = 2


#def btfss(pic, f, b, a):
    #"""Test bit; skip next instruction if it's equal '1'
    #pic: core of PIC18F
    #f: part of argument register address
    #b: number of bit for testing
    #a: flag specifying register address (if a = 1 then address is defined with BSR else fast access bank is used)
    #"""
    #if a == 1:
        #argAddr = (pic.bsr << 8) | f
    #else:
        #argAddr = f if f < 0x80 else (0xf00 | f)
    #bit = (pic.data[argAddr] >> b) & 0x01
    #if bit == 1:
        #pic.incPC(2)

#btfss.size = 2


#def btg(pic, f, b, a):
    #"""Inverse bit in 'f'
    #pic: core of PIC18F
    #f: part of argument register address
    #b: number of bit for testing
    #a: flag specifying register address (if a = 1 then address is defined with BSR else fast access bank is used)
    #"""
    #if a == 1:
        #argAddr = (pic.bsr << 8) | f
    #else:
        #argAddr = f if f < 0x80 else (0xf00 | f)
    #arg = pic.data[argAddr]
    #pic.data[argAddr] = (arg | (1 << b)) & ~(arg & (1 << b))

#btg.size = 2


##############################################
## Control instructions
##############################################
#def bc(pic, n):
    #"""Branch if carry
    #pic: core of PIC18F
    #n: number of jumps (instructions in both directions)
    #"""
    #if (pic.status & C) > 0:
        #pic.incPC(2*n)

#bc.size = 2


#def bn(pic, n):
    #"""Branch if negative result
    #pic: core of PIC18F
    #n: number of jumps (instructions in both directions)
    #"""
    #if (pic.status & N) > 0:
        #pic.incPC(2*n)

#bn.size = 2


#def bnc(pic, n):
    #"""Branch if not carry
    #pic: core of PIC18F
    #n: number of jumps (instructions in both directions)
    #"""
    #if (pic.status & C) == 0:
        #pic.incPC(2*n)

#bnc.size = 2


#def bnn(pic, n):
    #"""Branch if not negative result
    #pic: core of PIC18F
    #n: number of jumps (instructions in both directions)
    #"""
    #if (pic.status & N) == 0:
        #pic.incPC(2*n)

#bnn.size = 2


#def bnov(pic, n):
    #"""Branch if not overflow
    #pic: core of PIC18F
    #n: number of jumps (instructions in both directions)
    #"""
    #if (pic.status & OV) == 0:
        #pic.incPC(2*n)

#bnov.size = 2


#def bnz(pic, n):
    #"""Branch if not zero
    #pic: core of PIC18F
    #n: number of jumps (instructions in both directions)
    #"""
    #if (pic.status & Z) == 0:
        #pic.incPC(2*n)

#bnz.size = 2


#def bov(pic, n):
    #"""Branch if overflow
    #pic: core of PIC18F
    #n: number of jumps (instructions in both directions)
    #"""
    #if (pic.status & OV) > 0:
        #pic.incPC(2*n)

#bov.size = 2


#def bra(pic, n):
    #"""Unconditional branch
    #pic: core of PIC18F
    #n: number of jumps (instructions in both directions)
    #"""
    #pic.incPC(2*n)

#bra.size = 2


#def bz(pic, n):
    #"""Branch if zero
    #pic: core of PIC18F
    #n: number of jumps (instructions in both directions)
    #"""
    #if (pic.status & Z) > 0:
        #pic.incPC(2*n)

#bz.size = 2


#def call(pic, n, s):
    #"""Goto subroutine in all range of memory:
        #* return address (PC + 4) is saved in stack
        #* if s = 1 then WREG, STATUS, BSR is saved in fast access registers
        #* PC<20:1> is uploaded into the stack
    #"""
    #pass

#call.size = 4


#def clrwdt(pic):
    #"""Reset watcdog"""
    #pass

#def daw(pic):
    #"""Decimal correction of WREG"""
    #pass

#def goto(pic, n):
    #"""Goto to address"""
    #pass

#def nop(pic):
    #"""No operation"""
    #pass

#def pop(pic):
    #"""Read the top of stack TOS"""
    #pass

#def push(pic):
    #"""Record into the top of stack TOS"""
    #pass

#def rcall(pic, n):
    #"""Short branch to subroutine"""
    #pass

#def reset(pic):
    #"""Program reset"""
    #pass

#def retfie(pic, s):
    #"""Return from subroutine with permit of interruption"""
    #pass

#def retlw(pic, k):
    #"""Return from subroutine with loading of WREG"""
    #pass

#def return_(pic, s):
    #"""Return from subroutine"""
    #pass

#def sleep(pic):
    #"""Goto sleep mode"""
    #pass

#############################################
## Operations with constants
#############################################
#def addlw(pic, k):
    #"""Add WREG with constant 'k'
    #affect C, DC, Z, OV, N
    #pic: core of PIC18F
    #k: constant value to be added
    #"""
    #_add(pic, WREG, pic.wreg, k)

#addlw.size = 2

#def andlw(pic, k):
    #"""Logical conjunction WREG with constant 'k'
    #affect Z and N
    #pic: core of PIC18F
    #k: constant value
    #"""
    #_and(pic, WREG, pic.wreg, k)

#def iorlw(pic, k):
    #"""Logical disjunction WREG with constant 'k'
    #affect Z and N
    #pic: core of PIC18F
    #k: constant value
    #"""
    #_ior(pic, WREG, pic.wreg, k)

#def lfsr(pic, f, k):
    #"""Put constant value (12 bit) to FSR (2 words)
    #pic: core of PIC18F
    #f: number of FSR register (0-3)
    #k: constant value (12 bit)
    #"""
    #if f == 0:
        #pic.fsr0l = k & 0xff
        #pic.fsr0h = (k & 0x0f00) >> 8
    #elif f == 1:
        #pic.fsr1l = k & 0xff
        #pic.fsr1h = (k & 0x0f00) >> 8
    #elif f == 2:
        #pic.fsr2l = k & 0xff
        #pic.fsr2h = (k & 0x0f00) >> 8

#def movlb(pic, k):
    #"""Move constant value to BSR<3:0>
    #pic: core of PIC18F
    #k: constant value (0-0x0f)
    #"""
    #pic.bsr = k

#def movlw(pic, k):
    #"""Move constant to WREG
    #pic: core of PIC18F
    #k: constant value
    #"""
    #pic.wreg = k

#def mullw(pic, k):
    #"""Multiplication constant value with WREG
    #pic: core of PIC18F
    #k: constant value
    #"""
    #result = pic.wreg * k
    #pic.prodl = result & 0xff
    #pic.prodh = (result & 0xff00) >> 8

#def retlw(pic, k):
    #"""Return from subroutine with loading WREG
    #pic: core of PIC18F
    #k: constant value
    #"""
    #pass

#def sublw(pic, k):
    #"""Substitute WREG from constant value
    #affect C, DC, Z, OV, N flags
    #pic: core of PIC18F
    #k: constant value
    #"""
    #arg = (~pic.wreg + 1) & 0xff
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

    #pic.wreg = result & 0xff
    #pic.affectStatusBits(0x1f, set_bits)

#def xorlw(pic, k):
    #"""Logical exclusive dijunction between constant and WREG
    #affect Z and N flags
    #pic: core of PIC18F
    #k: constant value
    #"""
    #_xor(pic, WREG, pic.wreg, k)
    
##############################################
## Operations: data memory <-> program memory
##############################################

#def tblrd_ask(pic):
    #"""Table read"""
    #pass

#def tblrd_ask_plus(pic):
    #"""Table read with post-increment"""
    #pass

#def tblrd_ask_minus(pic):
    #"""Table read with post-decrement"""
    #pass

#def tblrd_plus_ask(pic):
    #"""Table read with pred-increment"""
    #pass

#def tblwt_ask(pic):
    #"""Table write"""
    #pass

#def tblwt_ask_plus(pic):
    #"""Table write with post-increment"""
    #pass

#def tblwt_ask_minus(pic):
    #"""Table write with post-decrement"""
    #pass

#def tblwt_plus_ask(pic):
    #"""Table write with pred-increment"""
    #pass
