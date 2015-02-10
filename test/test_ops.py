import unittest
import op
from picmicro import PICmicro

class TestAllOps(unittest.TestCase):
    def setUp(self):
        self.pic = PICmicro()

    def testAddition(self):
        op._add(self.pic, 0, 0, 0)
        self.assertEqual(self.pic.data[0], 0)
        self.assertEqual(self.pic.status, op.Z)

        op._add(self.pic, 0, 0, 10)
        self.assertEqual(self.pic.data[0], 10)
        self.assertEqual(self.pic.status, 0)

        op._add(self.pic, 0, 10, 0xf)
        self.assertEqual(self.pic.data[0], 25)
        self.assertEqual(self.pic.status, op.DC)

        op._add(self.pic, 0, 25, 0x70)
        self.assertEqual(self.pic.data[0], 0x89)
        self.assertEqual(self.pic.status, op.OV | op.N)

        op._add(self.pic, 0, 0x89, 0x80)
        self.assertEqual(self.pic.data[0], 0x09)
        self.assertEqual(self.pic.status, op.C | op.OV)

    def testConjuction(self):
        op._and(self.pic, 0, 0, 0)
        self.assertEqual(self.pic.data[0], 0)
        self.assertEqual(self.pic.status, op.Z)

        op._and(self.pic, 0, 0xff, 0xf)
        self.assertEqual(self.pic.data[0], 0xf)
        self.assertEqual(self.pic.status, 0)

        op._and(self.pic, 0, 0xf0, 0x8f)
        self.assertEqual(self.pic.data[0], 0x80)
        self.assertEqual(self.pic.status, op.N)

    def testDisjunction(self):
        op._ior(self.pic, op.WREG, 0, 0)
        self.assertEqual(self.pic.wreg, 0)
        self.assertEqual(self.pic.status, op.Z)

        op._ior(self.pic, op.WREG, 0, 0xf)
        self.assertEqual(self.pic.wreg, 0xf)
        self.assertEqual(self.pic.status, 0)

        op._ior(self.pic, op.WREG, 0xf, 0x80)
        self.assertEqual(self.pic.wreg, 0x8f)
        self.assertEqual(self.pic.status, op.N)

    def testExclusiveDisjunction(self):
        op._xor(self.pic, op.WREG, 0, 0)
        self.assertEqual(self.pic.wreg, 0)
        self.assertEqual(self.pic.status, op.Z)

        op._xor(self.pic, op.WREG, 0, 0xf)
        self.assertEqual(self.pic.wreg, 0xf)
        self.assertEqual(self.pic.status, 0)

        op._xor(self.pic, op.WREG, 0xf7, 0xf)
        self.assertEqual(self.pic.wreg, 0xf8)
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
        self.pic.affectStatusBits(op.C, op.C)
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
        self.pic.data[0] = 0xfe
        op.incfsz(self.pic, 0, 1, 0)
        self.assertEqual(self.pic.data[0], 0xff)
        self.assertEqual(self.pic.pc, 0)
        op.incfsz(self.pic, 0, 0, 0)
        self.assertEqual(self.pic.data[0], 0xff)
        self.assertEqual(self.pic.wreg, 0)
        self.assertEqual(self.pic.pc, 2)

    def testInfsnz(self):
        self.pic.data[0] = 0xfe
        op.infsnz(self.pic, 0, 1, 0)
        self.assertEqual(self.pic.data[0], 0xff)
        self.assertEqual(self.pic.pc, 2)
        op.infsnz(self.pic, 0, 0, 0)
        self.assertEqual(self.pic.data[0], 0xff)
        self.assertEqual(self.pic.wreg, 0)
        self.assertEqual(self.pic.pc, 2)

    def testIorwf(self):
        self.pic.data[0] = 0x13
        self.pic.wreg = 0x91
        op.iorwf(self.pic, 0, 0, 1)
        self.assertEqual(self.pic.data[0], 0x13)
        self.assertEqual(self.pic.wreg, 0x93)
        self.assertEqual(self.pic.status, op.N)

        self.pic.data[0] = 0
        self.pic.wreg = 0
        op.iorwf(self.pic, 0, 1, 0)
        self.assertEqual(self.pic.data[0], 0)
        self.assertEqual(self.pic.wreg, 0)
        self.assertEqual(self.pic.status, op.Z)

    def testMovf(self):
        self.pic.wreg = 0xff
        self.pic.data[0] = 0x22
        op.movf(self.pic, 0, 0, 0)
        self.assertEqual(self.pic.wreg, 0x22)
        self.assertEqual(self.pic.data[0], 0x22)

        self.pic.data[0] = 0x33
        op.movf(self.pic, 0, 1, 0)
        self.assertEqual(self.pic.wreg, 0x22)
        self.assertEqual(self.pic.data[0], 0x33)

    def testMovff(self):
        self.pic.data[0] = 1
        self.pic.data[1] = 2
        op.movff(self.pic, 0, 1)
        self.assertEqual(self.pic.data[1], 1)

        self.assertRaises(AssertionError, op.movff, self.pic, op.PCL, 0)
        self.assertRaises(AssertionError, op.movff, self.pic, op.TOSL, 0)
        self.assertRaises(AssertionError, op.movff, self.pic, op.TOSH, 0)
        self.assertRaises(AssertionError, op.movff, self.pic, op.TOSU, 0)

    def testMovwf(self):
        self.pic.wreg = 0x4f
        self.pic.data[0xff] = 0xff
        op.movwf(self.pic, 0, 0)
        self.assertEqual(self.pic.wreg, 0x4f)
        self.assertEqual(self.pic.data[0], 0x4f)

        self.pic.bsr = 1
        op.movwf(self.pic, 0, 1)
        self.assertEqual(self.pic.data[0x100], 0x4f)

    def testMulwf(self):
        self.pic.data[0] = 0xb5
        self.pic.wreg = 0xc4
        op.mulwf(self.pic, 0, 1)
        self.assertEqual(self.pic.wreg, 0xc4)
        self.assertEqual(self.pic.data[0], 0xb5)
        self.assertEqual(self.pic.prodl, 0x94)
        self.assertEqual(self.pic.prodh, 0x8a)

    def testNegf(self):
        self.pic.data[0] = 0x3a
        op.negf(self.pic, 0, 1)
        self.assertEqual(self.pic.data[0], 0xc6)
        self.assertEqual(self.pic.status, op.N)

        op.negf(self.pic, 0, 1)
        self.assertEqual(self.pic.data[0], 0x3a)
        self.assertEqual(self.pic.status, 0)

        self.pic.data[0] = 0
        op.negf(self.pic, 0, 1)
        self.assertEqual(self.pic.data[0], 0)
        self.assertEqual(self.pic.status, op.C | op.Z | op.DC)

        self.pic.data[0] = 0x80
        op.negf(self.pic, 0, 1)
        self.assertEqual(self.pic.data[0], 0x80)
        self.assertEqual(self.pic.status, op.DC | op.OV | op.N)

    def testRlcf(self):
        self.pic.data[0] = 0b11100110
        op.rlcf(self.pic, 0, 0, 0)
        self.assertEqual(self.pic.data[0], 0b11100110)
        self.assertEqual(self.pic.wreg, 0b11001100)
        self.assertEqual(self.pic.status, op.C | op.N)

        op.rlcf(self.pic, 0, 1, 0)
        self.assertEqual(self.pic.data[0], 0b11001101)
        self.assertEqual(self.pic.wreg, 0b11001100)
        self.assertEqual(self.pic.status, op.C | op.N)

        self.pic.data[0] = 0x0
        self.pic.affectStatusBits(op.C, 0)
        op.rlcf(self.pic, 0, 0, 0)
        self.assertEqual(self.pic.wreg, 0b0)
        self.assertEqual(self.pic.status, op.Z)

    def testRlncf(self):
        self.pic.data[0] = 0b10101011
        op.rlncf(self.pic, 0, 1, 0)
        self.assertEqual(self.pic.data[0], 0b01010111)
        self.assertEqual(self.pic.status, 0)

        self.pic.data[0] = 0b0
        op.rlncf(self.pic, 0, 1, 0)
        self.assertEqual(self.pic.data[0], 0b0)
        self.assertEqual(self.pic.status, op.Z)

        self.pic.data[0] = 0b01101011
        op.rlncf(self.pic, 0, 1, 0)
        self.assertEqual(self.pic.data[0], 0b11010110)
        self.assertEqual(self.pic.status, op.N)

    def testRrcf(self):
        self.pic.data[0] = 0b11100110
        op.rrcf(self.pic, 0, 0, 0)
        self.assertEqual(self.pic.data[0], 0b11100110)
        self.assertEqual(self.pic.wreg, 0b01110011)
        self.assertEqual(self.pic.status, 0)

        self.pic.data[0] = self.pic.wreg
        op.rrcf(self.pic, 0, 1, 0)
        self.assertEqual(self.pic.data[0], 0b00111001)
        self.assertEqual(self.pic.status, op.C)

        op.rrcf(self.pic, 0, 1, 0)
        self.assertEqual(self.pic.data[0], 0b10011100)
        self.assertEqual(self.pic.status, op.N | op.C)

        self.pic.data[0] = 0
        self.pic.affectStatusBits(op.C, 0)
        op.rrcf(self.pic, 0, 1, 0)
        self.assertEqual(self.pic.data[0], 0b0)
        self.assertEqual(self.pic.status, op.Z)

    def testRrncf(self):
        self.pic.data[0] = 0b11010111
        op.rrncf(self.pic, 0, 1, 0)
        self.assertEqual(self.pic.data[0], 0b11101011)
        self.assertEqual(self.pic.status, op.N)

        self.pic.data[0] = 0b11010111
        op.rrncf(self.pic, 0, 0, 0)
        self.assertEqual(self.pic.data[0], 0b11010111)
        self.assertEqual(self.pic.wreg, 0b11101011)
        self.assertEqual(self.pic.status, op.N)

        self.pic.data[0] = 0b0
        op.rrncf(self.pic, 0, 0, 0)
        self.assertEqual(self.pic.data[0], 0b0)
        self.assertEqual(self.pic.wreg, 0)
        self.assertEqual(self.pic.status, op.Z)

        self.pic.data[0] = 0b10
        op.rrncf(self.pic, 0, 0, 0)
        self.assertEqual(self.pic.data[0], 0b10)
        self.assertEqual(self.pic.wreg, 1)
        self.assertEqual(self.pic.status, 0)

    def testSetf(self):
        self.pic.data[0] = 0x5a
        op.setf(self.pic, 0, 1)
        self.assertEqual(self.pic.data[0], 0xff)

    def testSubfwb(self):
        self.pic.data[0] = 3
        self.pic.wreg = 2
        self.pic.affectStatusBits(op.C, 1)
        op.subfwb(self.pic, 0, 1, 0)
        self.assertEqual(self.pic.data[0], 0xff)
        self.assertEqual(self.pic.wreg, 2)
        self.assertEqual(self.pic.status, op.N)

        self.pic.data[0] = 2
        self.pic.wreg = 5
        self.pic.affectStatusBits(op.C, 1)
        op.subfwb(self.pic, 0, 0, 0)
        self.assertEqual(self.pic.data[0], 2)
        self.assertEqual(self.pic.wreg, 3)
        self.assertEqual(self.pic.status, op.C | op.DC)

        self.pic.data[0] = 1
        self.pic.wreg = 2
        self.pic.affectStatusBits(op.C, 0)
        op.subfwb(self.pic, 0, 1, 0)
        self.assertEqual(self.pic.data[0], 0)
        self.assertEqual(self.pic.wreg, 2)
        self.assertEqual(self.pic.status, op.C | op.DC | op.Z)

        self.pic.data[0] = 0xef
        self.pic.wreg = 0x70
        self.pic.affectStatusBits(op.C, 0)
        op.subfwb(self.pic, 0, 0, 0)
        self.assertEqual(self.pic.wreg, 0x80)
        self.assertEqual(self.pic.status, op.OV | op.DC | op.N | op.C)

    def testSubwf(self):
        self.pic.data[0] = 3
        self.pic.wreg = 2
        op.subwf(self.pic, 0, 1, 0)
        self.assertEqual(self.pic.data[0], 1)
        self.assertEqual(self.pic.wreg, 2)
        self.assertEqual(self.pic.status, op.C | op.DC)

        self.pic.data[0] = 2
        self.pic.wreg = 2
        op.subwf(self.pic, 0, 0, 0)
        self.assertEqual(self.pic.data[0], 2)
        self.assertEqual(self.pic.wreg, 0)
        self.assertEqual(self.pic.status, op.C | op.Z | op.DC)

        self.pic.data[0] = 1
        self.pic.wreg = 2
        op.subwf(self.pic, 0, 1, 0)
        self.assertEqual(self.pic.data[0], 0xff)
        self.assertEqual(self.pic.wreg, 2)
        self.assertEqual(self.pic.status, op.N)

    def testSubwfb(self):
        self.pic.data[0] = 0x19
        self.pic.wreg = 0xd
        self.pic.affectStatusBits(op.C, 1)
        op.subwfb(self.pic, 0, 1, 0)
        self.assertEqual(self.pic.data[0], 0xc)
        self.assertEqual(self.pic.wreg, 0xd)
        self.assertEqual(self.pic.status, op.C)

        self.pic.data[0] = 0x1b
        self.pic.wreg = 0x1a
        self.pic.affectStatusBits(op.C, 0)
        op.subwfb(self.pic, 0, 0, 0)
        self.assertEqual(self.pic.data[0], 0x1b)
        self.assertEqual(self.pic.wreg, 0x0)
        self.assertEqual(self.pic.status, op.C | op.DC | op.Z)

        self.pic.data[0] = 0x03
        self.pic.wreg = 0x0e
        self.pic.affectStatusBits(op.C, 1)
        op.subwfb(self.pic, 0, 1, 0)
        self.assertEqual(self.pic.data[0], 0xf5)
        self.assertEqual(self.pic.wreg, 0x0e)
        self.assertEqual(self.pic.status, op.N)

    def testSwapf(self):
        self.pic.data[0] = 0x53
        op.swapf(self.pic, 0, 1, 0)
        self.assertEqual(self.pic.data[0], 0x35)

        op.swapf(self.pic, 0, 0, 0)
        self.assertEqual(self.pic.data[0], 0x35)
        self.assertEqual(self.pic.wreg, 0x53)

    def testTstfsz(self):
        self.pic.data[0] = 0
        op.tstfsz(self.pic, 0, 0)
        self.assertEqual(self.pic.pc, 2)

        self.pic.data[0] = 1
        op.tstfsz(self.pic, 0, 0)
        self.assertEqual(self.pic.pc, 2)

    def testXorwf(self):
        self.pic.data[0] = 0xaf
        self.pic.wreg = 0xb5
        op.xorwf(self.pic, 0, 1, 1)
        self.assertEqual(self.pic.wreg, 0xb5)
        self.assertEqual(self.pic.data[0], 0x1a)

        self.pic.wreg = 0x1a
        op.xorwf(self.pic, 0, 0, 1)
        self.assertEqual(self.pic.wreg, 0x0)
        self.assertEqual(self.pic.data[0], 0x1a)
        self.assertEqual(self.pic.status, op.Z)

        self.pic.wreg = 0xaa
        op.xorwf(self.pic, 0, 0, 1)
        self.assertEqual(self.pic.wreg, 0xb0)
        self.assertEqual(self.pic.data[0], 0x1a)
        self.assertEqual(self.pic.status, op.N)

    def testBcf(self):
        self.pic.data[0] = 0xc7
        op.bcf(self.pic, 0, 7, 0)
        self.assertEqual(self.pic.data[0], 0x47)

        self.pic.data[0x100] = 0xf7
        self.pic.bsr = 1
        op.bcf(self.pic, 0, 5, 1)
        self.assertEqual(self.pic.data[0x100], 0xd7)

    def testBsf(self):
        self.pic.data[0] = 0x0a
        op.bsf(self.pic, 0, 7, 1)
        self.assertEqual(self.pic.data[0], 0x8a)

        self.pic.data[0] = 0x07
        op.bsf(self.pic, 0, 5, 0)
        self.assertEqual(self.pic.data[0], 0x27)

    def testBtfsc(self):
        self.pic.data[0] = 0x7a
        op.btfsc(self.pic, 0, 7, 0)
        self.assertEqual(self.pic.pc, 2)

        self.pic.data[0] = 0x67
        op.btfsc(self.pic, 0, 5, 0)
        self.assertEqual(self.pic.pc, 2)

    def testBtfss(self):
        self.pic.data[0] = 0x7a
        op.btfss(self.pic, 0, 7, 0)
        self.assertEqual(self.pic.pc, 0)

        self.pic.data[0] = 0x67
        op.btfss(self.pic, 0, 5, 0)
        self.assertEqual(self.pic.pc, 2)

    def testBtg(self):
        self.pic.data[0] = 0x75
        op.btg(self.pic, 0, 4, 0)
        self.assertEqual(self.pic.data[0], 0x65)

    def testBc(self):
        op.bc(self.pic, 5)
        self.assertEqual(self.pic.pc, 0)

        self.pic.affectStatusBits(op.C, 1)
        op.bc(self.pic, 5)
        self.assertEqual(self.pic.pc, 10)

    def testBn(self):
        op.bn(self.pic, 5)
        self.assertEqual(self.pic.pc, 0)

        self.pic.affectStatusBits(op.N, op.N)
        op.bn(self.pic, 5)
        self.assertEqual(self.pic.pc, 10)

    def testBnc(self):
        op.bnc(self.pic, 5)
        self.assertEqual(self.pic.pc, 10)

        self.pic.affectStatusBits(op.C, 1)
        op.bnc(self.pic, 5)
        self.assertEqual(self.pic.pc, 10)

    def testBnn(self):
        op.bnn(self.pic, 5)
        self.assertEqual(self.pic.pc, 10)

        self.pic.affectStatusBits(op.N, op.N)
        op.bnn(self.pic, 5)
        self.assertEqual(self.pic.pc, 10)

    def testBnov(self):
        op.bnov(self.pic, 5)
        self.assertEqual(self.pic.pc, 10)

        self.pic.affectStatusBits(op.OV, op.OV)
        op.bnov(self.pic, 5)
        self.assertEqual(self.pic.pc, 10)

    def testBnz(self):
        op.bnz(self.pic, 5)
        self.assertEqual(self.pic.pc, 10)

        self.pic.affectStatusBits(op.Z, op.Z)
        op.bnz(self.pic, 5)
        self.assertEqual(self.pic.pc, 10)

    def testBov(self):
        op.bov(self.pic, 5)
        self.assertEqual(self.pic.pc, 0)

        self.pic.affectStatusBits(op.OV, op.OV)
        op.bov(self.pic, 5)
        self.assertEqual(self.pic.pc, 10)

    def testBra(self):
        op.bra(self.pic, 5)
        self.assertEqual(self.pic.pc, 10)

    def testBz(self):
        op.bz(self.pic, 5)
        self.assertEqual(self.pic.pc, 0)

        self.pic.affectStatusBits(op.Z, op.Z)
        op.bz(self.pic, 5)
        self.assertEqual(self.pic.pc, 10)

    @unittest.skip("opertion is not realized yet")
    def testCall(self):
        self.assertTrue(False)

    @unittest.skip("opertion is not realized yet")
    def testDaw(self):
        pass

    @unittest.skip("opertion is not realized yet")
    def testGoto(self):
        pass

    @unittest.skip("opertion is not realized yet")
    def testPop(self):
        pass

    @unittest.skip("opertion is not realized yet")
    def testPush(self):
        pass

    @unittest.skip("opertion is not realized yet")
    def testRcall(self):
        pass

    @unittest.skip("opertion is not realized yet")
    def testReset(self):
        pass

    @unittest.skip("opertion is not realized yet")
    def testRetfie(self):
        pass

    @unittest.skip("opertion is not realized yet")
    def testRetlw(self):
        pass

    @unittest.skip("opertion is not realized yet")
    def testReturn(self):
        pass

    def testAnd(self):
        self.pic.wreg = 0xa3
        op.andlw(self.pic, 0x5f)
        self.assertEqual(self.pic.wreg, 0x03)
        self.assertEqual(self.pic.status, 0)

        op.andlw(self.pic, 0)
        self.assertEqual(self.pic.wreg, 0)
        self.assertEqual(self.pic.status, op.Z)

        self.pic.wreg = 0xa3
        op.andlw(self.pic, 0x80)
        self.assertEqual(self.pic.wreg, 0x80)
        self.assertEqual(self.pic.status, op.N)

    def testIorlw(self):
        self.pic.wreg = 0x9a
        op.iorlw(self.pic, 0x35)
        self.assertEqual(self.pic.wreg, 0xbf)
        self.assertEqual(self.pic.status, op.N)

        self.pic.wreg = 0
        op.iorlw(self.pic, 0)
        self.assertEqual(self.pic.wreg, 0)
        self.assertEqual(self.pic.status, op.Z)

        op.iorlw(self.pic, 0x1f)
        self.assertEqual(self.pic.wreg, 0x1f)
        self.assertEqual(self.pic.status, 0)

    def testLfsr(self):
        op.lfsr(self.pic, 2, 0x3ab)
        self.assertEqual(self.pic.fsr2l, 0xab)
        self.assertEqual(self.pic.fsr2h, 0x03)

        op.lfsr(self.pic, 1, 0x3ab)
        self.assertEqual(self.pic.fsr1l, 0xab)
        self.assertEqual(self.pic.fsr1h, 0x03)

        op.lfsr(self.pic, 0, 0x3ab)
        self.assertEqual(self.pic.fsr0l, 0xab)
        self.assertEqual(self.pic.fsr0h, 0x03)

    def testMovlb(self):
        self.pic.bsr = 0x02
        op.movlb(self.pic, 5)
        self.assertEqual(self.pic.bsr, 0x05)

    def testMovlw(self):
        op.movlw(self.pic, 0x5a)
        self.assertEqual(self.pic.wreg, 0x5a)

    def testMullw(self):
        self.pic.wreg = 0xe2
        op.mullw(self.pic, 0xc4)
        self.assertEqual(self.pic.wreg, 0xe2)
        self.assertEqual(self.pic.prodl, 0x08)
        self.assertEqual(self.pic.prodh, 0xad)

    @unittest.skip("opertion is not realized yet")
    def testRetlw(self):
        pass

    def testSublw(self):
        self.pic.wreg = 1
        op.sublw(self.pic, 0x02)
        self.assertEqual(self.pic.wreg, 1)
        self.assertEqual(self.pic.status, op.C | op.DC)

        self.pic.wreg = 2
        op.sublw(self.pic, 0x02)
        self.assertEqual(self.pic.wreg, 0)
        self.assertEqual(self.pic.status, op.C | op.Z | op.DC)

        self.pic.wreg = 3
        op.sublw(self.pic, 0x02)
        self.assertEqual(self.pic.wreg, 0xff)
        self.assertEqual(self.pic.status, op.N)

    def testXorlw(self):
        self.pic.wreg = 0xb5
        op.xorlw(self.pic, 0xaf)
        self.assertEqual(self.pic.wreg, 0x1a)
        self.assertEqual(self.pic.status, 0)

        op.xorlw(self.pic, 0x8f)
        self.assertEqual(self.pic.wreg, 0x95)
        self.assertEqual(self.pic.status, op.N)

        op.xorlw(self.pic, 0x95)
        self.assertEqual(self.pic.wreg, 0)
        self.assertEqual(self.pic.status, op.Z)

    @unittest.skip("function is not realized yet")
    def testTblrdAsk(self):
        pass

    @unittest.skip("function is not realized yet")
    def testTblrdAskPlus(self):
        pass

    @unittest.skip("function is not realized yet")
    def testTblrdPlusAsk(self):
        pass

    @unittest.skip("function is not realized yet")
    def testTblwtAsk(self):
        pass

    @unittest.skip("function is not realized yet")
    def testTblwtAskPlus(self):
        pass

    @unittest.skip("function is not realized yet")
    def testTblwtAskMinus(self):
        pass

    @unittest.skip("function is not realized yet")
    def testTblwtPlusAsk(self):
        pass

if __name__ == '__main__':
    unittest.main()
