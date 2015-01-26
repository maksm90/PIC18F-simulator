import picmicro

# bitmasks of flags
N, OV, Z, DC, C = 0b10000, 0b01000, 0b00100, 0b00010, 0b00001

def _add(pic, addr, value):
    """Internal procedure for addition two byte values and saving result by address 'addr'.
    This operation affect C, DC, Z, OV, N flags
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
    pic.setStatusBits(set_bits)
    pic.resetStatusBits(~set_bits & 0x1f)

def _and(pic, addr, value):
    """Internal procedure for doing bitwise conjuction of content of cell by address 'addr' and byte value 'value' and saving result into the cell
    This operation affect Z and N flags
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
    pic.setStatusBits(set_bits)
    pic.resetStatusBits(~set_bits & (N | Z))

# addresses of SFRs
WREG, BSR = 0xfe8, 0xfe0

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
    resArgAddr = argAddr if d == 1 else WREG
    secondArg = pic.wreg if d == 1 else pic.data[argAddr]
    _add(pic, resArgAddr, secondArg)

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
    pic.setStatusBits(Z)

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
    pic.setStatusBits(set_bits)
    pic.resetStatusBits(~set_bits & (N | Z))
    pic.data[resAddr] = result

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


def addlw(pic, k):
    """Add WREG with constant 'k'
    affect C, DC, Z, OV, N
    pic: core of PIC18F
    k: constant value to be added
    """
    _add(pic, WREG, k)

addlw.size = 2
