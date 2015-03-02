"""
Definition of basic components of PIC18F simulator

DataMemory: memory for storing General Purpose Registers and Specific Purpose Registers
OutOfDataMemoryAccess: exception raised after access to nonexisting cell 

PICmicro: main class describing core of PIC18F
"""
from piclog import logger
from sfr import *

class OutOfDataMemoryAccess(Exception):
    pass

SFR_ADDR_MIN = 0xf80


class DataMemory:
    """Data memory of PICmicro"""

    DATA_ADDR_SUP = 0x1000
    GPR_ADDR_SUP = 0x300

    def __init__(self, pic):
        """Initialize memory of data that consists of GPRs and SFRs
        pic: core of PIC18F
        """
        self.pic = pic
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
            logger.info('Write 0x%X to data memory by address 0x0x%X' % (byte, addr))
        elif addr >= SFR_ADDR_MIN:
            if addr == WREG:
                self.pic.wreg = byte
            elif addr == STATUS:
                self.pic.status = byte
            elif addr == BSR:
                self.pic.bsr = byte
            elif addr == PCL:
                self.pic.pcl = byte
            elif addr == STKPTR:
                self.pic.stkptr = byte
            elif addr == TOSU:
                self.pic.tosu = byte
            elif addr == TOSH:
                self.pic.tosh = byte
            elif addr == TOSL:
                self.pic.tosl = byte
            elif addr == PRODL:
                self.pic.prodl = byte
            elif addr == PRODH:
                self.pic.prodh = byte
            elif addr == FSR0L:
                self.pic.fsr0l = byte
            elif addr == FSR0H:
                self.pic.fsr0h = byte
            elif addr == FSR1L:
                self.pic.fsr1l = byte
            elif addr == FSR1H:
                self.pic.fsr1h = byte
            elif addr == FSR2L:
                self.pic.fsr2l = byte
            elif addr == FSR2H:
                self.pic.fsr2h = byte
            else:
                logger.info('Write 0x%X to data memory by address 0x%X' % (byte, addr))
                self.pic.sfr[addr - SFR_ADDR_MIN] = byte

    def __getitem__(self, addr):
        """get byte cell from memory at given address
        addr: address of data memory (integer from 0 up to DATA_ADDR_SUP)
        return: byte value associated with input address
        throws: OutOfDataMemoryAccess if addr havn't entered in acceptable interval
        """
        if not (0 <= addr < self.DATA_ADDR_SUP):
            raise OutOfDataMemoryAccess()

        if addr < self.GPR_ADDR_SUP:
            res = self.gpr.setdefault(addr, 0)
            logger.info('Read 0x%X from data memory by address 0x%X' % (res, addr))
            return res
        if addr >= SFR_ADDR_MIN:
            if addr == WREG:
                return self.pic.wreg
            if addr == STATUS:
                return self.pic.status
            if addr == BSR:
                return self.pic.bsr
            if addr == PCL:
                return self.pic.pcl
            if addr == STKPTR:
                return self.pic.stkptr 
            if addr == TOSU:
                return self.pic.tosu 
            if addr == TOSH:
                return self.pic.tosh 
            if addr == TOSL:
                return self.pic.tosl 
            if addr == PRODL:
                return self.pic.prodl 
            if addr == PRODH:
                return self.pic.prodh 
            if addr == FSR0L:
                return self.pic.fsr0l 
            if addr == FSR0H:
                return self.pic.fsr0h 
            if addr == FSR1L:
                return self.pic.fsr1l 
            if addr == FSR1H:
                return self.pic.fsr1h 
            if addr == FSR2L:
                return self.pic.fsr2l 
            if addr == FSR2H:
                return self.pic.fsr2h 
            res = self.pic.sfr[addr - SFR_ADDR_MIN]
            logger.info('Read 0x%X from data memory by address 0x%X' % (res, addr))
            return res
        return 0


class Stack:
    """Stack memory of PIC18F"""
    
    SIZE = 31
    PC_SUP = 0x200000

    def __init__(self):
        """Initialize stack and fast registries of stack"""
        self.storage = [0] * self.SIZE
        self.stkptr = 0
        self.wregs = self.statuss = self.bsrs = 0

    def push(self, value):
        """Push value on top of stack"""
        pass
    
    def pop(self):
        """Pop value from top of stack"""
        return 0

    @property
    def top(self):
        return 0
    @top.setter
    def top(self, value):
        assert 0 <= value < PC_SUP
        pass


