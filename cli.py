import sys
import picmicro

pic = picmicro.PICmicro()

print '*** Starting CLI:'
while True:
    text_cmd = raw_input('minipic> ')
    if text_cmd == 'exit':
        print '*** Done'
        sys.exit(0)
    print '*** input command is "' + text_cmd + '"'
