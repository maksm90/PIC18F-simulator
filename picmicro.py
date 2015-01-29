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

    def __init__(self, sfr):
        """Initialize memory of data that consists of GPRs and SFRs
        sfr: array composed of SFR entries
        """
        self.sfr = sfr
        self.gpr = {}               # general puspose registers

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
        if not (0 <= addr < self.DATA_ADDR_SUP):
            raise OutOfDataMemoryAccess()

        if addr < self.GPR_ADDR_SUP:
            return self.gpr.setdefault(addr, 0)
        if addr >= self.SFR_ADDR_MIN:
            return self.sfr[addr - self.SFR_ADDR_MIN]
        return 0


class PICmicro(object):
    """PIC18F microcontroller definition"""

    # indices of SFRs
    WREG = 0x68
    STATUS = 0x58
    BSR = 0x60
    PRODL, PRODH = 0x73, 0x74

    ADDR_MASK = 0x1fffff
    N_SFRs = 0x80

    def __init__(self):
        """Initialize state of PIC18F"""
        self.__pc = 0                                       # program counter
        self.sfr = [0] * self.N_SFRs                        # specific purpose registers
        self.data = DataMemory(self.sfr)                    # addressable memory

    @property
    def pc(self):
        return self.__pc

    def incPC(self, delta):
        """Increment program counter by delta"""
        self.__pc = (self.__pc + delta) & self.ADDR_MASK

    def affectStatusBits(self, affected_bit_mask, bits):
        """Affect bits on STATUS
        affected_bit_mask: bit mask for picking affected bits (0b0-0b11111)
        bits: result bits
        """
        self.sfr[self.STATUS] &= ~affected_bit_mask & 0x1f
        self.sfr[self.STATUS] |= bits & affected_bit_mask

    @property
    def wreg(self):
        return self.sfr[self.WREG]
    @wreg.setter
    def wreg(self, value):
        assert 0 <= value <= 0xff
        self.sfr[self.WREG] = value

    @property
    def status(self):
        return self.sfr[self.STATUS]
    @status.setter
    def status(self, value):
        assert 0 <= value <= 0xff
        self.sfr[self.STATUS] = value

    @property
    def bsr(self):
        return self.sfr[self.BSR] & 0xf
    @bsr.setter
    def bsr(self, value):
        assert 0 <= value <= 0xff
        self.sfr[self.BSR] = value

    @property
    def prodl(self):
        return self.sfr[self.PRODL]
    @prodl.setter
    def prodl(self, value):
        assert 0 <= value <= 0xff
        self.sfr[self.PRODL] = value

    @property
    def prodh(self):
        return self.sfr[self.PRODH]
    @prodh.setter
    def prodh(self, value):
        assert 0 <= value <= 0xff
        self.sfr[self.PRODH] = value
