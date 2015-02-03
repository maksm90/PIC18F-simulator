import picmicro

# bitmasks of flags
N, OV, Z, DC, C = 0b10000, 0b01000, 0b00100, 0b00010, 0b00001

def _add(pic, addr, value):
    """Internal procedure for addition two byte values and saving result by address 'addr'.
    This operation affects C, DC, Z, OV, N flags
    pic: core of PIC18F
    addr: address of first argument and result cell
    value: byte value to be added
    """
    arg1, arg2 = pic.data[addr], value
    result = arg1 + arg2

    set_bits = 0
    if result & 0x100 > 0:
        set_bits |= C
    if ((arg1 & 0xf) + (arg2 & 0xf)) & 0x10 > 0:
        set_bits |= DC
    if result & 0xff == 0:
        set_bits |= Z
    if (arg1 & 0x80 == arg2 & 0x80) and (arg1 & 0x80 != result & 0x80):
        set_bits |= OV
    if result & 0x80 > 0:
        set_bits |= N

    pic.data[addr] = result & 0xff
    pic.affectStatusBits(0x1f, set_bits)

def _and(pic, addr, value):
    """Internal procedure for doing bitwise conjuction of content of cell by address 'addr' and byte value 'value' and saving result into the cell
    This operation affects Z and N flags
    pic: core of PIC18F
    addr: address of first argument of conjuction
    value: byte value
    """
    result = pic.data[addr] & value
    set_bits = 0
    if result == 0:
        set_bits |= Z
    if result & 0x80 > 0:
        set_bits |= N
    pic.data[addr] = result
    pic.affectStatusBits(N | Z, set_bits)

def _ior(pic, addr, value):
    """Internal procedure for bitwise disjunction between memory cell by address 'addr' and byte value
    This operation affects Z and N flags
    pic: core of PIC18F
    addr: address of first argument of conjuction
    value: byte value
    """
    result = pic.data[addr] | value
    set_bits = 0
    if result == 0:
        set_bits |= Z
    if result & 0x80 > 0:
        set_bits |= N
    pic.data[addr] = result
    pic.affectStatusBits(N | Z, set_bits)

def _xor(pic, addr, value):
    """Internal procedure for exclusive disjunction between memory cell and byte and for saving result in memory cell
    This operation affects Z and N flags
    pic: core of PIC18F
    addr: address of first argument of execlusive conjuction and result
    value: byte value - the second argument
    """
    result = pic.data[addr] ^ value
    set_bits = 0
    if result == 0:
        set_bits |= Z
    if result & 0x80 > 0:
        set_bits |= N
    pic.data[addr] = result
    pic.affectStatusBits(N | Z, set_bits)

# addresses of SFRs
WREG, BSR = 0xfe8, 0xfe0
PCL = 0xff9
TOSU, TOSH, TOSL = 0xfff, 0xffe, 0xffd

########################################
# Byte oriented commands with registers
########################################
def addwf(pic, f, d, a):
    """Add WREG with 'f'
    affect C, DC, Z, OV, N
    pic: core of PIC18F
    f: part of register address of second term of sum
    d: flag specifying direction of saving result (if d = 0 then result is saved in WREG else in register by address defined 'f')
    a: flag specifying address of second term of sum (if a = 1 then address defined BSR else fast access bank is used)
    """
    if a == 1:
        argAddr = (pic.bsr << 8) | f
    else:
        argAddr = f if f < 0x80 else (0xf00 | f)
    resAddr = argAddr if d == 1 else WREG
    secondArg = pic.wreg if d == 1 else pic.data[argAddr]
    _add(pic, resAddr, secondArg)

addwf.size = 2


def addwfc(pic, f, d, a):
    """Add WREG with 'f' and with bit C
    affect C, DC, Z, OV, N
    pic: core of PIC18F
    f: part of register address of second term of sum
    d: flag specifying direction of saving result (if d = 0 then result is saved in WREG else in register by address defined 'f')
    a: flag specifying address of second term of sum (if a = 1 then address defined BSR else fast access bank is used)
    """
    if a == 1:
        argAddr = (pic.bsr << 8) | f
    else:
        argAddr = f if f < 0x80 else (0xf00 | f)
    carryFlag = pic.status & C
    resAddr = WREG if d == 0 else argAddr
    secondArg = pic.wreg if d == 1 else pic.data[argAddr]
    _add(pic, resAddr, secondArg)
    _add(pic, resAddr, carryFlag)
 
