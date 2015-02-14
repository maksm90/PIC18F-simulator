from cmd import Cmd
import re
from picmicro import PICmicro
import op

def parse_fda(line):
    pass

class CLI(Cmd):
    """Command processor for pic microcontroller"""

    prompt = 'minipic> '

    pic = PICmicro()
    env = {}

    def do_addwf(self, line):
        """
        addwf f[,d[,a]]
        Add content of 'f' to WREG
        """
        pass

    def do_addlw(self, line):
        """
        addlw <byte>
        Add constant byte value to WREG 
        """
        op.addlw(self.pic, int(line))

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
