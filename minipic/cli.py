#!/usr/bin/python

from cmd import Cmd
import re
from picmicro import PICmicro
import op
import piclog
import sys, getopt


def parse_constant(line):
    return int(line)

def parse_fda(line):
    return (0, 0, 0)

class CLI(Cmd):
    """Command processor for pic microcontroller"""

    prompt = 'minipic> '

    pic = PICmicro()
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
            for line in f:
                data_len = int(line[1:3], 16)
                start_addr = int(line[3:7], 16)
                type_rec = int(line[7:9], 16)
                data = line[9:(9 + 2*data_len)]
                if type_rec == 0:
                    print data
                    # copy chunk of bytes into program memory of MC
                    for i in xrange(0, data_len, 2):
                        opcode = int(data[(2*i + 2):(2*i + 4)] + data[2*i:(2*i + 2)], 16)
                        print hex(opcode),
                    print
                    pass
                elif type_rec == 1:
                    return
                elif type_rec == 4:
                    # specify higher-order bytes of address
                    pass

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
