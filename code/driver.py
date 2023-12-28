from tokenizer import Tokenizer
from parser import Parser
import compiler
import interpreter
import sys, getopt

VERSION = "0.0.0"

def usage():
    print("usage: jutsu [option] ... [file | -] [arg] ...")
    print("-c     : use compiler instead of the default interpreter (also --compile)")
    print("-h     : print this help message and exit (also --help)")
    print("-v     : verbose (also --verbose)")
    print("-V     : print the Jutsu version number and exit (also --version)")
    print("file   : program read from script file")
    print("-      : program read from stdin (default)")
    print("arg ...: arguments passed to program in sys.argv[1:]")

def execute(executor, text):
    tokens = Tokenizer(text).tokenize()
    print("TOKENS")
    print(tokens)
    ast = Parser(tokens).ast
    print("AST")
    print(ast)
    executor(ast, env)

env = {}

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
    elif o in ("-V, --version"):
        print("Jutsu", VERSION)
        sys.exit()
    else:
        assert False, "unhandled option"

if len(args) >= 1:
    # TODO remove
    print(args[0])
    file = open(args[0], mode='r')
    targs = args[1:]  # TODO add functionality to actually use tail args
    text = file.read()
    file.close()
    execute(executor, text)  
else:
    print("Jutsu", VERSION)
    print("Type \"help\" for more information.")
    while True:
        try:
            text = input(">>> ")
        except EOFError:
            break

        if text == 'help':
            usage()
        if text == 'quit':
            sys.exit()
        else:
            execute(executor, text)