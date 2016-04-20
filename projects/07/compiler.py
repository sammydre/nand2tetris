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
        elif f0 in ['add', 'sub', 'eq', 'lt', 'gt', 'neg', 'or', 'not', 'and']:
            return Command.C_ARITHMETIC

    def __str__(self):
        return ' '.join(self.fields) + ', t=' + str(self.command_type())

class CodeGen(object):
    def __init__(self, f):
        self.f = f
        self.label_num = 0

    def _make_label(self):
        self.label_num += 1
        return 'CompilerLabel%03d' % self.label_num

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

    def _emit_op_binary(self, sign):
        # pop the two numbers from the top of the stack and add them together
        # - we skip over the pops, rather read, then read+add, overwrite, and
        #   finally pop
        self._e('@SP')
        self._e('A=M-1')
        self._e('D=M')
        self._e('A=A-1')
        self._e('D=M%sD' % sign)
        self._e('M=D')
        self._emit_sp_dec()

    def _emit_add(self):
        self._emit_op_binary(sign='+')

    def _emit_sub(self):
        self._emit_op_binary(sign='-')

    def _emit_and(self):
        self._emit_op_binary(sign='&')

    def _emit_or(self):
        self._emit_op_binary(sign='|')

    def _emit_op_unary(self, op):
        self._e('@SP')
        self._e('A=M-1')
        self._e('D=%sM' % op)
        self._e('@SP')
        self._e('A=M-1')
        self._e('M=D')

    def _emit_neg(self):
        self._emit_op_unary(op='-')

    def _emit_not(self):
        self._emit_op_unary(op='!')

    def _emit_comparison(self, cmptor):
        # There seems to be some confusion about true/false values in their
        # documentation. The lectures notes say "0 and -1 representing true
        # and false respectively". But this is both insane, and incorrect.
        # Elsewhere (e.g. in the test scripts), the opposite is assumed. Maybe
        # the book describes it correctly, but the lecture notes don't? Not
        # sure.
        label = self._make_label()
        label_end = self._make_label()

        self._e('@SP // comparison: %s' % cmptor)
        self._e('A=M-1')
        self._e('D=M')
        self._e('A=A-1')
        self._e('A=M')
        # now D=arg2, A=arg1
        
        # FIXME: consider maximal sized values here (WORD_MAX and WORD_MIN)
        # and what it means for my arithmetic below
        if cmptor == 'eq':
            self._e('D=D-A')
            self._e('@%s' % label)
            self._e('D; JEQ')
        elif cmptor == 'lt':
            self._e('D=D-A')
            self._e('@%s' % label)
            self._e('D; JGT')
        elif cmptor == 'gt':
            self._e('D=D-A')
            self._e('@%s' % label)
            self._e('D; JLT')
        else:
            assert False
        
        # false part
        self._emit_sp_dec()
        self._emit_sp_dec()
        self._e('D=0') # 0 == false
        self._emit_write_d_to_stack()
        self._emit_sp_inc()

        # skip to end (don't run true part!)
        self._e('@%s' % label_end)
        self._e('0; JMP')

        # true part
        self._e('(%s)' % label)
        self._emit_sp_dec()
        self._emit_sp_dec()
        self._e('D=-1') # -1 == true
        self._emit_write_d_to_stack()
        self._emit_sp_inc()

        self._e('(%s) // end comparison (%s)' % (label_end, cmptor))

    def _emit_arithmetic(self, carg):
        if carg[0] == 'add':
            assert len(carg) == 1
            return self._emit_add()
        elif carg[0] == 'sub':
            assert len(carg) == 1
            return self._emit_sub()
        elif carg[0] == 'neg':
            assert len(carg) == 1
            return self._emit_neg()
        elif carg[0] == 'and':
            assert len(carg) == 1
            return self._emit_and()
        elif carg[0] == 'or':
            assert len(carg) == 1
            return self._emit_or()
        elif carg[0] == 'not':
            assert len(carg) == 1
            return self._emit_not()
        elif carg[0] in ['eq', 'lt', 'gt']:
            assert len(carg) == 1
            return self._emit_comparison(carg[0])
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
