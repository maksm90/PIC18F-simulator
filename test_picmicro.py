import unittest
import picmicro


class TestRegularReg(unittest.TestCase):
    def setUp(self):
        self.reg = picmicro.RegularReg()
    def test_add(self):
        self.reg.add(1)
        self.assertEqual(self.reg.value, 1)

        status = picmicro.StatusReg()
        self.reg.add(1, status)
        self.assertEqual(status.value, 0)

        self.reg.add(0xf, status)
        self.assertEqual(status.value, 0b10)

        self.reg.add(0x70, status)
        self.assertEqual(status.value, 0b11000)

        self.reg.add(0x7f, status)
        self.assertEqual(status.value, 0b111)


class TestDataMemory(unittest.TestCase):
    pass


if __name__ == '__main__':
    unittest.main()