addwfc.size = 2


def andwf(pic, f, d, a):
    """Conjunction between WREG and 'f'
    affect Z, N
    pic: core of PIC18F
    f: part of register address of second term of conjunction
    d: flag specifying direction of saving result (if d = 0 then result is saved in WREG else in register by address defined 'f')
    a: flag specifying address of second term of conjuction (if a = 1 then address defined BSR else fast access bank is used)
    """
    if a == 1:
        argAddr = (pic.bsr << 8) | f
    else:
        argAddr = f if f < 0x80 else (0xf00 | f)
    resAddr = WREG if d == 0 else argAddr
    secondArg = pic.wreg if d == 1 else pic.data[argAddr]
    _and(pic, resAddr, secondArg) 
    
andwf.size = 2


def clrf(pic, f, a):
    """Clear register 'f'
    affect Z
    pic: core of PIC18F
    f: part of register address
    a: flag specifying register address (if a = 1 then address defined BSR else fast access bank is used)
    """
    if a == 1:
        argAddr = (pic.bsr << 8) | f
    else:
        argAddr = f if f < 0x80 else (0xf00 | f)
    pic.data[argAddr] = 0
    pic.affectStatusBits(Z, Z)

clrf.size = 2


def comf(pic, f, d, a):
    """Inverse register 'f'
    affect Z, N
    pic: core of PIC18F
    f: part of register address
    d: flag specifying direction of saving result (if d = 0 then result is saved in WREG else in register by address defined 'f')
    a: flag specifying register address (if a = 1 then address is defined with BSR else fast access bank is used)
    """
    if a == 1:
        argAddr = (pic.bsr << 8) | f
    else:
        argAddr = f if f < 0x80 else (0xf00 | f)
    resAddr = WREG if d == 0 else argAddr

    result = ~pic.data[argAddr] & 0xff
    set_bits = 0
    if result == 0:
        set_bits |= Z
    if result & 0x80 > 0:
        set_bits |= N
    pic.data[resAddr] = result
    pic.affectStatusBits(N | Z, set_bits)

comf.size = 2


def cpfseq(pic, f, a):
    """Compare WREG and 'f'; skip next instuction if they are equal
    pic: core of PIC18F
    f: part of register address
    a: flag specifying register address (if a = 1 then address is defined with BSR else fast access bank is used)
    """
    if a == 1:
        argAddr = (pic.bsr << 8) | f
    else:
        argAddr = f if f < 0x80 else (0xf00 | f)
    if pic.data[argAddr] == pic.wreg:
        pic.incPC(2)

cpfseq.size = 2


def cpfsgt(pic, f, a):
    """Compare WREG and 'f'; if WREG > 'f' then skip next instruction
    pic: core of PIC18F
    f: part of register address
    a: flag specifying register address (if a = 1 then address is defined with BSR else fast access bank is used)
    """
    if a == 1:
        argAddr = (pic.bsr << 8) | f
    else:
        argAddr = f if f < 0x80 else (0xf00 | f)
    if pic.data[argAddr] < pic.wreg:
        pic.incPC(2)

cpfsgt.size = 2


def cpfslt(pic,f, a):
    """Compare WREG and 'f'; if WREG < 'f' then skip next instruction
    pic: core of PIC18F
    f: part of register address
    a: flag specifying register address (if a = 1 then address is defined with BSR else fast access bank is used)
    """
    if a == 1:
        argAddr = (pic.bsr << 8) | f
    else:
        argAddr = f if f < 0x80 else (0xf00 | f)
    if pic.data[argAddr] > pic.wreg:
        pic.incPC(2)

cpfslt.size = 2


