import tokenizer
import parser
import compiler
import interpreter

env = {}

while True:
    try:
        print("Jutsu 0.0.0")
        text = input(">>> ")
    except EOFError:
        break

    if text:
        ast = parser.parse(tokenizer.tokenize(text))
        compiler.compile(ast, env)