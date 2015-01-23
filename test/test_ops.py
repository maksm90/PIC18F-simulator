import unittest
import op
from picmicro import PICmicro

class TestAllOps(unittest.TestCase):
    def setUp(self):
        self.pic = PICmicro()

    def testAddition(self):
        op._add(self.pic, 0, 0)
        self.assertEqual(self.pic.data[0], 0)
        self.assertEqual(self.pic.status, op.Z)

        op._add(self.pic, 0, 10)
        self.assertEqual(self.pic.data[0], 10)
        self.assertEqual(self.pic.status, 0)

        op._add(self.pic, 0, 0xf)
        self.assertEqual(self.pic.data[0], 25)
        self.assertEqual(self.pic.status, op.DC)

        op._add(self.pic, 0, 0x70)
        self.assertEqual(self.pic.data[0], 0x89)
        self.assertEqual(self.pic.status, op.OV | op.N)

        op._add(self.pic, 0, 0x80)
        self.assertEqual(self.pic.data[0], 0x09)
        self.assertEqual(self.pic.status, op.C | op.OV)

    def testAddlw(self):
        self.pic.wreg = 0x10
        op.addlw(self.pic, 0x15)
        self.assertEqual(self.pic.wreg, 0x25)
        self.assertEqual(self.pic.status, 0)

    def testAddwf(self):
        self.pic.wreg = 0x17
        self.pic.data[0] = 0xc2
        op.addwf(self.pic, 0, 0, 0)
        self.assertEqual(self.pic.wreg, 0xd9)
        self.assertEqual(self.pic.data[0], 0xc2)

    def testAddwfc(self):
        self.pic.setStatusBits(op.C)
        self.pic.data[0] = 0x4d
        self.pic.wreg = 0x02
        op.addwfc(self.pic, 0, 0, 1)
        self.assertEqual(self.pic.status & op.C, 0)
        self.assertEqual(self.pic.data[0], 0x4d)
        self.assertEqual(self.pic.wreg, 0x50)


if __name__ == '__main__':
    unittest.main()