def decf(pic, f, d, a):
    """Decrement 'f'
    affect C, DC, Z, OV, N flags
    pic: core of PIC18F
    f: part of argument register address
    d: flag specifying direction of saving result (if d = 0 then result is saved in WREG else in register by address defined 'f')
    a: flag specifying register address (if a = 1 then address is defined with BSR else fast access bank is used)
    """
    if a == 1:
        argAddr = (pic.bsr << 8) | f
    else:
        argAddr = f if f < 0x80 else (0xf00 | f)
    resAddr = WREG if d == 0 else argAddr

    arg = pic.data[argAddr]
    result = arg - 1
    set_bits = 0
    if arg != 0:
        set_bits |= C
    if (arg & 0xf) != 0:
        set_bits |= DC
    if result == 0:
        set_bits |= Z
    if result == 0x7f:
        set_bits |= OV
    if result & 0x80 > 0:
        set_bits |= N
    pic.data[resAddr] = result & 0xff
    pic.affectStatusBits(0x1f, set_bits)

decf.size = 2


def decfsz(pic, f, d, a):
    """Decrement 'f'; skip next instruction if result is equal zero
    pic: core of PIC18F
    f: part of argument register address
    d: flag specifying direction of saving result (if d = 0 then result is saved in WREG else in register by address defined 'f')
    a: flag specifying register address (if a = 1 then address is defined with BSR else fast access bank is used)
    """
    if a == 1:
        argAddr = (pic.bsr << 8) | f
    else:
        argAddr = f if f < 0x80 else (0xf00 | f)
    resAddr = WREG if d == 0 else argAddr

    result = pic.data[argAddr] - 1
    if result == 0:
        pic.incPC(2)
    pic.data[resAddr] = result & 0xff

decf.size = 2


def dcfsnz(pic, f, d, a):
    """Decrement 'f'; skip next instruction if result is not equal zero
    pic: core of PIC18F
    f: part of argument register address
    d: flag specifying direction of saving result (if d = 0 then result is saved in WREG else in register by address defined 'f')
    a: flag specifying register address (if a = 1 then address is defined with BSR else fast access bank is used)
    """
    if a == 1:
        argAddr = (pic.bsr << 8) | f
    else:
        argAddr = f if f < 0x80 else (0xf00 | f)
    resAddr = WREG if d == 0 else argAddr

    result = pic.data[argAddr] - 1
    if result != 0:
        pic.incPC(2)
    pic.data[resAddr] = result & 0xff

dcfsnz.size = 2


def incf(pic, f, d, a):
    """Increment 'f'
    affect C, DC, Z, OV, N flags
    pic: core of PIC18F
    f: part of argument register address
    d: flag specifying direction of saving result (if d = 0 then result is saved in WREG else in register by address defined 'f')
    a: flag specifying register address (if a = 1 then address is defined with BSR else fast access bank is used)
    """
    if a == 1:
        argAddr = (pic.bsr << 8) | f
    else:
        argAddr = f if f < 0x80 else (0xf00 | f)
    resAddr = WREG if d == 0 else argAddr

    arg = pic.data[argAddr]
    result = arg + 1
    set_bits = 0
    if arg == 0xff:
        set_bits |= C
    if (arg & 0xf) == 0xf:
        set_bits |= DC
    if (result & 0xff) == 0:
        set_bits |= Z
    if result == 0x80:
        set_bits |= OV
    if result & 0x80 > 0:
        set_bits |= N
    pic.data[resAddr] = result & 0xff
    pic.affectStatusBits(0x1f, set_bits)

incf.size = 2


def incfsz(pic, f, d, a):
    """Increment 'f'; skip next instruction if result is equal zero
    pic: core of PIC18F
    f: part of argument register address
    d: flag specifying direction of saving result (if d = 0 then result is saved in WREG else in register by address defined 'f')
    a: flag specifying register address (if a = 1 then address is defined with BSR else fast access bank is used)
    """
    if a == 1:
        argAddr = (pic.bsr << 8) | f
    else:
        argAddr = f if f < 0x80 else (0xf00 | f)
    resAddr = WREG if d == 0 else argAddr

    result = (pic.data[argAddr] + 1) & 0xff
    if result == 0:
        pic.incPC(2)
    pic.data[resAddr] = result

incfsz.size = 2


