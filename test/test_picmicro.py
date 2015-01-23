import unittest
from picmicro import DataMemory, PICmicro


class TestDataMemory(unittest.TestCase):
    """Test DataMemory access methods"""

    def setUp(self):
        N_SFRs = 0x80
        sfr = [0] * N_SFRs
        self.data = DataMemory(sfr)

    def _testSetGetByte(self, addr):
        self.data[addr] = 10
        self.assertEqual(self.data[addr], 10)

    def _testSetGetRegister(self, addr1, addr2):
        self.data[addr1] = self.data[addr2]
        self.assertEqual(self.data[addr1], self.data[addr2])

    def testSetGetForGPR(self):
        self._testSetGetByte(100)
        self._testSetGetRegister(100, 200)

    def testSetGetForSFR(self):
        WREG = 0xfe8
        BSR = 0xfe0

        self._testSetGetByte(WREG)
        self._testSetGetRegister(WREG, BSR)


class TestPICmicro(unittest.TestCase):
    """Test core of PIC18F"""

    def setUp(self):
        self.pic = PICmicro()

    def testIncPC(self):
        self.pic.incPC(2)
        self.assertEqual(self.pic.pc, 2)
        self.pic.incPC(10)
        self.assertEqual(self.pic.pc, 12)

    @unittest.skip('')
    def testSetStatus(self):
        self.pic.setStatus(0)
        self.assertEqual(self.pic.status, 0)
        self.pic.setStatusBits(0b0101)
        self.assertEqual(self.pic.status, 0x0101)
        self.pic.setStatusBits(0b0010)
        self.assertEqual(self.pic.status, 0x0111)


if __name__ == '__main__':
    unittest.main()
