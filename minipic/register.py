"""
Definition of registers
"""

# special function registers addresses contants
WREG, STATUS, BSR = 0xfe8, 0xfd8, 0xfe0
PCL = 0xff9
STKPTR = 0xffc
PORTA, PORTB = 0xf80, 0xf81
TRISA, TRISB = 0xf92, 0xf93

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
        assert bit in (0, 1)
        self.value = (self.value & 0x0f) | (bit << 4)
        self.trace.add_event(('status_set', 'N', bit))
    def put_OV(self, bit):
        assert bit in (0, 1)
        self.value = (self.value & 0x17) | (bit << 3)
        self.trace.add_event(('status_set', 'OV', bit))
    def put_Z(self, bit):
        assert bit in (0, 1)
        self.value = (self.value & 0x1b) | (bit << 2)
        self.trace.add_event(('status_set', 'Z', bit))
    def put_DC(self, bit):
        assert bit in (0, 1)
        self.value = (self.value & 0x1d) | (bit << 1)
        self.trace.add_event(('status_set', 'DC', bit))
    def put_C(self, bit):
        assert bit in (0, 1)
        self.value = (self.value & 0x1e) | bit
        self.trace.add_event(('status_set', 'C', bit))

class Pcl(ByteRegister):
    """ Low byte of PC """
    def __init__(self, pc, trace):
        ByteRegister.__init__(self, PCL, trace)
        self.pc = pc
    def put(self, value):
        ByteRegister.put(self, value)
        self.pc.value = (self.pc.value & ~0xff) | value
    def get(self):
        self.value = self.pc.value & 0xff
        return ByteRegister.get(self)
    def __setitem__(self, i, bit):
        ByteRegister.__setitem__(self, i, bit)
        bit_pattern = 1 << i
        self.pc.value = (self.pc.value & ~bit_pattern) | (bit << i)
    def __getitem__(self, i):
        self.value = self.pc.value & 0xff
        return ByteRegister.__getitem__(self, i)
