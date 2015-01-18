"""
Definition of basic components of PIC18F simulator
"""

# limit parameters of PICmicro
PC_SUP = 0x200000

class Register:
    """Register for storing byte value

    inv: 
        self.value & 0xff == self.value
    """
    def __init__(self, value=0):
        """value: byte value of register (integer between 0-255)"""
        self.value = value

# status bit masks
C = 0b00001
DC = 0b00010
Z = 0b00100
OV = 0b01000
N = 0b10000

class StatusReg(Register):
    """Register for storing status flags"""
    def set_bit(self, bit_mask):
        self.value |= bit_mask
    def reset_bit(self, bit_mask):
        self.value &= ~bit_mask

class RegularReg(Register):
    """Register with simple arithmetic operations"""

    def add(self, value, flag_reg=None):
        """ 
        pre: value & 0xff == value
        post: self.value == (__old__.self.value + value) & 0xff
        """
        result = self.value + value
        if flag_reg != None:
            if result & 0x80 == 0x80:
                flag_reg.set_bit(N)
            else:
                flag_reg.reset_bit(N)
            if (self.value & 0x80 == value & 0x80) and (result & 0x80 != value & 0x80):
                flag_reg.set_bit(OV)
            else:
                flag_reg.reset_bit(OV)
            if result & 0xff == 0:
                flag_reg.set_bit(Z)
            else:
                flag_reg.reset_bit(Z)
            if ((self.value & 0xf) + (value & 0xf)) & 0x10 == 0:
                flag_reg.reset_bit(DC)
            else:
                flag_reg.set_bit(DC)
            if result & 0x100 == 0:
                flag_reg.reset_bit(C)
            else:
                flag_reg.set_bit(C)
        self.value = result & 0xff


class DataMemory(object):
    """Data memory of PICmicro"""

    DATA_ADDR_SUP = 0x1000
    GPR_ADDR_SUP = 0x300
    SFR_ADDR_MIN = 0xf00

    # SFRs addresses
    WREG = 0xfe8
    STATUS = 0xfd8
    BSR = 0xfe0

    def __init__(self):
        """
        storage: dictionary for storing data at address (dict: integer -> ByteCell)
        wreg, status, bsr: SFRs of microcontroller
        """
        self.storage = {}
        self.wreg = RegularReg()
        self.status = StatusReg()
        self.bsr = RegularReg()

    def __setitem__(self, addr, value):
        """set byte to memory cell at given address

        addr: address of data memory 
            (integer from 0 up to GPR_ADDR_SUP or from SFR_ADDR_MIN up to DATA_ADDR_SUP)
        value: stored value to memory (integer between 0-255)
        """
        if addr == self.WREG:
            self.wreg.value = value
        if addr == self.BSR:
            self.bsr.value = value
        if addr == self.STATUS:
            self.status.value = value
        else:
            cell = self.storage.setdefault(addr, ByteCell())
            cell.value = value

    def __getitem__(self, addr):
        """get byte cell from memory at given address

        addr: address of data memory 
            (integer from 0 up to GPR_ADDR_SUP or from SFR_ADDR_MIN up to DATA_ADDR_SUP)
        """
        return self.storage.setdefault(addr, ByteCell())


class PICmicro(object):
    """PIC18F microcontroller definition
    
    inv: 
        0 <= self.pc < PC_SUP
    """

    def __init__(self, data=DataMemory()):
        self.pc = 0
        self.data = data

    def inc_pc(self, delta):
        self.pc = (self.pc + delta) & PC_SUP