class PICmicro(object):
    """PIC18F microcontroller definition"""

    ADDR_MASK = 0x1fffff
    N_SFRs = 0x80

    def __init__(self):
        """Initialize state of PIC18F"""
        self.__pc = 0                                       # program counter
        self.sfr = [0] * self.N_SFRs                        # specific purpose registers
        self.data = DataMemory(self)                        # addressable memory
        self.stack = Stack()                                # stack

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
        self.sfr[STATUS - SFR_ADDR_MIN] &= ~affected_bit_mask & 0x1f
        self.sfr[STATUS - SFR_ADDR_MIN] |= bits & affected_bit_mask

    @property
    def wreg(self):
        byte = self.sfr[WREG - SFR_ADDR_MIN]
        logger.info('Read 0x%X from WREG' % byte)
        return byte
    @wreg.setter
    def wreg(self, value):
        assert 0 <= value <= 0xff
        logger.info('Write 0x%X to WREG' % value)
        self.sfr[WREG - SFR_ADDR_MIN] = value

    @property
    def status(self):
        byte = self.sfr[STATUS - SFR_ADDR_MIN]
        logger.info('Read 0x%X from STATUS' % byte)
        return byte
    @status.setter
    def status(self, value):
        assert 0 <= value <= 0xff
        logger.info('Write 0x%X to STATUS' % value)
        self.sfr[STATUS - SFR_ADDR_MIN] = value

    @property
    def bsr(self):
        byte = self.sfr[BSR - SFR_ADDR_MIN] & 0xf
        logger.info('Read 0x%X from BSR' % byte)
        return byte
    @bsr.setter
    def bsr(self, value):
        assert 0 <= value <= 0xff
        logger.info('Write 0x%X to BSR' % value)
        self.sfr[BSR - SFR_ADDR_MIN] = value

    @property
    def stkptr(self):
        return 0
    @stkptr.setter
    def stkptr(self, value):
        assert 0 <= value < 32
        pass

    @property
    def tosu(self):
        byte = (self.stack.top & 0xff0000) >> 16
        logger.info('Read 0x%X from TOSU' % byte)
        return byte
    @tosu.setter
    def tosu(setter, value):
        assert 0 <= value <= 0x1f
        logger.info('Write 0x%X to TOSU' % value)
        self.stack.top = self.stack.top | 0xff0000 & (value << 16)

    @property
    def tosh(self):
        byte = (self.stack.top & 0xff00) >> 8
        logger.info('Read 0x%X from TOSH' % byte)
        return byte
    @tosh.setter
    def tosh(setter, value):
        assert 0 <= value <= 0xff
        logger.info('Write 0x%X to TOSH' % value)
        self.stack.top = self.stack.top | 0xff00 & (value << 8) 

    @property
    def tosl(self):
        byte = self.stack.top & 0xff
        logger.info('Read 0x%X from TOSL' % byte)
        return byte
    @tosl.setter
    def tosl(setter, value):
        assert 0 <= value <= 0xff
        logger.info('Write 0x%X to TOSL' % value)
        self.stack.top = self.stack.top | 0xff & value

    @property
    def pcl(self):
        return self.pc & 0xff
    @pcl.setter
    def pcl(self, value):
        assert 0 <= value <= 0xff
        logger.info('Write 0x%X to PCL' % value)
        self.__pc = (self.pc & 0xf00) | value

    @property
    def prodl(self):
        byte = self.sfr[PRODL - SFR_ADDR_MIN]
        logger.info('Read 0x%X from PRODL' % byte)
        return byte
    @prodl.setter
    def prodl(self, value):
        assert 0 <= value <= 0xff
        logger.info('Write 0x%X to PRODL' % value)
        self.sfr[PRODL - SFR_ADDR_MIN] = value

    @property
    def prodh(self):
        byte = self.sfr[PRODH - SFR_ADDR_MIN]
        logger.info('Read 0x%X from PRODH' % byte)
        return byte
    @prodh.setter
    def prodh(self, value):
        assert 0 <= value <= 0xff
        logger.info('Write 0x%X to PRODH' % value)
        self.sfr[PRODH - SFR_ADDR_MIN] = value

    @property
    def fsr0l(self):
        byte = self.sfr[FSR0L - SFR_ADDR_MIN]
        logger.info('Read 0x%X from FSR0L' % byte)
        return byte
    @fsr0l.setter
    def fsr0l(self, value):
        assert 0 <= value <= 0xff
        logger.info('Write 0x%X to FSR0L' % value)
        self.sfr[FSR0L - SFR_ADDR_MIN] = value

    @property
    def fsr0h(self):
        byte = self.sfr[FSR0H - SFR_ADDR_MIN]
        logger.info('Read 0x%X from FSR0H' % byte)
        return byte
    @fsr0h.setter
    def fsr0h(self, value):
        assert 0 <= value <= 0xff
        logger.info('Write 0x%X to FSR0H' % value)
        self.sfr[FSR0H - SFR_ADDR_MIN] = value

    @property
    def fsr1l(self):
        byte = self.sfr[FSR1L - SFR_ADDR_MIN]
        logger.info('Read 0x%X from FSR1L' % byte)
        return byte
    @fsr1l.setter
    def fsr1l(self, value):
        assert 0 <= value <= 0xff
        logger.info('Write 0x%X to FSR1L' % value)
        self.sfr[FSR1L - SFR_ADDR_MIN] = value

    @property
    def fsr1h(self):
        byte = self.sfr[FSR1H - SFR_ADDR_MIN]
        logger.info('Read 0x%X from FSR1H' % byte)
        return byte
    @fsr1h.setter
    def fsr1h(self, value):
        assert 0 <= value <= 0xff
        logger.info('Write 0x%X to FSR1H' % value)
        self.sfr[FSR1H - SFR_ADDR_MIN] = value
 
    @property
    def fsr2l(self):
        byte = self.sfr[FSR2L - SFR_ADDR_MIN]
        logger.info('Read 0x%X from FSR2L' % byte)
        return byte
    @fsr2l.setter
    def fsr2l(self, value):
        assert 0 <= value <= 0xff
        logger.info('Write 0x%X to FSR2L' % value)
        self.sfr[FSR2L - SFR_ADDR_MIN] = value
 
    @property
    def fsr2h(self):
        byte = self.sfr[FSR2H - SFR_ADDR_MIN]
        logger.info('Read 0x%X from FSR2H' % byte)
        return byte
    @fsr2h.setter
    def fsr2h(self, value):
        assert 0 <= value <= 0xff
        logger.info('Write 0x%X to FSR2H' % value)
        self.sfr[FSR2H - SFR_ADDR_MIN] = value
