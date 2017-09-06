from tatsu import model, parse, contexts
import subprocess
import readline
import tempfile
import os

import json
import pprint

GRAMMAR = open('grammar.peg','r').read()
readline.read_init_file('readline.rc')
PROMPT = '$ '


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
    print(json.dumps(tree, indent=4))
    # if tree['pipeline']:
    #     if tree['pipeline']['redirection']:
    #         outfiles = tree['pipeline']['redirection']['outfile']
    #         if type(outfiles) is list:
    #             outfiles = list(map(lambda x: x.unquoted_arg or x.quoted_arg[1:-1],outfiles))
    #         else:
    #             outfiles = [outfiles.unquoted_arg or outfiles.quoted_arg[1:-1]]

    #         execute_redirection(tree['pipeline']['redirection'],outfiles)
    #         if tree['pipeline']['pipeline']:
    #             t = tempfile.NamedTemporaryFile(mode='w')
    #             t.write('\0')
    #             execute_command(tree['pipeline']['pipeline']['command'],stdin=t)
    #             t.close()

    #     elif tree['pipeline']['pipeline']:
    #         t = tempfile.NamedTemporaryFile(mode='w')
    #         execute_pipeline(tree['pipeline'],stdin,stdout=t)
    #     else:
    #         execute_command(tree['pipeline']['command'],stdin)
    # if tree['cmdline']:
    #     execute(tree['cmdline'])


def execute_command(cmd,stdin=0,stdout=1):
    if hasattr(cmd,'args'):
        if type(cmd.args) is contexts.closure:
            cmd = list(map(lambda x: x.unquoted_arg or x.quoted_arg[1:-1],cmd.args))
        else:
            cmd = cmd.args.unquoted_arg or cmd.args.quoted_arg[1:-1]
        try:
            return subprocess.run(cmd,stdin=stdin,stdout=stdout)
        except:
            print('Command failed')
    else:
        if hasattr(cmd,'dest_dir'):
            dest = cmd.dest_dir.unquoted_arg or cmd.dest_dir.quoted_arg[1:-1]
            if dest == '~':
                dest = os.getenv('HOME')
        else:
            dest = os.getenv('HOME')
        os.chdir(dest)

def execute_redirection(cmd,outfiles):
    cmd = execute_command(cmd.command,stdout=subprocess.PIPE)
    if cmd.stdout:
        for f in outfiles:
            f = open(f,'w')
            f.write(cmd.stdout.decode('utf-8'))

def execute_pipeline(pipeline,stdin=0,stdout=1):
    execute_command(pipeline.command,stdin,stdout)
    f = open(stdout.name, 'r')
    stdout.close()
    execute(pipeline,stdin=f)



if __name__ =='__main__':
    main()

