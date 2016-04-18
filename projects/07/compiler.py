import sys

class Command(object):
    C_ARITHMETIC, C_PUSH, C_POP, C_LABEL, C_GOTO, C_IF, C_FUNCTION, \
        C_RETURN, C_CALL = range(0, 9)

    def __init__(self, fields):
        self.fields = fields        

    def command_type(self):
        f0 = self.fields[0]

        if f0 == 'push': return Command.C_PUSH
        elif f0 == 'pop': return Command.C_POP
        elif f0 in ['add', 'sub']: return Command.C_ARITHMETIC

    def __str__(self):
        return ' '.join(self.fields) + ', t=' + str(self.command_type())

class CodeGen(object):
    def __init__(self, f):
        self.f = f

    def _e(self, s):
        self.f.write(s + '\n')

    def _emit_sp_inc(self):
        self._e('@SP')
        self._e('M=M+1')

    def _emit_sp_dec(self):
        self._e('@SP')
        self._e('M=M-1')

    def _emit_write_d_to_stack(self):
        self._e('@SP')
        self._e('A=M')
        self._e('M=D')
    
    def _emit_push_constant(self, carg):
        assert len(carg) == 1
        self._e('@%s' % str(carg[0]))
        self._e('D=A')
        self._emit_write_d_to_stack()
        self._emit_sp_inc()

    def _emit_push(self, carg):
        if carg[0] == 'constant':
            return self._emit_push_constant(carg[1:])
        else:
            assert False

    def _emit_add(self):
        # pop the two numbers from the top of the stack and add them together
        self._e('@SP')
        self._e('A=M-1')
        self._e('D=M')
        self._e('A=A-1')
        self._e('D=M+D')
        self._e('M=D')
        self._emit_sp_dec()

    def _emit_sub(self):
        pass

    def _emit_arithmetic(self, carg):
        if carg[0] == 'add':
            assert len(carg) == 1
            return self._emit_add()
        elif carg[0] == 'sub':
            assert len(carg) == 1
            return self._emit_sub()
        else:
            assert False

    def gen(self, command):
        ty = command.command_type()

        if ty == Command.C_PUSH:
            self._emit_push(command.fields[1:])
        elif ty == Command.C_ARITHMETIC:
            self._emit_arithmetic(command.fields)
        else:
            assert False

def parser(f):
    for line in f:
        fields = line.split()
        # Do we need to do this after a split?
        fields = [x.strip() for x in fields]

        cnt = 0
        for i in fields:
            if i.startswith('//'):
                if cnt == 0: fields = []
                else: fields = fields[0:cnt - 1]
                break

        if not fields:
            continue

        yield Command(fields)


def main():
    cg = CodeGen(sys.stdout)

    with open(sys.argv[1], 'r') as f:
        for command in parser(f):
            cg.gen(command)

if __name__ == '__main__':
    main()
