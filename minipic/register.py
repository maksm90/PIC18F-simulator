"""
Definition of registers
"""

# special function registers addresses contants
WREG, STATUS, BSR = 0xfe8, 0xfd8, 0xfe0

class Register:
    """ Abstract class of register with bit-vector operations support """
    def put(self, value):
        raise NotImplementedError()
    def get(self):
        raise NotImplementedError()
    def __setitem__(self, i, bit):
        raise NotImplementedError()
    def __getitem__(self, i):
        raise NotImplementedError()

class PC: 
    """ Program counter """
    MAX_VALUE = 0x200000
    def __init__(self):
        self.value = 0
    def inc(self, delta):
        self.value = (self.value + delta) % self.MAX_VALUE

class ByteRegister(Register):
    """ Concrete class of register storing byte value """
    def __init__(self):
        self.value = 0
    def put(self, value):
        assert 0 <= value <= 0xff
        self.value = value
    def get(self):
        return self.value
    def __setitem__(self, i, bit):
        assert (0 <= i <= 7) and (bit in (0, 1))
        bit_pattern = 1 << i
        self.value = (self.value & ~bit_pattern) | (bit << i)
    def __getitem__(self, i):
        assert 0 <= i <= 7
        return (self.value & (1 << i)) >> i;

class Status(ByteRegister):
    """ Status register """
    def put(self, value):
        pass
    def __setitem__(self, i, bit):
        pass
    def put_N(self, bit):
        pass
    def put_OV(self, bit):
        pass
    def put_Z(self, bit):
        pass
    def put_DC(self, bit):
        pass
    def put_C(self, bit):
        pass
