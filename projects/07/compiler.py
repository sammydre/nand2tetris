import sys

class Command:
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
    with open(sys.argv[1], 'r') as f:
        for command in parser(f):
            print command

if __name__ == '__main__':
    main()
