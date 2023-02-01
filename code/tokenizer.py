from enum import Enum
class Type(Enum):
    LPAREN, LSQB, LCB, RPAREN, RSQB, RCB, COLON, NOT, PLUS, MINUS, MULT, DIV, PERCENT, LT, GT, EQ, COMMA, DOT, IDIV, DSTAR, DEQ, NEQ, LEQ, GEQ, OR, AND, PLUSEQ, MINUSEQ, MULTEQ, DIVEQ, IDIVEQ, DSTAREQ, DEFINE, TRUE, FALSE, IF, ELIF, ELSE, RETURN, PRINT, INT, STRING, NAME, NEWLINE, EOF = range(45)
class Token:
    def __init__(self, type, value):
        self.type = type
        self.value = value

    def __repr__(self):
        if self.value:
            return "{" + self.type.name + ", " + self.value + "}"
        return "{" + self.type.name + "}"
class Tokenizer:
    leftlevels = {
        '(': Type.LPAREN,
        '[': Type.LSQB,
        '{': Type.LCB,
    }

    rightlevels = {
        ')': Type.RPAREN,
        ']': Type.RSQB,
        '}': Type.RCB,
    }

    symbols = {
        ':': Type.COLON,
        '!': Type.NOT,
        '+': Type.PLUS,
        '-': Type.MINUS,
        '*': Type.MULT,
        '/': Type.DIV,
        '%': Type.PERCENT,
        '<': Type.LT,
        '>': Type.GT,
        '=': Type.EQ,
        ',': Type.COMMA,
        '.': Type.DOT
    }

    multicharSymbols = {
        '//': Type.IDIV,
        '**': Type.DSTAR,
        '==': Type.DEQ,
        '!=': Type.NEQ,
        '<=': Type.LEQ,
        '>=': Type.GEQ,
        'or': Type.OR,
        'and': Type.AND,
        '+=': Type.PLUSEQ,
        '-=': Type.MINUSEQ,
        '*=': Type.MULTEQ,
        '/=': Type.DIVEQ,
        '//=': Type.IDIVEQ,
        '**=': Type.DSTAREQ,
        'jutsu': Type.DEFINE,
        'True': Type.TRUE,
        'False': Type.FALSE,
        'if': Type.IF,
        'elif': Type.ELIF,
        'else': Type.ELSE,
        'release': Type.RETURN,
        'print': Type.PRINT
    }

    def __init__(self):
        self.level = 0

    def isalpha(self, char):
        return (ord(char) >= 65 and ord(char) <= 90) or (ord(char) >= 97 and ord(char) <= 122)

    def isnumeric(self, char):
        return ord(char) >= 48 and ord(char) <= 57

    def tokenizeWhitespace(self, input, current):
        if input[current] == ' ':
            return 1, None
        elif input[current] == '\n':
            if self.level == 0:
                return 1, Token(Type.NEWLINE, input[current])
            return 1, None
        elif input[current] == '#':
            consumed = 1
            while input[current+consumed] != '\n':
                consumed += 1
            return consumed+1, None
        return 0, None
        
    def tokenizeMultiCharSymbol(self, input, current):
        for symbol, token in self.multicharSymbols.items():
            curr = input[current]
            consumed = 0
            while consumed < len(symbol) and symbol[consumed] == curr:
                consumed += 1
                if current + consumed < len(input):
                    curr = input[current + consumed]
                else:
                    return 0, None
            if consumed == len(symbol) and input[current:current+consumed] == symbol:
                return consumed, Token(token, None)
        return 0, None

    def tokenizeSymbol(self, input, current):
        if input[current] in self.symbols:
            return 1, Token(self.symbols[input[current]], None)
        elif input[current] in self.leftlevels:
            self.level += 1
            return 1, Token(self.leftlevels[input[current]], None)
        elif input[current] in self.rightlevels:
            self.level -= 1
            return 1, Token(self.rightlevels[input[current]], None)
        return 0, None
    
    def tokenizeInteger(self, input, current):
        curr = input[current]
        consumed = 0
        while self.isnumeric(curr):
            consumed += 1
            if current + consumed < len(input):
                curr = input[current+consumed]
            else:
                break
        if consumed != 0:
            return consumed, Token(Type.INT, input[current:current+consumed])
        return 0, None

    def tokenizeString(self, input, current):
        if input[current] == '"':
            consumed = 1
            curr = input[current + consumed]
            while curr != '"':
                consumed += 1
                if current + consumed < len(input):
                    curr = input[current+consumed]
                else:
                    break
            if curr == '"':
                return consumed + 1, Token(Type.STRING, input[current+1:current+consumed])
            else:
                return 0, None
        return 0, None
    
    def tokenizeName(self, input, current):
        curr = input[current]
        consumed = 0
        while self.isalpha(curr):
            consumed += 1
            if current + consumed < len(input):
                curr = input[current+consumed]
            else:
                break
        if consumed != 0:
            return consumed, Token(Type.NAME, input[current:current+consumed])
        return 0, None

    def tokenize(self, input):

        tokenizers = [
            self.tokenizeWhitespace,
            self.tokenizeMultiCharSymbol, 
            self.tokenizeSymbol,
            self.tokenizeInteger,
            self.tokenizeString,
            self.tokenizeName
        ]

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
                raise Exception("Unreadable or invalid character %c during tokenization" % (input[current]))
        tokens.append(Token(Type.EOF, None))
        return tokens 