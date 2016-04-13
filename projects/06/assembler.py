import sys

symbol_table = {
    'R0': 0,
    'R1': 1,
    'R2': 2,
    'R3': 3,
    'R4': 4,
    'R5': 5,
    'R6': 6,
    'R7': 7,
    'R8': 8,
    'R9': 9,
    'R10': 10,
    'R11': 11,
    'R12': 12,
    'R13': 13,
    'R14': 14,
    'R15': 15,
    'SP': 0,
    'LCL': 1,
    'ARG': 2,
    'THIS': 3,
    'THAT': 4,
    'SCREEN': 16384,
    'KBD': 24576
}

class NoSuchSymbolError(Exception):
    def __init__(self, symbol):
        super(Exception, self).__init__('No such symbol: "%s"' % symbol)
        self.symbol = symbol

def is_int(x):
    try:
        int(x)
        return True
    except:
        return False

def binstr15(i):
    s = bin(i)[2:]  # remove 0b prefix
    return '0' * (15 - len(s)) + s

def a_instruction(l):
    symbol = l[1:]

    if is_int(symbol):
        return '0' + binstr15(int(symbol))

    if symbol in symbol_table:
        return '0' + binstr15(symbol_table[symbol])

    raise NoSuchSymbolError(symbol)

def c_instruction(l):

    dest_map = {
        'null': '000',
        'M':    '001',
        'D':    '010',
        'MD':   '011',
        'A':    '100',
        'AM':   '101',
        'AD':   '110',
        'AMD':  '111'
    }
    jump_map = {
        'null': '000',
        'JGT':  '001',
        'JEQ':  '010',
        'JGE':  '011',
        'JLT':  '100',
        'JNE':  '101',
        'JLE':  '110',
        'JMP':  '111'
    }
    comp_map = {
        '0':    '0101010',
        '1':    '0111111',
        '-1':   '0111010',
        'D':    '0001100',
        'A':    '0110000',
        'M':    '1110000',
        '!D':   '0001101',
        '!A':   '0110001',
        '!M':   '1110001',
        '-D':   '0001111',
        '-A':   '0110011',
        '-M':   '1110011',
        'D+1':  '0011111',
        'A+1':  '0110111',
        'M+1':  '1110111',
        'D-1':  '0001110',
        'A-1':  '0110010',
        'M-1':  '1110010',
        'D+A':  '0000010',
        'D+M':  '1000010',
        'D-A':  '0010011',
        'D-M':  '1010011',
        'A-D':  '0000111',
        'M-D':  '1000111',
        'D&A':  '0000000',
        'D&M':  '1000000',
        'D|A':  '0010101',
        'D|M':  '1010101'
    }

    parts = l.split(';')

    dc_part = parts[0].strip()

    assert dc_part

    if dc_part.find('=') != -1:
        dest_str, comp_str = dc_part.split('=')
        dest_str = dest_str.strip()
        comp_str = comp_str.strip()
    else:
        dest_str = 'null'
        comp_str = dc_part

    if len(parts) > 1:
        jump_str = parts[1].strip()
    else:
        jump_str = 'null'

    dest = dest_map[dest_str]
    comp = comp_map[comp_str]
    jump = jump_map[jump_str]

    return '111%(comp)s%(dest)s%(jump)s' % locals()

def define_symbol(l, address):
    assert l.endswith(')')

    symbol = l[1:-1]

    if symbol in symbol_table:
        if address != symbol_table[symbol]:
            raise 'Internal inconsistency'

    symbol_table[symbol] = address
    return

def do_line(l, address):
    l = l.strip()

    if not l:
        return

    # Comments
    if l.startswith('//'):
        return

    # no whitespace allowed in assembly right now (is that right??)
    l = l.split()[0]

    if l.startswith('('):
        return define_symbol(l, address)

    if l[0] == '@':
        return a_instruction(l)
    return c_instruction(l)

def make_symbol_table(f):
    address = 0
    for line in f:
        try:
            instr = do_line(line, address)
        except NoSuchSymbolError:
            instr = 'placeholder'

        if instr:
            address += 1

def assemble(f):
    address = 0
    variable_addr = 16
    for line in f:
        try:
            instr = do_line(line, address)
        except NoSuchSymbolError, e:
            symbol_table[e.symbol] = variable_addr
            variable_addr += 1
            instr = do_line(line, address)

        if instr is None:
            continue

        print instr
        address += 1

def main():
    if sys.argv[1] == '-':
        f = sys.stdin
    else:
        f = open(sys.argv[1], 'r')

    make_symbol_table(f)

    f.seek(0)

    assemble(f)


if __name__ == '__main__':
    main()
