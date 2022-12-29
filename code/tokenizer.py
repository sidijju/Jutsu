tokentypes = ["NAME", 
              "INT", 
              "STRING"]
class Token:
    def __init__(self, toktype, value):
        self.toktype = toktype
        self.value = value

def tokenizeWhitespace(input, current):
    if input[current] == ' ':
        return 1, None
    return 0, None

multicharSymbols = {'//': "IDIV",
                    '**': "DSTAR",
                    'or': "OR",
                    'and': "AND",
                    '==': "DEQ",
                    '!=': "NEQ",
                    '<=': "LEQ",
                    '>=': "GEQ",
                    '+=': "PLUSEQ",
                    '-=': "MINUSEQ",
                    '*=': "MULEQ",
                    '/=': "DIVEQ",
                    '//=': "IDIVEQ",
                    '**=': "DSTAREQ",
                    'release': "RETURN",
                    'no jutsu': "DEFINE"}

def tokenizeMultiCharSymbol(input, current):
    for symbol, tokentype in multicharSymbols:
        curr = input[current]
        consumed = 0
        while consumed < len(symbol) and symbol[consumed] == curr:
            consumed += 1
            curr = input[current + consumed]
        if consumed == len(symbol) and input[current:current+consumed] == symbol:
            return consumed, Token(tokentype, symbol)
    return 0, None


symbols = {'(': "LPAREN", 
            ')': "RPAREN", 
            '[': "LSQB", 
            ']': "RSQB", 
            '{': "LCB", 
            '}': "RCB",
            ':': "COLON",
            '+': "PLUS",
            '-': "MINUS",
            '*': "MULT",
            '/': "DIV",
            '%': "PERCENT",
            '<': "LT",
            '>': "GT",
            '=': "EQ",
            '#': "COMMENT",
            '/n': "NEWLINE",
            ',': "COMMA"}

def tokenizeSymbol(input, current):
    if input[current] in symbols:
        return 1, Token(symbols[input[current]], input[current])
    return 0, None
    
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