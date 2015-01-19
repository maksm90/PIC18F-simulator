"""
Definition of basic components of PIC18F simulator

Register: superclass for all memory cells

StatusReg: status register of PIC18F

RegularReg: simple register under that arithmetic operations are defined

DataMemory: memory for storing General Purpose Registers and Specific Purpose Registers
OutOfDataMemoryAccess: exception raised after access to nonexisting cell 

PICmicro: main class describing core of PIC18F
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

    def __init__(self):
        self.__value = 0

    @property
    def value(self):
        return self.__value
    @value.setter
    def value(self, val):
        pass

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
        """Substitute other from current register and save result in current register
        other: either byte value or register participating in substitution
        status: status register for detecting specific events after operations has done
        """
        if isinstance(other, Register):
            other.value = (~other.value + 1) % 0xff
        else:
            other = (~other + 1) % 0xff
        self.add(self, other, status)

class OutOfDataMemoryAccess(Exception):
    pass

class DataMemory:
    """Data memory of PICmicro"""

    DATA_ADDR_SUP = 0x1000
    GPR_ADDR_SUP = 0x300
    SFR_ADDR_MIN = 0xf00

    def __init__(self):
        """
        storage: dictionary for storing data at address (dict: integer -> ByteCell)
        """
        self.storage = {}

    def __setitem__(self, addr, other):
        """set byte to memory cell at given address

        addr: address of data memory (integer from 0 up to GPR_ADDR_SUP or from SFR_ADDR_MIN up to DATA_ADDR_SUP)
        other: byte value or register to be stored in memory (integer between 0-255)
        throws: OutOfDataMemoryAccess if addr havn't entered in acceptable interval
        """
        if not (0 <= addr < self.DATA_ADDR_SUP):
            raise OutOfDataMemoryAccess()
        if addr < self.GPR_ADDR_SUP or addr >= self.SFR_ADDR_MIN:
            cell = self[addr]
            cell.value = other.value if isinstance(other, Register) else other

    def __getitem__(self, addr):
        """get byte cell from memory at given address

        addr: address of data memory 
            (integer from 0 up to GPR_ADDR_SUP or from SFR_ADDR_MIN up to DATA_ADDR_SUP)
        return: register object associated with address 'addr'
        throws: OutOfDataMemoryAccess if addr havn't entered in acceptable interval
        """
        if not (0 <= addr < self.DATA_ADDR_SUP):
            raise OutOfDataMemoryAccess()
        if addr < self.GPR_ADDR_SUP or addr >= self.SFR_ADDR_MIN:
            return self.storage.setdefault(addr, RegularReg())
        return 0


class PICmicro(object):
    """PIC18F microcontroller definition"""

    # SFRs addresses
    WREG = 0xfe8
    STATUS = 0xfd8
    BSR = 0xfe0

    # limit parameters of PICmicro
    PC_SUP = 0x200000

    def __init__(self, data=DataMemory()):
        """
        pc: program counter (integer from 0 up to PC_SUP)
        data: data memory
        """
        self.pc = 0
        self.data = data

        self.wreg = 0
        self.bsr = 0
        self.status = 0

    def inc_pc(self, delta):
        self.pc = (self.pc + delta) & self.PC_SUP

    @property
    def wreg(self):
        return self.data[self.WREG]
    @wreg.setter
    def wreg(self, value):
        self.data[self.WREG] = value
    
    @property
    def status(self):
        return self.data[self.STATUS]

    @property
    def bsr(self):
        return self.data[self.BSR]
    @bsr.setter
    def bsr(self, value):
        self.data[self.BSR] = value
