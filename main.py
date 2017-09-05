from tatsu import model, parse, contexts
import subprocess
import readline
import tempfile

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
            execute(tree)


def parse_line(cmdline):
    semantics = model.ModelBuilderSemantics()
    return parse(GRAMMAR,cmdline,semantics=semantics)

def execute(tree,stdin=0):
    if tree['pipeline']:
        t = tempfile.NamedTemporaryFile(mode='w')
        execute_pipeline(tree['pipeline'],t,stdin)
    else:
        execute_command(tree['command'],stdin)

def execute_command(cmd,stdin=0,stdout=1):
    if type(cmd.args) is contexts.closure:
        cmd = list(map(lambda x: x.unquoted_arg or x.quoted_arg[1:-1],cmd.args))
    else:
        cmd = cmd.args.unquoted_arg or cmd.args.quoted_arg[1:-1]

    a = subprocess.run(cmd,stdin=stdin,stdout=stdout)

def execute_pipeline(pipeline,t,stdin=0):
    f = open(t.name, 'r')
    execute_command(pipeline.command,stdin=stdin,stdout=t)
    t.close()
    execute(pipeline.cmdline,stdin=f)


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
