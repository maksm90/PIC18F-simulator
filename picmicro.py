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
    SFR_ADDR_MIN = 0xf80

    def __init__(self, sfr, gpr):
        """Initialize memory of data that consists of GPRs and SFRs
        sfr: array composed of SFR entries
        gpr: empty dictionary that maps address cell to GPR entry
        """
        self.sfr = sfr
        self.gpr = gpr

    def __setitem__(self, addr, byte):
        """set byte to memory cell at given address
        addr: address of data memory (integer from 0 up to DATA_ADDR_SUP)
        byte: byte value to be stored in memory (integer between 0-255)
        throws: OutOfDataMemoryAccess if addr doesn't enter in acceptable interval
        """
        assert 0 <= byte <= 0xff
        if not (0 <= addr < self.DATA_ADDR_SUP):
            raise OutOfDataMemoryAccess()

        if addr < self.GPR_ADDR_SUP:
            self.gpr[addr] = byte
        elif addr >= self.SFR_ADDR_MIN:
            self.sfr[addr - self.SFR_ADDR_MIN] = byte

    def __getitem__(self, addr):
        """get byte cell from memory at given address
        addr: address of data memory (integer from 0 up to DATA_ADDR_SUP)
        return: byte value associated with input address
        throws: OutOfDataMemoryAccess if addr havn't entered in acceptable interval
        """
        assert 0 <= byte <= 0xff
        if not (0 <= addr < self.DATA_ADDR_SUP):
            raise OutOfDataMemoryAccess()

        if addr < self.GPR_ADDR_SUP:
            return self.gpr[addr]
        if addr >= self.SFR_ADDR_MIN:
            return self.sfr[addr - self.SFR_ADDR_MIN]
        return 0


class PICmicro(object):
    """PIC18F microcontroller definition"""

    # indices of SFRs
    WREG = 0x68
    STATUS = 0x58
    BSR = 0x60

    # limit parameters of PICmicro
    PC_SUP = 0x200000
    N_SFRs = 0x80

    def __init__(self):
        """Initialize state of PIC18F"""

        self.__pc = 0                                       # program counter
        self.__sfr = [0] * N_SFRs                           # specific purpose registers
        self.__gpr = {}                                     # general puspose registers

        self.data = DataMemory(self.__sfr, self.__gpr)      # addressable memory

    @property
    def pc(self):
        return pc

    def inc_pc(self, delta):
        """Increment program counter by delta"""
        self.pc = (self.pc + delta) & self.PC_SUP

    def set_status(self, bit_mask):
        self.__sfr[self.STATUS] |= bit_mask
    def reset_status(self, bit_mask):
        self.__sfr[self.STATUS] &= ~bit_mask

    @property
    def wreg(self):
        return self.__sfr[self.WREG]
    @wreg.setter
    def wreg(self, value):
        self.__sfr[self.WREG] = value

    @property
    def status(self):
        return self.__sfr[self.STATUS]

    @property
    def bsr(self):
        return self.__sfr[self.BSR]
    @bsr.setter
    def bsr(self, value):
        self.__sfr[self.BSR] = value
