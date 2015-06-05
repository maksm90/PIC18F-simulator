import socket
import threading
from register import ByteRegister, PORTA, PORTB

def _run_port_thread(regs, pin_state, trace):
    """ Inner executable procedure of thread of port """
    port, tris, pin = regs
    if pin_state.direction == 'in':
        while 1:
            s_bit = pin_state.conn_socket.recv(8)
            if not s_bit:
                break
            bit = int(s_bit[:1], 2)
            trace.add_event(('bit_receive', port.addr, pin, bit))
            if tris[pin] == 1:
                port[pin] = bit
    elif pin_state.direction == 'out':
        while 1:
            bit = port.get_modified_pin(pin)
            if tris[pin] == 0:
                sent_num = pin_state.conn_socket.send(str(bit))
                if sent_num == 0:
                    break
                trace.add_event(('bit_send', port.addr, pin, bit))
    pin_state.conn_socket.close()
    pin_state.release()
    trace.add_event(('fail_connect_port', port.addr, pin))

class PinState:
    """ State of connection at pin """
    def __init__(self):
        self.conn_socket = None
        self.direction = None
        self.conn_type = None
        self.sync_socket = None
    def release(self):
        self.conn_socket = None
    def released(self):
        return self.conn_socket == None

def _run_server(port_num, port_tris_regs, trace):
    """ Procedure for running tcp server for receiving connections to ports """

    # init states of io ports
    pins_states = {
            'ra': [PinState()] * 8,
            'rb': [PinState()] * 8
            }

    # init tcp server
    listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listen_socket.bind(('', port_num))
    listen_socket.listen(1)
    while 1:

        # receive incoming tcp connections
        (conn_socket, client_addr) = listen_socket.accept()
        data = conn_socket.recv(1024)
        if not data:
            conn_socket.close()
            continue
        tokens = data.lower().split()
        request = tokens[0]

        # if connection request
        if request == 'connect':

            # extract parameters and check pin state
            port, pin = tokens[1][:-1], int(tokens[1][-1])
            dir, conn_type, rest = tokens[2], tokens[3], tokens[4:]
            if not pins_states[port][pin].released():
                conn_socket.send('BUSY')
                conn_socket.close()
                continue

            # init pin state and set it to io_
            pin_state = PinState()
            pin_state.conn_socket = conn_socket
            pin_state.direction = dir
            pin_state.conn_type = conn_type
            pins_states[port][pin] = pin_state
            
            # define port and tris pair of registers
            if port == 'ra':
                port_reg, tris_reg = port_tris_regs[0]
            elif port == 'rb':
                port_reg, tris_reg = port_tris_regs[1]

            # run thread to realize bit streaning through port  
            port_thread = threading.Thread(
                    target=_run_port_thread, 
                    args=((port_reg, tris_reg, pin), 
                          pin_state, 
                          trace))
            port_thread.daemon = True
            port_thread.start()

            # send answer and log connection event
            conn_socket.send('OK')
            trace.add_event(('port_connect', port, pin, dir, conn_type, rest))

        # if request is about synchronizing processes of MC and periphery
        elif request == 'sync_channel':
            # add sync channel
            conn_socket.send('OK')

    listen_socket.close()

class PortA(ByteRegister):
    """ PORTA register of MC """
    def __init__(self, trace):
        ByteRegister.__init__(self, PORTA, trace)
        self.pins_modified = []
        for _ in xrange(8):
            self.pins_modified.append(threading.Event())
    def put(self, value):
        ByteRegister.put(self, value)
        for _ in xrange(8):
            self.pins_modified[i].set()
    def __setitem__(self, i, bit):
        ByteRegister.__setitem__(self, i, bit)
        self.pins_modified[i].set()
    def get_modified_pin(self, i):
        self.pins_modified[i].wait()
        bit = self[i]
        self.pins_modified[i].clear()
        return bit

class PortB(PortA):
    """ PORTB register of MC """
    def __init__(self, trace):
        PortA.__init__(self, trace)

class IOPorts:
    """ System of IO ports of MC """
    INET_PORT_NUM = 8080
    def __init__(self, port_tris_regs, trace):
        server_thread = threading.Thread(
                target=_run_server, 
                args=(self.INET_PORT_NUM, port_tris_regs, trace))
        server_thread.daemon = True
        server_thread.start()