def infsnz(pic, f, d, a):
    """Increment 'f'; skip next instruction if result is not equal zero
    pic: core of PIC18F
    f: part of argument register address
    d: flag specifying direction of saving result (if d = 0 then result is saved in WREG else in register by address defined 'f')
    a: flag specifying register address (if a = 1 then address is defined with BSR else fast access bank is used)
    """
    if a == 1:
        argAddr = (pic.bsr << 8) | f
    else:
        argAddr = f if f < 0x80 else (0xf00 | f)
    resAddr = WREG if d == 0 else argAddr

    result = (pic.data[argAddr] + 1) & 0xff
    if result != 0:
        pic.incPC(2)
    pic.data[resAddr] = result

infsnz.size = 2


def iorwf(pic, f, d, a):
    """Logic disjunction between WREG and 'f';
    Flags Z and N are affected
    pic: core of PIC18F
    f: part of argument register address
    d: flag specifying direction of saving result (if d = 0 then result is saved in WREG else in register by address defined 'f')
    a: flag specifying register address (if a = 1 then address is defined with BSR else fast access bank is used)
    """
    if a == 1:
        argAddr = (pic.bsr << 8) | f
    else:
        argAddr = f if f < 0x80 else (0xf00 | f)
    resAddr = WREG if d == 0 else argAddr
    secondArg = pic.wreg if d == 1 else pic.data[argAddr]
    _ior(pic, resAddr, secondArg)

iorwf.size = 2


def movf(pic, f, d, a):
    """Move 'f'
    Flags Z and N are affected
    pic: core of PIC18F
    f: part of argument register address
    d: flag specifying direction of saving result (if d = 0 then result is saved in WREG else in register by address defined 'f')
    a: flag specifying register address (if a = 1 then address is defined with BSR else fast access bank is used)
    """
    if a == 1:
        argAddr = (pic.bsr << 8) | f
    else:
        argAddr = f if f < 0x80 else (0xf00 | f)
    resAddr = WREG if d == 0 else argAddr
    pic.data[resAddr] = pic.data[argAddr]

movf.size = 2


def movff(pic, fs, fd):
    """Move source 'fs' to destination 'fd'
    pic: core of PIC18F
    fs: address of source
    fd: address of destination
    """
    assert fs != PCL and fs != TOSU and fs != TOSH and fs != TOSL
    pic.data[fd] = pic.data[fs]

movff.size = 4


def movwf(pic, f, a):
    """Move WREG to 'f'
    pic: core of PIC18F
    f: part of argument register address
    a: flag specifying register address (if a = 1 then address is defined with BSR else fast access bank is used)
    """
    if a == 1:
        argAddr = (pic.bsr << 8) | f
    else:
        argAddr = f if f < 0x80 else (0xf00 | f)
    pic.data[argAddr] = pic.wreg

movwf.size = 2


def mulwf(pic, f, a):
    """Multiply WREG and 'f'
    pic: core of PIC18F
    f: part of argument register address
    a: flag specifying register address (if a = 1 then address is defined with BSR else fast access bank is used)
    """
    if a == 1:
        argAddr = (pic.bsr << 8) | f
    else:
        argAddr = f if f < 0x80 else (0xf00 | f)
    result = pic.wreg * pic.data[argAddr]
    pic.prodl = result & 0xff
    pic.prodh = (result & 0xff00) >> 8

mulwf.size = 2


def negf(pic, f, a):
    """Negative value of 'f'
    Flags C, DC, Z, OV, N are affected
    pic: core of PIC18F
    f: part of argument register address
    a: flag specifying register address (if a = 1 then address is defined with BSR else fast access bank is used)
    """
    if a == 1:
        argAddr = (pic.bsr << 8) | f
    else:
        argAddr = f if f < 0x80 else (0xf00 | f)

    result = (~pic.data[argAddr] + 1) & 0xff
    set_bits = 0
    if result & 0x80 > 0:
        set_bits |= N
    if result == 0:
        set_bits |= (C | Z)
    if result & 0xf == 0:
        set_bits |= DC
    if result == 0x80:
        set_bits |= OV
    pic.data[argAddr] = result
    pic.affectStatusBits(0x1f, set_bits)

negf.size = 2


