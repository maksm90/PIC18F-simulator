#!/usr/bin/python

from cmd import Cmd
import re
from picmicro import PICmicro
from op import *
import piclog
import sys, getopt
from interpreter import Interpreter

# masks to pick out code of commands of operations
def CMD_COP4(cmd):
    return (cmd & 0xF000)
def CMD_COP5(cmd):
    return (cmd & 0xF800)
def CMD_COP6(cmd):
    return (cmd & 0xFC00)
def CMD_COP7(cmd):
    return (cmd & 0xFE00)
def CMD_COP8(cmd):
    return (cmd & 0xFF00)
def CMD_COP10(cmd):
    return (cmd & 0xFFC0)
def CMD_COP12(cmd):
    return (cmd & 0xFFF0)
def CMD_COP15(cmd):
    return (cmd & 0xFFFE)

# codes of commands of operations
COP_ADDLW = 0x0F00
COP_ADDWF = 0x2400
COP_ADDWFC =0x2000
COP_ANDLW = 0x0B00
COP_ANDWF = 0x1400
COP_BC = 0xE200
COP_BCF = 0x9000
COP_BN = 0xE600
COP_BNC = 0xE300
COP_BNN = 0xE700
COP_BNOV = 0xE500
COP_BNZ = 0xE100
COP_BOV = 0xE400
COP_BRA = 0xD000
COP_BSF = 0x8000
COP_BTFSC = 0xB000
COP_BTFSS = 0xA000
COP_BTG = 0x7000
COP_BZ = 0xE000
COP_CALL = 0xEC00
COP_CLRF = 0x6A00
COP_CLRWDT = 0x0004
COP_COMF = 0x1C00
COP_CPFSEQ = 0x6200
COP_CPFSGT = 0x6400
COP_CPFSLT = 0x6000
COP_DAW = 0x0007
COP_DECF = 0x0400
COP_DECFSZ = 0x2C00
COP_DCFSNZ = 0x4C00
COP_GOTO = 0xEF00
COP_INCF = 0x2800
COP_INCFSZ = 0x3C00
COP_INFSNZ = 0x4800
COP_IORLW = 0x0900
COP_IORWF = 0x1000
COP_LFSR = 0xEE00
COP_MOVF = 0x5000
COP_MOVFF = 0xC000
COP_MOVLB = 0x0100
COP_MOVLW = 0x0E00
COP_MOVWF = 0x6E00
COP_MULLW = 0x0D00
COP_MULWF = 0x0200
COP_NEGF = 0x6C00
COP_NOP = 0x0000
COP_NOP2 = 0xF000   # NOP in second word
COP_POP = 0x0006
COP_PUSH = 0x0005
COP_RCALL = 0xD800
COP_RESET = 0x00FF
COP_RETFIE = 0x0010
COP_RETLW = 0x0C00
COP_RETURN = 0x0012
COP_RLCF = 0x3400
COP_RLNCF = 0x4400
COP_RRCF = 0x3000
COP_RRNCF = 0x4000
COP_SETF = 0x6800
COP_SLEEP = 0x0003
COP_SUBFWB = 0x5400
COP_SUBLW = 0x0800
COP_SUBWF = 0x5C00
COP_SUBWFB = 0x5800
COP_SWAPF = 0x3800
COP_TBLRD = 0x0008
COP_TBLWT = 0x000C
COP_TSTFSZ = 0x6600
COP_XORLW = 0x0A00
COP_XORWF = 0x1800

def parse_constant(line):
    return int(line)

def parse_fda(line):
    return (0, 0, 0)

def decode_op(opcode):
    # 16-bit operations
    op = opcode
    if op == COP_CLRWDT:
        return NOP()
    elif op == COP_DAW:
        return NOP()
    elif op == COP_NOP:
        return NOP()
    # 15-bit operations
    op = CMD_COP15(opcode)
    if op == COP_RETFIE:
        return NOP()
    # 12-bit operations
    op = CMD_COP12(opcode)
    if op == COP_MOVLB:
        return NOP()
    # 10-bit operation
    op = CMD_COP10(opcode)
    if op == COP_LFSR:
        return NOP()
    # 8-bit operations
    op = CMD_COP8(opcode)
    if op == COP_ADDLW:
        return NOP()
    elif op == COP_MOVLW:
        return MOVLW(opcode & 0xff)
    # 7-bit operations
    op = CMD_COP7(opcode)
    if op == COP_MOVWF:
        return MOVWF(opcode & 0xff, (opcode & 0x100) >> 8)
    return NOP()


