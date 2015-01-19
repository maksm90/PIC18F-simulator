"""
Definition of basic components of PIC18F simulator

DataMemory: memory for storing General Purpose Registers and Specific Purpose Registers
OutOfDataMemoryAccess: exception raised after access to nonexisting cell 

PICmicro: main class describing core of PIC18F
"""

class OutOfDataMemoryAccess(Exception):
    pass

class DataMemory:
    """Data memory of PICmicro"""

    DATA_ADDR_SUP = 0x1000
    GPR_ADDR_SUP = 0x300
    SFR_ADDR_MIN = 0xf00

    def __init__(self):
        """
        storage: dictionary for storing data at address (dict: integer -> byte value)
        """
        self.storage = {}

    def __setitem__(self, addr, byte):
        """set byte to memory cell at given address

        addr: address of data memory (integer from 0 up to DATA_ADDR_SUP)
        byte: byte value to be stored in memory (integer between 0-255)
        throws: OutOfDataMemoryAccess if addr doesn't enter in acceptable interval
        """
        assert 0 <= byte <= 0xff
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