def rlcf(pic, f, d, a):
    """Left shift with carry
    Flags C, Z, N are affects
    pic: core of PIC18F
    f: part of argument register address
    d: flag specifying direction of saving result (if d = 0 then result is saved in WREG else in register by address defined 'f')
    a: flag specifying register address (if a = 1 then address is defined with BSR else fast access bank is used)
    """
    if a == 1:
        argAddr = (pic.bsr << 8) | f
    else:
        argAddr = f if f < 0x80 else (0xf00 | f)
    resAddr = WREG if d == 0 else argAddr

    result = pic.data[argAddr] << 1
    result |= pic.status & C
    set_bits = (result & 0x100) >> 8
    if result & 0xff == 0:
        set_bits |= Z
    if result & 0x80 > 0:
        set_bits |= N

    pic.data[resAddr] = result & 0xff
    pic.affectStatusBits(C | Z | N, set_bits)

rlcf.size = 2


def rlncf(pic, f, d, a):
    """Left shift without carry
    Flags Z, N are affects
    pic: core of PIC18F
    f: part of argument register address
    d: flag specifying direction of saving result (if d = 0 then result is saved in WREG else in register by address defined 'f')
    a: flag specifying register address (if a = 1 then address is defined with BSR else fast access bank is used)
    """
    if a == 1:
        argAddr = (pic.bsr << 8) | f
    else:
        argAddr = f if f < 0x80 else (0xf00 | f)
    resAddr = WREG if d == 0 else argAddr

    result = pic.data[argAddr] << 1
    result |= (result >> 8)
    set_bits = 0
    if result & 0xff == 0:
        set_bits |= Z
    if result & 0x80 > 0:
        set_bits |= N

    pic.data[resAddr] = result & 0xff
    pic.affectStatusBits(Z | N, set_bits)

rlncf.size = 2


def rrcf(pic, f, d, a):
    """Right shift with carry
    Flags C, Z, N are affects
    pic: core of PIC18F
    f: part of argument register address
    d: flag specifying direction of saving result (if d = 0 then result is saved in WREG else in register by address defined 'f')
    a: flag specifying register address (if a = 1 then address is defined with BSR else fast access bank is used)
    """
    if a == 1:
        argAddr = (pic.bsr << 8) | f
    else:
        argAddr = f if f < 0x80 else (0xf00 | f)
    resAddr = WREG if d == 0 else argAddr

    arg = pic.data[argAddr]
    set_bits = arg & 0x1
    result = (arg >> 1) | ((pic.status & C) << 7)
    if result & 0xff == 0:
        set_bits |= Z
    if result & 0x80 > 0:
        set_bits |= N

    pic.data[resAddr] = result
    pic.affectStatusBits(C | Z | N, set_bits)

rrcf.size = 2


def rrncf(pic, f, d, a):
    """Right shift without carry
    Flags Z, N are affects
    pic: core of PIC18F
    f: part of argument register address
    d: flag specifying direction of saving result (if d = 0 then result is saved in WREG else in register by address defined 'f')
    a: flag specifying register address (if a = 1 then address is defined with BSR else fast access bank is used)
    """
    if a == 1:
        argAddr = (pic.bsr << 8) | f
    else:
        argAddr = f if f < 0x80 else (0xf00 | f)
    resAddr = WREG if d == 0 else argAddr

    arg = pic.data[argAddr]
    arg |= ((arg & 0b1) << 8)
    result = arg >> 1
    set_bits = 0
    if result & 0xff == 0:
        set_bits |= Z
    if result & 0x80 > 0:
        set_bits |= N

    pic.data[resAddr] = result
    pic.affectStatusBits(Z | N, set_bits)

rrncf.size = 2


def setf(pic, f, a):
    """Set all bits of 'f'
    pic: core of PIC18F
    f: part of argument register address
    a: flag specifying register address (if a = 1 then address is defined with BSR else fast access bank is used)
    """
    if a == 1:
        argAddr = (pic.bsr << 8) | f
    else:
        argAddr = f if f < 0x80 else (0xf00 | f)
    pic.data[argAddr] = 0xff

setf.size = 2


