from tatsu import model, parse, contexts
import subprocess
import readline
import tempfile
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
                if pid.stdin:
                    pid.stdin.close()
                if pid.stdout:
                    pid.stdout.close()
                pid.wait()

def parse_line(cmdline):
    semantics = model.ModelBuilderSemantics()
    return parse(GRAMMAR,cmdline,semantics=semantics)

def execute(tree,stdin=0,stdout=1):
    if tree['pipeline']:
        return execute_pipeline(tree['pipeline'])
    else:
        return execute_command(tree['command'],stdin=stdin,stdout=stdout)

def execute_command(cmd,stdin=0,stdout=1):
    if type(cmd.args) is contexts.closure:
        cmd = list(map(lambda x: x.unquoted_arg or x.quoted_arg[1:-1],cmd.args))
    else:
        cmd = cmd.args.unquoted_arg or cmd.args.quoted_arg[1:-1]

    return [subprocess.Popen(cmd,stdin=stdin,stdout=stdout)]

def execute_pipeline(pipeline):
    p = pipes.Template()
    t = tempfile.NamedTemporaryFile(mode='r')
    f = p.open(t.name, 'w')
    return execute_command(pipeline.command,stdout=f) + \
            execute(pipeline.cmdline,stdin=t)


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
