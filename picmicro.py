"""
Definition of basic components of PIC18F simulator

DataMemory: memory for storing General Purpose Registers and Specific Purpose Registers
OutOfDataMemoryAccess: exception raised after access to nonexisting cell 

PICmicro: main class describing core of PIC18F
"""
import logging
from sfr import *

logging.basicConfig(format='*** %(levelname)-8s %(message)s', level=logging.INFO)

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
            logging.info('Write 0x0x%X to data memory by address 0x0x%X' % (byte, addr))
        elif addr >= SFR_ADDR_MIN:
            if addr == WREG:
                self.pic.wreg = byte
            elif addr == BSR:
                self.pic.bsr = byte
            elif addr == PCL:
                self.pic.pcl = byte
            else:
                logging.info('Write 0x0x%X to data memory by address 0x0x%X' % (byte, addr))
                self.pic.sfr[addr - SFR_ADDR_MIN] = byte

    def __getitem__(self, addr):
        """get byte cell from memory at given address
        addr: address of data memory (integer from 0 up to DATA_ADDR_SUP)
        return: byte value associated with input address
        throws: OutOfDataMemoryAccess if addr havn't entered in acceptable interval
        """
        if not (0 <= addr < self.DATA_ADDR_SUP):
            raise OutOfDataMemoryAccess()
            if addr == WREG:
                self.pic.wreg = byte
            elif addr == BSR:
                self.pic.bsr = byte
            elif addr == PCL:
                self.pic.pcl = byte

        if addr < self.GPR_ADDR_SUP:
            res = self.gpr.setdefault(addr, 0)
            logging.info('Read 0x0x%X from data memory by address 0x0x%X' % (res, addr))
            return res
        if addr >= SFR_ADDR_MIN:
            if addr == WREG:
                return self.pic.wreg
            if addr == BSR:
                return self.pic.bsr
            if addr == PCL:
                return self.pic.pcl
            res = self.sfr[addr - SFR_ADDR_MIN]
            logging.info('Read 0x%X from data memory by address 0x%X' % (res, addr))
            return res
        return 0


class PICmicro(object):
    """PIC18F microcontroller definition"""

    # indices of SFRs
    WREG = 0x68
    STATUS = 0x58
    BSR = 0x60
    PRODL, PRODH = 0x73, 0x74
    FSR0L, FSR0H, FSR1L, FSR1H, FSR2L, FSR2H = 0x69, 0x6a, 0x61, 0x62, 0x59, 0x5a

    ADDR_MASK = 0x1fffff
    N_SFRs = 0x80

    def __init__(self):
        """Initialize state of PIC18F"""
        self.__pc = 0                                       # program counter
        self.sfr = [0] * self.N_SFRs                        # specific purpose registers
        self.data = DataMemory(self)                        # addressable memory

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
        byte = self.sfr[WREG - SFR_ADDR_MIN]
        logging.info('Read 0x%X from WREG' % byte)
        return byte
    @wreg.setter
    def wreg(self, value):
        assert 0 <= value <= 0xff
        logging.info('Write 0x%X to WREG' % value)
        self.sfr[WREG - SFR_ADDR_MIN] = value

    @property
    def status(self):
        byte = self.sfr[STATUS - SFR_ADDR_MIN]
        logging.info('Read 0x%X from STATUS' % byte)
        return byte
    @status.setter
    def status(self, value):
        assert 0 <= value <= 0xff
        logging.info('Write 0x%X to STATUS' % value)
        self.sfr[STATUS - SFR_ADDR_MIN] = value

    @property
    def bsr(self):
        byte = self.sfr[BSR - SFR_ADDR_MIN] & 0xf
        logging.info('Read 0x%X from BSR' % byte)
        return byte
    @bsr.setter
    def bsr(self, value):
        assert 0 <= value <= 0xff
        logging.info('Write 0x%X to BSR' % value)
        self.sfr[BSR - SFR_ADDR_MIN] = value

    @property
    def pcl(self):
        return self.pc & 0xff
    @pcl.setter
    def pcl(self, value):
        assert 0 <= value <= 0xff
        self.pc = (self.pc & 0xf00) | value


    @property
    def prodl(self):
        return self.sfr[PRODL - SFR_ADDR_MIN]
    @prodl.setter
    def prodl(self, value):
        assert 0 <= value <= 0xff
        self.sfr[PRODL - SFR_ADDR_MIN] = value

    @property
    def prodh(self):
        return self.sfr[PRODH - SFR_ADDR_MIN]
    @prodh.setter
    def prodh(self, value):
        assert 0 <= value <= 0xff
        self.sfr[PRODH - SFR_ADDR_MIN] = value

    @property
    def fsr0l(self):
        return self.sfr[FSR0L - SFR_ADDR_MIN]
    @fsr0l.setter
    def fsr0l(self, value):
        assert 0 <= value <= 0xff
        self.sfr[FSR0L - SFR_ADDR_MIN] = value

    @property
    def fsr0h(self):
        return self.sfr[FSR0H - SFR_ADDR_MIN]
    @fsr0h.setter
    def fsr0h(self, value):
        assert 0 <= value <= 0xff
        self.sfr[FSR0H - SFR_ADDR_MIN] = value

    @property
    def fsr1l(self):
        return self.sfr[FSR1L - SFR_ADDR_MIN]
    @fsr1l.setter
    def fsr1l(self, value):
        assert 0 <= value <= 0xff
        self.sfr[FSR1L - SFR_ADDR_MIN] = value

    @property
    def fsr1h(self):
        return self.sfr[FSR1H - SFR_ADDR_MIN]
    @fsr1h.setter
    def fsr1h(self, value):
        assert 0 <= value <= 0xff
        self.sfr[FSR1H - SFR_ADDR_MIN] = value
 
    @property
    def fsr2l(self):
        return self.sfr[FSR2L - SFR_ADDR_MIN]
    @fsr2l.setter
    def fsr2l(self, value):
        assert 0 <= value <= 0xff
        self.sfr[FSR2L - SFR_ADDR_MIN] = value
 
    @property
    def fsr2h(self):
        return self.sfr[FSR2H - SFR_ADDR_MIN]
    @fsr2h.setter
    def fsr2h(self, value):
        assert 0 <= value <= 0xff
        self.sfr[FSR2H - SFR_ADDR_MIN] = value
