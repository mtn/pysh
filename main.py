from tatsu.model import ModelBuilderSemantics
from tatsu import parse
import subprocess
import readline

readline.read_init_file('readline.rc')
PROMPT = '> '


def main():
    while True:
        cmdline = input(PROMPT)
        if cmdline == 'exit':
            break

        if cmdline != '':
            tree = parse_line(cmdline)
            pids = execute_command(tree['command'])

            for pid in pids:
                pid.wait()

def parse_line(cmdline):
    semantics = ModelBuilderSemantics()
    return parse(GRAMMAR, cmdline, semantics=semantics)

def execute_command(cmd):
    if type(cmd.arg) is list:
        cmd = list(map((lambda x: x.arg),cmd.arg))
    else:
        cmd = cmd.arg.arg

    return [subprocess.Popen(cmd)]


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