class CLI(Cmd):
    """Command processor for pic microcontroller"""

    prompt = 'minipic> '

    interpreter = Interpreter()
    pic = interpreter.cpu
    env = {}

    def _print_pic_state(self):
        piclog.logger.disabled = True
        print "  WREG=0x%X BSR=0x%X PC=%d"  % (self.pic.wreg, self.pic.bsr, self.pic.pc)
        N, OV, Z, DC, C = (self.pic.status & op.N) >> 4, \
                          (self.pic.status & op.OV) >> 3, \
                          (self.pic.status & op.Z) >> 2, \
                          (self.pic.status & op.DC) >> 1, \
                          (self.pic.status & op.C)
        print "  STATUS: N=%d OV=%d Z=%d DC=%d C=%d" % (N, OV, Z, DC, C)
        piclog.logger.disabled = False

    def do_load(self , hexfile):
        """
        load hex-file
        Load program code from file in hex format
        """
        with open(hexfile, 'r') as f:
            higher_addr = 0
            for line in f:
                data_len = int(line[1:3], 16)
                start_addr = int(line[3:7], 16)
                type_rec = int(line[7:9], 16)
                data = line[9:(9 + 2*data_len)]
                if type_rec == 0:
                    # copy chunk of bytes into program memory of MC
                    for i in xrange(0, data_len, 2):
                        s_opcode = data[(2*i + 2):(2*i + 4)] + data[2*i:(2*i + 2)]
                        opcode = int(s_opcode, 16)
                        addr = ((higher_addr << 16) | start_addr) + i
                        self.pic.program[addr] = decode_op(opcode)
                elif type_rec == 1:
                    return
                elif type_rec == 4:
                    # specify higher-order bytes of address
                    higher_addr = int(data, 16)

    def do_step(self, line):
        if line == '':
            num_steps = 1
        else:
            num_steps = int(line)
        for _ in xrange(num_steps):
            self.interpreter.step()

    def do_addwf(self, line):
        """
        addwf f[,d[,a]]
        Add content of 'f' to WREG
        """
        f, d, a = parse_fda(line)

    def do_addlw(self, line):
        """
        addlw <byte>
        Add constant byte value to WREG 
        """
        op.addlw(self.pic, parse_constant(line))
        self._print_pic_state()

    def do_exit(self, line):
        """
        Exit from CLI
        """
        return True

    def preloop(self):
        print '*** Starting CLI:'

    def postloop(self):
        print '*** Done'

def parse_hexrec(hex_line):
    return (start_addr, type_rec, data)

def load_code_from_hex(pic, hex_recs):
    def convert_word(str_word):
        return int(str_word[2:4] + str_word[:2], 16)

    base_addr = 0
    for hex_rec in hex_recs:
        start_addr, type_rec, data = hex_rec
        if type_rec == 1:
            return
        if type_rec == 4:
            base_addr = convert_word(data)
        elif type_rec == 0:
            pic.program.load(base_addr+start_addr, data)


if __name__ == '__main__':
    cli = CLI()

    # parse command line options
    opts, args = getopt.getopt(sys.argv[1:], 'x:', ['hex='])
    for opt, arg in opts:
        if opt in ('-h', '--help'):
            print './cli.py [-x <hexfile>]'
            sys.exit(0)
        if opt in ('-x', '--hex'):
            hex_recs = list()
            with open(arg) as hexfile:
                for line in hexfile:
                    hex_recs.append(parse_hexrec(line))
            load_code_from_hex(cli.pic, hex_recs)
        else:
            pass

    # run CLI
    cli.cmdloop()