def subfwb(pic, f, d, a):
    """Substitute 'f' from WREG with borrow
    Flags Z, N, OV, DC, C are affects
    pic: core of PIC18F
    f: part of argument register address
    d: flag specifying direction of saving result (if d = 0 then result is saved in WREG else in register by address defined 'f')
    a: flag specifying register address (if a = 1 then address is defined with BSR else fast access bank is used)
    """
    if a == 1:
        argAddr = (pic.bsr << 8) | f
    else:
        argAddr = f if f < 0x80 else (0xf00 | f)
    resAddr = WREG if d == 0 else argAddr

    arg1 = pic.wreg
    arg2 = (-pic.data[argAddr]) & 0xff
    arg3 = 0 if (pic.status & C == 1) else 0xff
    result = arg1 + arg2 + arg3

    set_bits = 0
    if result & 0xf00 > 0:
        set_bits |= C
    if ((arg1 & 0xf) + (arg2 & 0xf) + (arg3 & 0xf)) & 0xf0 > 0:
        set_bits |= DC
    if result & 0xff == 0:
        set_bits |= Z
    carryIntoSign = ((arg1 & 0x7f) + (arg2 & 0x7f) + (arg3 & 0x7f)) & 0x80
    if ((result & 0x100) ^ (carryIntoSign << 1)) > 0:
        set_bits |= OV
    if result & 0x80 > 0:
        set_bits |= N

    pic.data[resAddr] = result & 0xff
    pic.affectStatusBits(0x1f, set_bits)

subfwb.size = 2


def subwf(pic, f, d, a):
    """Substitute WREG from 'f'
    Flags Z, N, OV, DC, C are affects
    pic: core of PIC18F
    f: part of argument register address
    d: flag specifying direction of saving result (if d = 0 then result is saved in WREG else in register by address defined 'f')
    a: flag specifying register address (if a = 1 then address is defined with BSR else fast access bank is used)
    """
    if a == 1:
        argAddr = (pic.bsr << 8) | f
    else:
        argAddr = f if f < 0x80 else (0xf00 | f)
    resAddr = WREG if d == 0 else argAddr

    arg1, arg2 = pic.data[argAddr], (~pic.wreg + 1) & 0xff
    result = arg1 + arg2

    set_bits = 0
    if result & 0x100 > 0:
        set_bits |= C
    if ((arg1 & 0xf) + (arg2 & 0xf)) & 0x10 > 0:
        set_bits |= DC
    if result & 0xff == 0:
        set_bits |= Z
    if (arg1 & 0x80 == arg2 & 0x80) and (arg1 & 0x80 != result & 0x80):
        set_bits |= OV
    if result & 0x80 > 0:
        set_bits |= N

    pic.data[resAddr] = result & 0xff
    pic.affectStatusBits(0x1f, set_bits)

subwf.size = 2


def subwfb(pic, f, d, a):
    """Substitute WREG from 'f' with borrow
    Flags Z, N, OV, DC, C are affects
    pic: core of PIC18F
    f: part of argument register address
    d: flag specifying direction of saving result (if d = 0 then result is saved in WREG else in register by address defined 'f')
    a: flag specifying register address (if a = 1 then address is defined with BSR else fast access bank is used)
    """
    if a == 1:
        argAddr = (pic.bsr << 8) | f
    else:
        argAddr = f if f < 0x80 else (0xf00 | f)
    resAddr = WREG if d == 0 else argAddr

    arg1 = pic.data[argAddr]
    arg2 = (-pic.wreg) & 0xff
    arg3 = 0 if (pic.status & C == 1) else 0xff
    result = arg1 + arg2 + arg3

    set_bits = 0
    if result & 0xf00 > 0:
        set_bits |= C
    if ((arg1 & 0xf) + (arg2 & 0xf) + (arg3 & 0xf)) & 0xf0 > 0:
        set_bits |= DC
    if result & 0xff == 0:
        set_bits |= Z
    carryIntoSign = ((arg1 & 0x7f) + (arg2 & 0x7f) + (arg3 & 0x7f)) & 0x80
    if ((result & 0x100) ^ (carryIntoSign << 1)) > 0:
        set_bits |= OV
    if result & 0x80 > 0:
        set_bits |= N

    pic.data[resAddr] = result & 0xff
    pic.affectStatusBits(0x1f, set_bits)

