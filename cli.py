from cmd import Cmd
import re
from picmicro import PICmicro
import op
import piclog


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


if __name__ == '__main__':
    CLI().cmdloop()
