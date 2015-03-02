import unittest
from picmicro import DataMemory, PICmicro
from sfr import *


class TestDataMemory(unittest.TestCase):
    """Test DataMemory access methods"""

    def setUp(self):
        self.data = DataMemory(PICmicro())

    def _testSetGetByte(self, addr, name=None):
        self.data[addr] = 10
        self.assertEqual(self.data[addr], 10)
        if name != None:
            self.assertEqual(self.data.pic.__getattribute__(name), 10)

    def _testSetGetRegister(self, addr1, addr2, name1=None, name2=None):
        self.data[addr2] = 0x10
        self.data[addr1] = self.data[addr2]
        self.assertEqual(self.data[addr1], self.data[addr2])
        if name1 != None:
            self.assertEqual(self.data.pic.__getattribute__(name1),
                             self.data[addr2])
        if name2 != None:
            self.assertEqual(self.data.pic.__getattribute__(name2),
                             self.data[addr1])
        if name1 != None and name2 != None:
            self.assertEqual(self.data.pic.__getattribute__(name2),
                             self.data.pic.__getattribute__(name1))

    def testSetGetForGPR(self):
        self._testSetGetByte(100)
        self._testSetGetRegister(100, 200)

    def testWreg(self):
        self._testSetGetByte(WREG, 'wreg')
        self._testSetGetRegister(WREG, 0, 'wreg')
        self._testSetGetRegister(WREG, BSR, 'wreg', 'bsr')

    def testBsr(self):
        self.data.pic.bsr = 0x12
        self.assertEqual(self.data.pic.bsr, 0x2)
        self.assertEqual(self.data[BSR], 0x2)
        self.data[BSR] = 0x15
        self.assertEqual(self.data.pic.bsr, 0x5)
        self.assertEqual(self.data[BSR], 0x5)

    def testSFR(self):
        sfrs = [(STATUS, 'status'),
                (PCL, 'pcl'),
                (PRODL, 'prodl'),
                (PRODH, 'prodh'),
                (FSR0L, 'fsr0l'),
                (FSR0H, 'fsr0h'),
                (FSR1L, 'fsr1l'),
                (FSR1H, 'fsr1h'),
                (FSR2L, 'fsr2l'),
                (FSR2H, 'fsr2h')]

        for addr, name in sfrs:
            #print(name)
            self._testSetGetByte(addr, name)
            self._testSetGetRegister(addr, 0, name)
            self._testSetGetRegister(addr, WREG, name, 'wreg')
  

class TestStack(unittest.TestCase):
    """Test Stack memory"""
    pass


class TestPICmicro(unittest.TestCase):
    """Test core of PIC18F"""

    def setUp(self):
        self.pic = PICmicro()

    def testIncPC(self):
        self.pic.incPC(2)
        self.assertEqual(self.pic.pc, 2)
        self.pic.incPC(10)
        self.assertEqual(self.pic.pc, 12)

    def testAffectStatusBits(self):
        self.pic.affectStatusBits(0, 0b11111)
        self.assertEqual(self.pic.status, 0)
        self.pic.affectStatusBits(0b00110, 0b01100)
        self.assertEqual(self.pic.status, 0b100)


if __name__ == '__main__':
    unittest.main()
