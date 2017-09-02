from tatsu.model import ModelBuilderSemantics
from tatsu import parse
import readline

readline.read_init_file('readline.rc')
PROMPT = '> '


def main():
    while True:
        cmdline = input(PROMPT)
        if cmdline == 'exit':
            break

        tree = parse_line(cmdline)
        print(tree)
        print(tree['command'])

def parse_line(cmdline):
    semantics = ModelBuilderSemantics()
    return parse(GRAMMAR, cmdline, semantics=semantics)


GRAMMAR = '''
    @@grammar::CMD_PARSE


    start = cmdline $ ;


    cmdline
        =
        { command:command }
        ;

    command::Command
        =
        { arg:arg }
        ;

    arg
        =
        arg:/[^\s]+/
        ;

'''


if __name__ =='__main__':
    main()
