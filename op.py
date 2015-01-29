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


def addlw(pic, k):
    """Add WREG with constant 'k'
    affect C, DC, Z, OV, N
    pic: core of PIC18F
    k: constant value to be added
    """
    _add(pic, WREG, k)

addlw.size = 2
