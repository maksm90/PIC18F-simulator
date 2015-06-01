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

class SFR(ByteRegister):
    """ Special function register class with trace logging support """
    def __init__(self, name, trace):
        ByteRegister.__init__(self)
        self.name = name
        self.trace = trace
    def put(self, value):
        ByteRegister.put(self, value)
        self.trace.add_event(('register_write', 'SFR', self.name, value))
    def get(self):
        value = ByteRegister.get(self)
        self.trace.add_event(('register_read', 'SFR', self.name, value))
        return value
    def __setitem__(self, i, bit):
        ByteRegister.__setitem__(self, i, bit)
        self.trace.add_event(('register_write_bit', 'SFR', self.name, i, bit))
    def __getitem__(self, i):
        bit = ByteRegister.__getitem__(self, i)
        self.trace.add_event(('register_read_bit', 'SFR', self.name, i, bit))
        return bit

class GPR(ByteRegister):
    """ General purpose register class with trace logging support """
    def __init__(self, addr, trace):
        ByteRegister.__init__(self)
        self.addr = addr
        self.trace = trace
    def put(self, value):
        ByteRegister.put(self, value)
        self.trace.add_event(('register_write', 'GPR', self.addr, value))
    def get(self):
        value = ByteRegister.get(self)
        self.trace.add_event(('register_read', 'GPR', self.addr, value))
        return value
    def __setitem__(self, i, bit):
        ByteRegister.__setitem__(self, i, bit)
        self.trace.add_event(('register_write_bit', 'GPR', self.addr, i, bit))
    def __getitem__(self, i):
        bit = ByteRegister.__getitem__(self, i)
        self.trace.add_event(('register_read_bit', 'GPR', self.addr, i, bit))
        return bit

class Status(ByteRegister):
    """ Status register """
    def __init__(self, trace):
        ByteRegister.__init__(self)
        self.trace = trace
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
