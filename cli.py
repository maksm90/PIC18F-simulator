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

    def do_set(self, args):
        print args

    def do_get(self, args):
        print args

    def parseline(self, line):
        #identifier_pattern = '[a-z]\w*'
        #number_pattern = '\d+|0x[\da-f]+'
        #data_mem_pattern = 'data\[(' + number_pattern + ')\]'
        term_pattern = '[\w\[\]]+'
        set_cmd_pattern = '^\s*(' + term_pattern + ')\s*=\s*(' + term_pattern + ')\s*$'
        get_cmd_pattern = '^\s*(' + term_pattern + ')\s*$'

        set_re = re.compile(set_cmd_pattern, re.IGNORECASE)
        get_re = re.compile(get_cmd_pattern, re.IGNORECASE)

        m = set_re.match(line)
        if m != None:
            return ('set', (m.group(1), m.group(2)), line)

        m = get_re.match(line)
        if m != None:
            return ('get', m.group(1), line)

        Cmd.parseline(self, line)

    def preloop(self):
        print '*** Starting CLI:'

    def postloop(self):
        print '*** Done'


if __name__ == '__main__':
    CLI().cmdloop()
