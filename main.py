from tatsu import parse
import readline
import pprint

readline.read_init_file('readline.rc')
PROMPT = '> '

def main():
    while True:
        cmdline = input(PROMPT)
        if cmdline == 'exit':
            break

        tree = parse_line(cmdline)
        print(tree)

def parse_line(cmdline):
    return parse(GRAMMAR, cmdline)

GRAMMAR = '''
    @@grammar::CMD_PARSE


    start = cmdline $ ;


    cmdline
        =
        { command }
        ;

    command
        =
        { arg }
        ;

    arg
        =
        /[^\s]+/
        ;


'''


if __name__ =='__main__':
    main()
