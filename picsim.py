import sys
import re

delims = re.compile("\s*,?\s*")
while True:
    instr = delims.split(raw_input("> "))
    print instr

    instr = instr[0]
    if instr == "quit" or instr == "exit":
        sys.exit(0)
