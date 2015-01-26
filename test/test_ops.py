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

    def testConjuction(self):
        op._and(self.pic, 0, 0)
        self.assertEqual(self.pic.data[0], 0)
        self.assertEqual(self.pic.status, op.Z)

        self.pic.data[0] = 0xff
        op._and(self.pic, 0, 0xf)
        self.assertEqual(self.pic.data[0], 0xf)
        self.assertEqual(self.pic.status, 0)

        self.pic.data[0] = 0xf0
        op._and(self.pic, 0, 0x8f)
        self.assertEqual(self.pic.data[0], 0x80)
        self.assertEqual(self.pic.status, op.N)

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

        op.addwf(self.pic, 0, 1, 0)
        self.assertEqual(self.pic.wreg, 0xd9)
        self.assertEqual(self.pic.data[0], 0x9b)

    def testAddwfc(self):
        self.pic.setStatusBits(op.C)
        self.pic.data[0] = 0x4d
        self.pic.wreg = 0x02
        op.addwfc(self.pic, 0, 0, 1)
        self.assertEqual(self.pic.status & op.C, 0)
        self.assertEqual(self.pic.data[0], 0x4d)
        self.assertEqual(self.pic.wreg, 0x50)

        op.addwfc(self.pic, 0, 1, 0)
        self.assertEqual(self.pic.wreg, 0x50)
        self.assertEqual(self.pic.data[0], 0x9d)
        self.assertEqual(self.pic.status & op.C, 0)

    def testAndwf(self):
        self.pic.wreg = 0x17
        self.pic.data[0] = 0xc2
        op.andwf(self.pic, 0, 0, 0)
        self.assertEqual(self.pic.wreg, 0x02)
        self.assertEqual(self.pic.data[0], 0xc2)
        self.assertEqual(self.pic.status, 0x0)

        op.andwf(self.pic, 0, 1, 0)
        self.assertEqual(self.pic.wreg, 0x02)
        self.assertEqual(self.pic.data[0], 0x02)

    def testClrf(self):
        self.pic.data[0] = 0xf
        op.clrf(self.pic, 0, 1)
        self.assertEqual(self.pic.data[0], 0)
        self.assertEqual(self.pic.status, op.Z)

    def testCompf(self):
        self.pic.data[0] = 0x13
        op.comf(self.pic, 0, 0, 0)
        self.assertEqual(self.pic.data[0], 0x13)
        self.assertEqual(self.pic.wreg, 0xec)
        self.assertEqual(self.pic.status, op.N)

        self.pic.data[1] = 0xff
        op.comf(self.pic, 1, 1, 1)
        self.assertEqual(self.pic.data[1], 0)
        self.assertEqual(self.pic.wreg, 0xec)
        self.assertEqual(self.pic.status, op.Z)

        self.pic.data[0] = 0xec
        op.comf(self.pic, 0, 0, 0)
        self.assertEqual(self.pic.data[0], 0xec)
        self.assertEqual(self.pic.wreg, 0x13)
        self.assertEqual(self.pic.status, 0)

    def testCpfseq(self):
        op.cpfseq(self.pic, 0, 0)
        self.assertEqual(self.pic.pc, 2)

        self.pic.wreg = 1
        op.cpfseq(self.pic, 0, 0)
        self.assertEqual(self.pic.pc, 2)

    def testCpfsgt(self):
        op.cpfsgt(self.pic, 0, 0)
        self.assertEqual(self.pic.pc, 0)

        self.pic.wreg = 1
        op.cpfsgt(self.pic, 0, 0)
        self.assertEqual(self.pic.pc, 2)

    def testCpfslt(self):
        op.cpfslt(self.pic, 0, 0)
        self.assertEqual(self.pic.pc, 0)

        self.pic.data[0] = 1
        op.cpfslt(self.pic, 0, 0)
        self.assertEqual(self.pic.pc, 2)

    def testDecf(self):
        self.pic.data[0] = 0x01
        op.decf(self.pic, 0, 1, 0)
        self.assertEqual(self.pic.data[0], 0)
        self.assertEqual(self.pic.status, op.Z | op.DC | op.C)

        op.decf(self.pic, 0, 0, 0)
        self.assertEqual(self.pic.data[0], 0)
        self.assertEqual(self.pic.wreg, 0xff)
        self.assertEqual(self.pic.status, op.N)

        self.pic.data[0] = 0x80
        op.decf(self.pic, 0, 1, 0)
        self.assertEqual(self.pic.data[0], 0x7f)
        self.assertEqual(self.pic.status, op.OV | op.C)

    def testDecfsz(self):
        self.pic.data[0] = 0x2
        op.decfsz(self.pic, 0, 1, 0)
        self.assertEqual(self.pic.data[0], 0x1)
        self.assertEqual(self.pic.pc, 0)
        op.decfsz(self.pic, 0, 0, 0)
        self.assertEqual(self.pic.data[0], 0x1)
        self.assertEqual(self.pic.wreg, 0)
        self.assertEqual(self.pic.pc, 2)

    def testDcfsnz(self):
        self.pic.data[0] = 0x2
        op.dcfsnz(self.pic, 0, 1, 0)
        self.assertEqual(self.pic.data[0], 0x1)
        self.assertEqual(self.pic.pc, 2)
        op.dcfsnz(self.pic, 0, 0, 0)
        self.assertEqual(self.pic.data[0], 0x1)
        self.assertEqual(self.pic.wreg, 0)
        self.assertEqual(self.pic.pc, 2)

    def testIncf(self):
        self.pic.data[0] = 0xff
        op.incf(self.pic, 0, 1, 0)
        self.assertEqual(self.pic.data[0], 0)
        self.assertEqual(self.pic.status, op.Z | op.C | op.DC)

        op.incf(self.pic, 0, 0, 0)
        self.assertEqual(self.pic.wreg, 1)
        self.assertEqual(self.pic.status, 0)

        self.pic.data[0] = 0x7f
        op.incf(self.pic, 0, 1, 0)
        self.assertEqual(self.pic.data[0], 0x80)
        self.assertEqual(self.pic.status, op.OV | op.N | op.DC)

    def testIncfsz(self):
        pass
        #self.pic.data[0] = 
    def testInfsnz(self):
        pass

if __name__ == '__main__':
    unittest.main()