subwfb.size = 2


def swapf(pic, f, d, a):
    """Exchange nibbles in 'f'
    pic: core of PIC18F
    f: part of argument register address
    d: flag specifying direction of saving result (if d = 0 then result is saved in WREG else in register by address defined 'f')
    a: flag specifying register address (if a = 1 then address is defined with BSR else fast access bank is used)
    """
    if a == 1:
        argAddr = (pic.bsr << 8) | f
    else:
        argAddr = f if f < 0x80 else (0xf00 | f)
    resAddr = WREG if d == 0 else argAddr

    arg = pic.data[argAddr]
    nibble1, nibble2 = arg & 0xf, (arg & 0xf0) >> 4
    pic.data[resAddr] = (nibble1 << 4) | nibble2

swapf.size = 2


def tstfsz(pic, f, a):
    """Test 'f', skip next instruction if it's equal 0
    pic: core of PIC18F
    f: part of argument register address
    a: flag specifying register address (if a = 1 then address is defined with BSR else fast access bank is used)
    """
    if a == 1:
        argAddr = (pic.bsr << 8) | f
    else:
        argAddr = f if f < 0x80 else (0xf00 | f)
    if pic.data[argAddr] == 0:
        pic.incPC(2)

tstfsz.size = 2


def xorwf(pic, f, d, a):
    """Logical exclusive OR between WREG and 'f'
    Flags Z and N are affected
    f: part of argument register address
    d: flag specifying direction of saving result (if d = 0 then result is saved in WREG else in register by address defined 'f')
    a: flag specifying register address (if a = 1 then address is defined with BSR else fast access bank is used)
    """
    if a == 1:
        argAddr = (pic.bsr << 8) | f
    else:
        argAddr = f if f < 0x80 else (0xf00 | f)
    if d == 1:
        resAddr = argAddr
        arg = pic.wreg
    else:
        resAddr = WREG
        arg = pic.data[argAddr]
    _xor(pic, resAddr, arg)

xorwf.size = 2


##################################################
# Bit oriented operations with registries
##################################################
def bcf(pic, f, b, a):
    """Reset bit in 'f'
    pic: core of PIC18F
    f: part of argument register address
    b: number of bit to be reset
    a: flag specifying register address (if a = 1 then address is defined with BSR else fast access bank is used)
    """
    if a == 1:
        argAddr = (pic.bsr << 8) | f
    else:
        argAddr = f if f < 0x80 else (0xf00 | f)
    pic.data[argAddr] &= ~(1 << b)

bcf.size = 2


def bsf(pic, f, b, a):
    """Set bit in 'f'
    pic: core of PIC18F
    f: part of argument register address
    b: number of bit to be set
    a: flag specifying register address (if a = 1 then address is defined with BSR else fast access bank is used)
    """
    if a == 1:
        argAddr = (pic.bsr << 8) | f
    else:
        argAddr = f if f < 0x80 else (0xf00 | f)
    pic.data[argAddr] |= (1 << b)

bsf.size = 2


def btfsc(pic, f, b, a):
    """Test bit; skip next instruction if it's equal '0'
    pic: core of PIC18F
    f: part of argument register address
    b: number of bit for testing
    a: flag specifying register address (if a = 1 then address is defined with BSR else fast access bank is used)
    """
    if a == 1:
        argAddr = (pic.bsr << 8) | f
    else:
        argAddr = f if f < 0x80 else (0xf00 | f)
    bit = (pic.data[argAddr] >> b) & 0x01
    if bit == 0:
        pic.incPC(2)

btfsc.size = 2


def btfss(pic, f, b, a):
    """Test bit; skip next instruction if it's equal '1'
    pic: core of PIC18F
    f: part of argument register address
    b: number of bit for testing
    a: flag specifying register address (if a = 1 then address is defined with BSR else fast access bank is used)
    """
    if a == 1:
        argAddr = (pic.bsr << 8) | f
    else:
        argAddr = f if f < 0x80 else (0xf00 | f)
    bit = (pic.data[argAddr] >> b) & 0x01
    if bit == 1:
        pic.incPC(2)

