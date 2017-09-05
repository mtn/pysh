from tatsu import model, parse, contexts
import subprocess
import readline
import tempfile
import os

readline.read_init_file('readline.rc')
PROMPT = '> '



def main():
    while True:
        cmdline = input(PROMPT)
        if cmdline == 'exit':
            break

        if cmdline != '':
            tree = parse_line(cmdline)
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
    if hasattr(cmd,'args'):
        if type(cmd.args) is contexts.closure:
            cmd = list(map(lambda x: x.unquoted_arg or x.quoted_arg[1:-1],cmd.args))
        else:
            cmd = cmd.args.unquoted_arg or cmd.args.quoted_arg[1:-1]
        subprocess.run(cmd,stdin=stdin,stdout=stdout)
    else:
        if hasattr(cmd,'dest_dir'):
            dest = cmd.dest_dir.unquoted_arg or cmd.dest_dir.quoted_arg[1:-1]
            if dest == '~':
                dest = os.getenv('HOME')
        else:
            dest = os.getenv('HOME')
        os.chdir(dest)

def execute_pipeline(pipeline,t,stdin=0):
    execute_command(pipeline.command,stdin=stdin,stdout=t)
    f = open(t.name, 'r')
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
        | cd: (/cd/ | /'cd'/) [dest_dir:arg]
        | args: { arg }
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
