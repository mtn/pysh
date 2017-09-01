import readline

readline.read_init_file('readline.rc')
PROMPT = '> '

def main():
    while True:
        line = input(PROMPT)
        if line == 'exit':
            break
        print(line)



if __name__ =='__main__':
    main()
