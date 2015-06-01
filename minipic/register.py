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
    def __init__(self, addr, trace):
        self.value = 0
        self.addr = addr
        self.trace = trace
    def put(self, value):
        assert 0 <= value <= 0xff
        self.value = value
        self.trace.add_event(('register_write', self.addr, value))
    def get(self):
        self.trace.add_event(('register_read', self.addr, self.value))
        return self.value
    def __setitem__(self, i, bit):
        assert (0 <= i <= 7) and (bit in (0, 1))
        bit_pattern = 1 << i
        self.value = (self.value & ~bit_pattern) | (bit << i)
        self.trace.add_event(('register_write_bit', self.addr, i, bit))
    def __getitem__(self, i):
        assert 0 <= i <= 7
        bit = (self.value & (1 << i)) >> i
        self.trace.add_event(('register_read_bit', self.addr, i, bit))
        return bit

class Status(ByteRegister):
    """ Status register """
    def __init__(self, trace):
        ByteRegister.__init__(self, STATUS, trace)
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
