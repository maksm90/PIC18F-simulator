import sys
import re
from picmicro import PICmicro

# init microcontroller
pic = PICmicro()

# run REPL interpreter
delims = re.compile("\s*,?\s*")
while True:
    instr = delims.split(raw_input("> "))
    print instr

    cmd, operands = instr[0], instr[1:]
    if instr == "quit" or instr == "exit":
        sys.exit(0)
