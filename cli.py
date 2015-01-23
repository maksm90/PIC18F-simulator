from cmd import Cmd
import re
from picmicro import PICmicro
import op

class CLI(Cmd):
    """Command processor for pic microcontroller"""

    prompt = 'minipic> '

    pic = PICmicro()
    env = {}

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

    def setValue(self, identifier, value):
        print identifier, value

    def getValue(self, identifier):
        print identifier

    def default(self, line):
        term_pattern = '[\w\[\]]+'
        set_val_pattern = '^\s*(' + term_pattern + ')\s*=\s*(' + term_pattern + ')\s*$'
        get_val_pattern = '^\s*(' + term_pattern + ')\s*$'

        set_re = re.compile(set_val_pattern, re.IGNORECASE)
        get_re = re.compile(get_val_pattern, re.IGNORECASE)

        m = set_re.match(line)
        if m != None:
            return self.setValue(m.group(1), m.group(2))

        m = get_re.match(line)
        if m != None:
            return self.getValue(m.group(1))

        return Cmd.default(line)

    def preloop(self):
        print '*** Starting CLI:'

    def postloop(self):
        print '*** Done'


if __name__ == '__main__':
    CLI().cmdloop()