btfss.size = 2


def btg(pic, f, b, a):
    """Inverse bit in 'f'
    pic: core of PIC18F
    f: part of argument register address
    b: number of bit for testing
    a: flag specifying register address (if a = 1 then address is defined with BSR else fast access bank is used)
    """
    if a == 1:
        argAddr = (pic.bsr << 8) | f
    else:
        argAddr = f if f < 0x80 else (0xf00 | f)
    arg = pic.data[argAddr]
    pic.data[argAddr] = (arg | (1 << b)) & ~(arg & (1 << b))

btg.size = 2


#############################################
# Control instructions
#############################################
def bc(pic, n):
    """Branch if carry
    pic: core of PIC18F
    n: number of jumps (instructions in both directions)
    """
    if (pic.status & C) > 0:
        pic.incPC(2*n)

bc.size = 2


def bn(pic, n):
    """Branch if negative result
    pic: core of PIC18F
    n: number of jumps (instructions in both directions)
    """
    if (pic.status & N) > 0:
        pic.incPC(2*n)

bn.size = 2


def bnc(pic, n):
    """Branch if not carry
    pic: core of PIC18F
    n: number of jumps (instructions in both directions)
    """
    if (pic.status & C) == 0:
        pic.incPC(2*n)

bnc.size = 2


def bnn(pic, n):
    """Branch if not negative result
    pic: core of PIC18F
    n: number of jumps (instructions in both directions)
    """
    if (pic.status & N) == 0:
        pic.incPC(2*n)

bnn.size = 2


def bnov(pic, n):
    """Branch if not overflow
    pic: core of PIC18F
    n: number of jumps (instructions in both directions)
    """
    if (pic.status & OV) == 0:
        pic.incPC(2*n)

bnov.size = 2


def bnz(pic, n):
    """Branch if not zero
    pic: core of PIC18F
    n: number of jumps (instructions in both directions)
    """
    if (pic.status & Z) == 0:
        pic.incPC(2*n)

bnz.size = 2


def bov(pic, n):
    """Branch if overflow
    pic: core of PIC18F
    n: number of jumps (instructions in both directions)
    """
    if (pic.status & OV) > 0:
        pic.incPC(2*n)

bov.size = 2


def bra(pic, n):
    """Unconditional branch
    pic: core of PIC18F
    n: number of jumps (instructions in both directions)
    """
    pic.incPC(2*n)

bra.size = 2


def bz(pic, n):
    """Branch if zero
    pic: core of PIC18F
    n: number of jumps (instructions in both directions)
    """
    if (pic.status & Z) > 0:
        pic.incPC(2*n)

bz.size = 2


def call(pic, n, s):
    """Goto subroutine in all range of memory:
        * return address (PC + 4) is saved in stack
        * if s = 1 then WREG, STATUS, BSR is saved in fast access registers
        * PC<20:1> is uploaded into the stack
    """
    pass

call.size = 4


def clrwdt(pic):
    """Reset watcdog"""
    pass

def daw(pic):
    """Decimal correction of WREG"""
    pass

def goto(pic, n):
    """Goto to address"""
    pass

def nop(pic):
    """No operation"""
    pass

def pop(pic):
    """Read the top of stack TOS"""
    pass

def push(pic):
    """Record into the top of stack TOS"""
    pass

def rcall(pic, n):
    """Short branch to subroutine"""
    pass

def reset(pic):
    """Program reset"""
    pass

def retfie(pic, s):
    """Return from subroutine with permit of interruption"""
    pass

def retlw(pic, k):
    """Return from subroutine with loading of WREG"""
    pass

def return_(pic, s):
    """Return from subroutine"""
    pass

def sleep(pic):
    """Goto sleep mode"""
    pass

############################################
# Operations with constants
############################################
def addlw(pic, k):
    """Add WREG with constant 'k'
    affect C, DC, Z, OV, N
    pic: core of PIC18F
    k: constant value to be added
    """
    _add(pic, WREG, k)

addlw.size = 2

#def 

#############################################
# Operations: data memory <-> program memory
#############################################
