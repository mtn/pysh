from tatsu import model, parse, contexts
import subprocess
import readline
import pipes

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
            pids = execute(tree)
            for pid in pids:
                print(pid)
                pid.wait()

def parse_line(cmdline):
    semantics = model.ModelBuilderSemantics()
    return parse(GRAMMAR, cmdline, semantics=semantics)

def execute(tree):
    if tree['pipeline']:
        return execute_pipeline(tree['pipeline'])
    else:
        return execute_command(tree['command'])

def execute_command(cmd):
    if type(cmd.args) is contexts.closure:
        cmd = list(map(lambda x: x.unquoted_arg or x.quoted_arg[1:-1],cmd.args))
    else:
        cmd = cmd.args.unquoted_arg or cmd.args.quoted_arg[1:-1]

    return [subprocess.Popen(cmd)]

def execute_pipeline(pipeline):
    return execute_command(pipeline.command) + execute(pipeline.cmdline)


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

    pipeline
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
