import unittest
import op
from picmicro import PICmicro

class TestAllOps(unittest.TestCase):
    def setUp(self):
        self.pic = PICmicro()
    @unittest.skip("")
    def test_addlw(self):
        self.pic.data.wreg.value = 0x10
        op.addlw(self.pic, 0x15)
        self.assertEqual(self.pic.data.wreg.value, 0x25)
        self.assertEqual(self.pic.data.status.value, 0)


if __name__ == '__main__':
    unittest.main()
