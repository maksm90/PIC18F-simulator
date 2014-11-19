"""
Definition of basic components of PIC18F simulator: core, data memory, program memory, etc
"""

# limit parameters of PICmicro
PC_SUP = 0x200000

class ByteCell:
    """Memory cell for storing byte value"""
    def __init__(self, value=0):
        """value: byte value of cell (integer between 0-255)"""
        self.value = value

class StatusCell(ByteCell):
    """Memory cell for storing status flags"""
    pass


class DataMemory:
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
        self.wref = ByteCell()
        self.status = StatusCell()
        self.bsr = ByteCell()

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
        return self.__storage.setdefault(addr, ByteCell())

    @property
    def wreg(self):
        return self.data[self.WREG]
    @wreg.setter
    def wreg(self, value):
        self.data[self.WREG] = value


class PICmicro(object):

    """PIC18F microcontroller definition
    
    inv: 
        0 <= self.pc < PC_SUP
        isinstance(self.data, DataMemory)
    """

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
