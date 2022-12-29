tokentypes = ["NAME", 
              "INT", 
              "FLOAT", 
              "STRING", 
              "NEWLINE", 
              "INDENT", 
              "LPAREN", 
              "RPAREN", 
              "LSQB", 
              "RSQB", 
              "LCB", 
              "RCB",
              "COLON",
              "PLUS",
              "MINUS",
              "MULT",
              "IDIV",
              "DIV",
              "DSTAR",
              "MOD",
              "OR",
              "AND",
              "LT",
              "GT",
              "EQ",
              "DEQ",
              "NEQ",
              "LEQ",
              "GEQ",
              "PLUSEQ",
              "MINUSEQ",
              "MULEQ",
              "DIVEQ",
              "IDIVEQ",
              "DSTAREQ",
              "COMMENT"]

reserved_names = ['release',
                  'no jutsu']

class Token:
    def __init__():
        toktype = None
        value = None

def tokenizeWhitespace(input, current):
    if input[current] == ' ':
        return 1, None
    return 0, None

def tokenizeMultiCharSymbol(input, current):
    raise NotImplementedError

def tokenizeSymbol(input, current):
    raise NotImplementedError

def tokenizeInteger(input, current):
    raise NotImplementedError

def tokenizeString(input, current):
    raise NotImplementedError

def tokenizeName(input, current):
    raise NotImplementedError

def tokenize(input):

    tokenizers = [tokenizeMultiCharSymbol, 
                  tokenizeSymbol,
                  tokenizeInteger,
                  tokenizeName,
                  tokenizeString]

    current = 0
    tokens = []
    while current < len(input):
        tokenized = False
        for tokenizer in tokenizers:
            if tokenized:
                break
            consumed, token = tokenizer(input, current)
            if consumed != 0:
                current += consumed
                tokenized = True
            if token:
                tokens.append(token)
        if not tokenized:
            raise Exception("Unreadable or invalid character during tokenization")
    return tokens