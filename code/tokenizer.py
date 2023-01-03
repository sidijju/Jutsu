from enum import Enum

class Type(Enum):
    LPAREN = 0
    LSQB = 1
    LCB = 2
    RPAREN = 3
    RSQB = 4
    RCB = 5
    COLON = 6
    NOT = 7
    PLUS = 8
    MINUS = 9
    DIV = 10
    PERCENT = 11
    LT = 12
    GT = 13
    EQ = 14
    COMMA = 15
    DOT = 16
    IDIV = 17
    DSTAR = 18
    DEQ = 19
    NEQ = 20
    LEQ = 21
    GEQ = 22
    OR = 23
    AND = 24
    PLUSEQ = 25
    MINUSEQ = 26
    MULTEQ = 27
    DIVEQ = 28
    IDIVEQ = 29
    DSTAREQ = 30
    DEFINE = 31
    TRUE = 32
    FALSE = 33
    IF = 34
    ELIF = 35
    ELSE = 36
    RETURN = 37
    PRINT = 38
    INT = 39
    STRING = 40
    NAME = 41
    NEWLINE = 42
    EOF = 43
class Token:
    def __init__(self, type, value):
        self.type = type
        self.value = value

    def __repr__(self):
        if self.value:
            return "{" + self.toktype + ", " + self.value + "}"
        return "{" + self.toktype + "}"
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
                curr = input[current + consumed]
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