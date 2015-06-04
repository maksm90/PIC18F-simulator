import socket

class IOPorts:
    """ System of IO ports of MC """
    INET_PORT_NUM = 8080
    def __init__(self, trace): #port_regs, tris_regs, trace):
        #self.porta, self.portb = port_regs
        #self.trisa, self.trisb = tris_regs
        self.trace = trace
