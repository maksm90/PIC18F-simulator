"""
Definition of basic components of PIC18F simulator: core, data memory, program memory, etc
"""

# limit parameters of PICmicro
PC_SUP = 0x200000

class DataMemory:
    """Memory for data of PICmicro"""

    DATA_ADDR_SUP = 0x1000
    GPR_ADDR_SUP = 0x300
    SFR_ADDR_MIN = 0xf00

    def __init__(self):
        self.__storage = {}

    def __setitem__(self, addr, value):
        """set byte to memory cell defined with address 'addr'

        pre:
            0 <= addr < GPR_ADDR_SUP or SFR_ADDR_MIN <= addr < DATA_ADDR_SUP
            0 <= value <= 255
        post:
            self[addr] == value
        """

        assert(0 <= addr < self.GPR_ADDR_SUP or \
               self.SFR_ADDR_MIN <= addr < self.DATA_ADDR_SUP)
        assert(0 <= value <= 255)
        self.__storage[addr] = value

    def __getitem__(self, addr):
        """get byte from memory cell defined with address 'addr'

        pre:
            0 <= addr < GPR_ADDR_SUP or SFR_ADDR_MIN <= addr < DATA_ADDR_SUP
        """

        assert(0 <= addr < self.GPR_ADDR_SUP or \
               self.SFR_ADDR_MIN <= addr < self.DATA_ADDR_SUP)
        return self.__storage.setdefault(addr, 0)


class PICmicro(object):

    """PIC18F microcontroller definition
    
    inv: 
        0 <= self.pc < PC_SUP
        isinstance(self.data, DataMemory)
    """

    # named addresses of SFRs
    WREG = 0xfe8

    def __init__(self):
        self.__pc = 0
        self.data = DataMemory()

    @property
    def pc(self):
        return self.__pc
    @pc.setter
    def pc(self, value):
        assert(0 <= value < PC_SUP)
        self.__pc = value

    @property
    def wreg(self):
        return self.data[self.WREG]
    @wreg.setter
    def wreg(self, value):
        self.data[self.WREG] = value
