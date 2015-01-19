"""
Definition of basic components of PIC18F simulator

Register: superclass for all memory cells
"""

class Register:
    """Register for storing byte value"""
    def __init__(self, value=0):
        """
        value: byte value of register (integer between 0-255)
        """
        self.value = value

class StatusReg(Register):
    """Register for storing status statuss""" 

    C = 0b00001
    DC = 0b00010
    Z = 0b00100
    OV = 0b01000
    N = 0b10000

    def set_C(self):
        self.value |= self.C
    def set_DC(self):
        self.value |= self.DC
    def set_Z(self):
        self.value |= self.Z
    def set_OV(self):
        self.value |= self.OV 
    def set_N(self):
        self.value |= self.N
    def reset_C(self):
        self.value &= ~self.C
    def reset_DC(self):
        self.value &= ~self.DC
    def reset_Z(self):
        self.value &= ~self.Z
    def reset_OV(self):
        self.value &= ~self.OV
    def reset_N(self):
        self.value &= ~self.N

class RegularReg(Register):
    """Register with simple arithmetic operations"""

    def add(self, other, status=None):
        """Add value of current register with other object into current register
        other: either byte value or register with that current register is sum up
        status: status register for detecting specific events after operations has done
        """
        value = other.value if isinstance(other, Register) else other
        result = self.value + value
        if status != None:
            if result & 0x80 == 0x80:
                status.set_N()
            else:
                status.reset_N()
            if (self.value & 0x80 == value & 0x80) and (result & 0x80 != value & 0x80):
                status.set_OV()
            else:
                status.reset_OV()
            if result & 0xff == 0:
                status.set_Z()
            else:
                status.reset_Z()
            if ((self.value & 0xf) + (value & 0xf)) & 0x10 == 0:
                status.reset_DC()
            else:
                status.set_DC()
            if result & 0x100 == 0:
                status.reset_C()
            else:
                status.set_C()
        self.value = result & 0xff

    def sub(self, other, status=None):
        if isinstance(other, Register):
            other.value = (~other.value + 1) % 0xff
        else:
            other = (~other + 1) % 0xff
        self.add(self, other, status)


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


# limit parameters of PICmicro
PC_SUP = 0x200000

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
