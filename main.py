from tatsu import model, parse, contexts
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
            print(tree)
            if type(tree['command']) is list:
                for cmd in tree['command']:
                    pids = execute_command(cmd)
            else:
                pids = execute_command(tree['command'])

            for pid in pids:
                pid.wait()

def parse_line(cmdline):
    semantics = model.ModelBuilderSemantics()
    return parse(GRAMMAR, cmdline, semantics=semantics)

def execute_command(cmd):
    if type(cmd.args) is contexts.closure:
        cmd = list(map(lambda x: x.unquoted_arg or x.quoted_arg[1:-1],cmd.args))
    else:
        cmd = cmd.args.unquoted_arg or cmd.args.quoted_arg[1:-1]

    return [subprocess.Popen(cmd)]


GRAMMAR = '''
    @@grammar::CMD_PARSE


    start = cmdline $ ;


    cmdline
        =
        | pipeline: pipeline
        | command: command
        ;

    command::Command
        =
        args: { arg }
        ;

    pipeline::Pipeline
        =
        command:command '|' cmdline:cmdline
        ;

    arg
        =
        | quoted_arg: /'[^'|]*'/
        | unquoted_arg: /[^\s|]+/
        ;

'''


if __name__ =='__main__':
    main()
