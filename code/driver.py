import tokenizer
import parser
import compiler
import interpreter
import sys, getopt

env = {}

def usage():
    print("usage: python [option] ... [file | -] [arg] ...")
    print("-c     : use compiler instead of the default interpreter (also --compile)")
    print("-h     : print this help message and exit (also --help)")
    print("-v     : verbose (also --verbose)")
    print("file   : program read from script file")
    print("-      : program read from stdin (default)")
    print("arg ...: arguments passed to program in sys.argv[1:]")

def execute(executor, text):
    ast = parser.parse(tokenizer.tokenize(text))
    executor(ast, env)

try:
    opts, args = getopt.getopt(sys.argv[1:],"hvc",["help", "verbose", "compile"])
except getopt.GetoptError as err:
    print(err)
    usage()
    sys.exit(2)

output = None
verbose = False
executor = interpreter.process
for o, a in opts:
    if o in ("-v", "--verbose"):
        verbose = True
    elif o in ("-h", "--help"):
        usage()
        sys.exit()
    elif o in ("-c", "--compile"):
        executor = compiler.process
    else:
        assert False, "unhandled option"

if len(sys.argv) > 1:
    #read text from file
    text = ""
    execute(executor, text)   
else:
    while True:
        try:
            print("Jutsu 0.0.0")
            text = input(">>> ")
        except EOFError:
            break

        if text:
            execute(executor, text)