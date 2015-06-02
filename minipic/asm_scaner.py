import ply.lex as lex

tokens = ('ID', 'KW', 'CMD', 'NUM', 'NL')
literals = ',:'

t_ignore = ' \r\t\f'
t_ignore_COMMENT = r';.*'

keywords = ['equ', 'end', 'org']

def t_ID(t):
    r'(?i)[a-z_]\w*'
    return t

def t_NUM(t):
    r'(?i)([\da-f]+h)|(\d+)|0x\d+'
    if t.value[:2].lower() == '0x':
        t.value = int(t.value[2:], 16)
    if t.value[-1].lower() == 'h':
        t.value = int(t.value[:-1], 16)
    else:
        t.value = int(t.value)
    return t

def t_NL(t):
    r'\n+'
    t.lexer.lineno += len(t.value)
    return t

def t_error(t):
    t.lexer.skip(1)
    return t


lexer = lex.lex()
lexer.input(file('../asm/test1/test.asm').read())
count = 0
for tok in lexer:
    #if count > 17:
        #break
    print tok
    count += 1
