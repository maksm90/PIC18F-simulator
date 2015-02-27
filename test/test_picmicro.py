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

    def testStatus(self):
        self._testSetGetByte(STATUS, 'status')
        self._testSetGetRegister(STATUS, 0, 'status')
        self._testSetGetRegister(STATUS, WREG, 'status', 'wreg')

    def testBsr(self):
        self._testSetGetByte(BSR, 'bsr')
        self._testSetGetRegister(BSR, 0, 'bsr')
        self._testSetGetRegister(BSR, WREG, 'bsr', 'wreg')


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
