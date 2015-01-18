from cmd import Cmd
from picmicro import PICmicro
import op

class CLI(Cmd):
    """Command processor for pic microcontroller"""

    prompt = 'minipic> '

    pic = PICmicro()

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
