from tatsu import parse, contexts
import subprocess
import readline
import tempfile
import os


GRAMMAR = open('grammar.peg','r').read()
readline.read_init_file('readline.rc')
PROMPT = '$ '


def main():
    while True:
        cmdline = input(PROMPT)
        if cmdline == 'exit':
            break

        if cmdline != '':
            tree = parse(GRAMMAR,cmdline)
            for cmd in tree:
                execute(cmd[0])


def execute(tree,stdin=0):
    if tree['pipeline']:
        if tree['pipeline']['left']['redirection']:
            outfiles = get_outfiles(tree['pipeline']['left']['redirection']['outfile'])
            execute_redirection(tree['pipeline']['left']['redirection']['command'],outfiles)

            t = tempfile.NamedTemporaryFile(mode='w')
            execute_command(tree['pipeline']['right']['command'],stdin=t)
            t.close()
        else:
            t = tempfile.NamedTemporaryFile(mode='w')
            execute_pipeline(tree['pipeline'],stdin,stdout=t)
    elif tree['command']:
        execute_command(tree['command'],stdin)
    elif tree['redirection']:
        outfiles = get_outfiles(tree['redirection']['outfile'])
        execute_redirection(tree['redirection']['command'],outfiles)


def execute_command(cmd,stdin=0,stdout=1):
    if cmd['args']:
        if type(cmd.args) is contexts.closure:
            cmd = list(map(lambda x: x.unquoted_arg or x.quoted_arg[1:-1],cmd.args))
        else:
            cmd = cmd.args.unquoted_arg or cmd.args.quoted_arg[1:-1]
        try:
            return subprocess.run(cmd,stdin=stdin,stdout=stdout)
        except:
            print('Command failed')
    else:
        if cmd['dest_dir']:
            dest = cmd['dest_dir']['unquoted_arg'] or cmd['dest_dir']['quoted_arg'][1:-1]
            if dest == '~':
                dest = os.getenv('HOME')
        else:
            dest = os.getenv('HOME')
        os.chdir(dest)

def execute_redirection(cmd,outfiles):
    for f in outfiles:
        f = open(f,'w')
        f.close()
    cmd = execute_command(cmd,stdout=subprocess.PIPE)
    if cmd and cmd.stdout:
        for f in outfiles:
            f = open(f,'w')
            f.write(cmd.stdout.decode('utf-8'))

def execute_pipeline(pipeline,stdin=0,stdout=1):
    execute_command(pipeline['left']['command'],stdin,stdout)
    f = open(stdout.name, 'r')
    stdout.close()
    execute(pipeline['right'],stdin=f)

def get_outfiles(outfiles):
    if type(outfiles) is list:
        return list(map(lambda x: x['unquoted_arg'] or x['quoted_arg'][1:-1],outfiles))
    else:
        return [outfiles['unquoted_arg'] or outfiles['quoted_arg'][1:-1]]


if __name__ =='__main__':
    main()

