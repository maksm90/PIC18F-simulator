import picmicro

# bitmasks of flags
N, OV, Z, DC, C = 0b10000, 0b01000, 0b00100, 0b00010, 0b00001

def _add(pic, addr, value):
    """Internal procedure for addition two memory cell and saving result by address 'addr'
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
    a: flag specifying address of second term of sum (if a = 1 then address defined BSR else fast access bank is used
    """
    if a == 1:
        argAddr = (pic.bsr << 8) | f
    else:
        argAddr = f if f < 0x80 else (0xf00 | f)
    resAddr = WREG if d == 0 else argAddr
    _add(pic, resAddr, pic.data[argAddr])

addwf.size = 2


def addwfc(pic, f, d, a):
    """Add WREG with 'f' and bit C
    affect C, DC, Z, OV, N
    pic: core of PIC18F
    f: part of register address of second term of sum
    d: flag specifying direction of saving result (if d = 0 then result is saved in WREG else in register by address defined 'f')
    a: flag specifying address of second term of sum (if a = 1 then address defined BSR else fast access bank is used
    """
    if a == 1:
        argAddr = (pic.bsr << 8) | f
    else:
        argAddr = f if f < 0x80 else (0xf00 | f)
    resAddr = WREG if d == 0 else argAddr
    carryFlag = pic.status & C
    _add(pic, resAddr, pic.data[argAddr])
    _add(pic, resAddr, carryFlag)
 
addwfc.size = 2

def addlw(pic, k):
    """Add WREG with constant 'k'
    affect C, DC, Z, OV, N
    """
    _add(pic, WREG, k)

addlw.size = 2
