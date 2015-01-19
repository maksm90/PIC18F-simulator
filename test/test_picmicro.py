import unittest
from picmicro import RegularReg, StatusReg
from picmicro import DataMemory


class TestRegularReg(unittest.TestCase):
    """Test RegularReg class's methods"""

    def setUp(self):
        self.reg = RegularReg()

    def test_add(self):
        """Test addition"""

        # standart test case
        self.reg.add(1)
        self.assertEqual(self.reg.value, 1)

        # test without changing of status
        status = StatusReg()
        self.reg.add(1, status)
        self.assertEqual(status.value, 0)

        # test decimal carry
        self.reg.add(0xf, status)
        self.assertEqual(status.value, 0b10)

        # test overflow and negative result
        self.reg.add(0x70, status)
        self.assertEqual(status.value, 0b11000)

        # test carry, decimal carry and zero result
        self.reg.add(0x7f, status)
        self.assertEqual(status.value, 0b111)

    def test_sub(self):
        pass


class TestDataMemory(unittest.TestCase):
    """Test DataMemory access methods"""

    def setUp(self):
        self.data = DataMemory()

    def testSetGetItem(self):
        self.data[0] = 10
        self.assertEqual(self.data[0].value, 10)


if __name__ == '__main__':
    unittest.main()
