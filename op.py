import picmicro

def _add(pic, addr1, addr2):
    """Internal procedure for addition two memory cell and saving result by address 'addr1'
    pic: core of PIC18F
    addr1: address of first argument and result cell
    addr2: address of second argument cell
    """
    arg1, arg2 = datamem[addr1], datamem[addr2]
    result = arg1 + arg2

    N, OV, Z, DC, C = 0b10000, 0b01000, 0b00100, 0b00010, 0b00001
    set_bits = 0
    if result & 0x100 > 0:
        set_bits |= C
    if ((arg1 & 0xf) + (arg2 & 0xf)) & 0x1f > 0:
        set_bits |= DC
    if result & 0xff == 0:
        set_bits |= Z
    if (arg1 & 0x80 == arg2 & 0x80) and (arg1 & 0x80 != result & 0x80):
        set_bits |= OV
    if result & 0x80 > 0:
        set_bits |= N

    datamem[addr1] = result & 0xff
    pic.setStatusBits(set_bits)
    pic.resetStatusBits(~set_bits & 0x1f)


def addlw(pic, k):
    """  """
    pic.data.wreg.add(k, pic.data.status)
    pic.inc_pc(2)
