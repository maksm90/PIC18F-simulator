import socket
import threading
from register import ByteRegister, PORTA, PORTB

def _run_port_thread(port_state, trace):
    if port_state.direction == 'in':
        while 1:
            s_bit = port_state.conn_socket.recv(8)
            if not s_bit:
                break
            bit = int(s_bit[:1], 2)
            trace.add_event(('bit_receive', port_state.port_reg.addr, port_state.pin_num, bit))
            if port_state.tris_reg[port_state.pin_num] == 1:
                port_state.port_reg[port_state.pin_num] = bit
    elif port_state.direction == 'out':
        pass
    conn_sock.close()

class IOPortState:
    """ Declaration of IO port state """
    def __init__(self):
        self.port_reg = None
        self.tris_reg = None
        self.pin_num = None
        self.direction = None
        self.conn_socket = None

def _handle_connect_request(conn_socket, request_tokens, io_ports_states, port_tris_regs, trace):
    """ Inner procedure of handling connection request """

    # extract parameters and check pin state
    port, pin = request_tokens[1][:-1], int(request_tokens[1][-1])
    direction, type_conn, rest = request_tokens[2], request_tokens[3], request_tokens[4:]
    if io_ports_states[port][pin] != None:
        conn_socket.send('BUSY')
        conn_socket.close()
        return
    
    # define port and tris pair of registers
    if port == 'ra':
        port_reg, tris_reg = port_tris_regs[0]
    elif port == 'rb':
        port_reg, tris_reg = port_tris_regs[1]

    # get state of port object and complete it
    port_state = io_ports_states[port][pin]
    port_state.direction = direction
    port_state.conn_socket = conn_socket

    # run thread to realize bit streaning through port  
    port_thread = threading.Thread(target=_run_port_thread, args=(port_state, trace))
    port_thread.daemon = True
    port_thread.start()

    # send answer and log connection event
    conn_socket.send('OK')
    trace.add_event(('port_connect', port, pin, direction, type_conn, rest))

def _run_server(port_num, port_tris_regs, trace):
    """ Procedure for running tcp server for receiving connections to ports """

    # init states of io ports
    io_ports_states = {
            'ra': [None] * 8,
            'rb': [None] * 8
            }
    for i in xrange(8):
        io_ports_states['ra'][i] = IOPortState()
        io_ports_states['ra'][i].port_reg = port_tris_regs[0][0]
        io_ports_states['ra'][i].tris_reg = port_tris_regs[0][1]
        io_ports_states['ra'][i].pin_num = i
        io_ports_states['rb'][i] = IOPortState()
        io_ports_states['rb'][i].port_reg = port_tris_regs[1][0]
        io_ports_states['rb'][i].tris_reg = port_tris_regs[1][1]
        io_ports_states['rb'][i].pin_num = i

    # init tcp server
    listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listen_socket.bind(('', port_num))
    listen_socket.listen(1)
    while 1:
        # receive incoming tcp connection
        (conn_socket, client_addr) = listen_socket.accept()
        data = conn_socket.recv(1024)
        if not data:
            conn_socket.close()
            continue
        tokens = data.lower().split()
        request = tokens[0]
        if request == 'connect':
            _handle_connect_request(conn_socket, tokens, io_ports_states, port_tris_regs, trace)
        elif request == 'sync_channel':
            # complement sync channel
            conn_socket.send('OK')
    listen_socket.close()

class PortA(ByteRegister):
    """ PORTA register of MC """
    def __init__(self, trisa_reg, trace):
        ByteRegister.__init__(self, PORTA, trace)
        self.trisa_reg = trisa_reg
        self.pins_modified = []
        for _ in xrange(8):
            self.pins_modified.append(threading.Event())
    def put(self, value):
        for _ in xrange(8):
            self.pins_modified[i].set()
        ByteRegister.put(self, value)
    def __setitem__(self, i, bit):
        self.pins_modified[i].set()
        ByteRegister.__setitem__(self, i, bit)

class PortB(ByteRegister):
    """ PORTB register of MC """
    def __init__(self, trisb_reg, trace):
        ByteRegister.__init__(self, PORTB, trace)
        self.trisb_reg = trisb_reg
        self.pins_modified = []
        for _ in xrange(8):
            self.pins_modified.append(threading.Event())
    def put(self, value):
        for _ in xrange(8):
            self.pins_modified[i].set()
        ByteRegister.put(self, value)
    def __setitem__(self, i, bit):
        self.pins_modified[i].set()
        ByteRegister.__setitem__(self, i, bit)

class IOPorts:
    """ System of IO ports of MC """
    INET_PORT_NUM = 8080
    def __init__(self, port_tris_regs, trace):
        server_thread = threading.Thread(
                target=_run_server, 
                args=(self.INET_PORT_NUM, port_tris_regs, trace))
        server_thread.daemon = True
        server_thread.start()
