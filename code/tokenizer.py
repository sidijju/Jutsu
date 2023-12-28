from enum import Enum
class Type(Enum):
    # organization types
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
    MULT = 10
    DIV = 11
    PERCENT = 12
    LT = 13
    GT = 14
    EQ = 15
    COMMA = 16
    DOT = 17
    IDIV = 18
    DSTAR = 19
    OR = 20
    AND = 21
    DEFINE = 22
    TRUE = 23
    FALSE = 24
    IF = 25
    ELIF = 26
    ELSE = 27
    RETURN = 28
    PRINT = 29
    INT = 30
    STRING = 31
    NAME = 32
    NEWLINE = 33
    EOF = 34
    DEQ = 35
    NEQ = 36
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
        'or': Type.OR,
        'and': Type.AND,
        'jutsu': Type.DEFINE,
        'True': Type.TRUE,
        'False': Type.FALSE,
        'if': Type.IF,
        'elif': Type.ELIF,
        'else': Type.ELSE,
        'release': Type.RETURN,
        'print': Type.PRINT,
        # '+=': Type.PLUSEQ,
        # '-=': Type.MINUSEQ,
        # '*=': Type.MULTEQ,
        # '/=': Type.DIVEQ,
        # '//=': Type.IDIVEQ,
        # '**=': Type.DSTAREQ,
        # '==': Type.DEQ,
        # '!=': Type.NEQ,
        # '<=': Type.LEQ,
        # '>=': Type.GEQ
    }

    def __init__(self, input):
        self.level = 0
        self.input = input
        self.eof = len(self.input)

    def isalpha(self, char):
        return (ord(char) >= 65 and ord(char) <= 90) or (ord(char) >= 97 and ord(char) <= 122)

    def isnumeric(self, char):
        return ord(char) >= 48 and ord(char) <= 57

    def tokenizeWhitespace(self, current):
        """Tokenize whitespace and ignore commented lines"""
        if self.input[current] == ' ':
            return 1, None
        elif self.input[current] == '\n':
            if self.level == 0:
                return 1, Token(Type.NEWLINE, None)
            return 1, None
        elif self.input[current] == '#':
            consumed = 1
            while current + consumed < self.eof and self.input[current+consumed] != '\n':
                consumed += 1
            return consumed+1, None
        return 0, None
        
    def tokenizeMultiCharSymbol(self, current):
        """Tokenize a multi character symbol"""

        for symbol, token in self.multicharSymbols.items():
            curr = self.input[current]
            consumed = 0
            while consumed < len(symbol) and symbol[consumed] == curr:
                consumed += 1
                if current + consumed < self.eof:
                    curr = self.input[current + consumed]
                else:
                    return 0, None
            if consumed == len(symbol) and self.input[current:current+consumed] == symbol:
                return consumed, Token(token, None)
        return 0, None

    def tokenizeSymbol(self, current):
        """Tokenize a symbol"""

        if self.input[current] in self.symbols:
            return 1, Token(self.symbols[self.input[current]], None)
        elif self.input[current] in self.leftlevels:
            self.level += 1
            return 1, Token(self.leftlevels[self.input[current]], None)
        elif self.input[current] in self.rightlevels:
            self.level -= 1
            return 1, Token(self.rightlevels[self.input[current]], None)
        return 0, None
    
    def tokenizeInteger(self, current):
        """Tokenize an integer"""

        curr = self.input[current]
        consumed = 0
        while self.isnumeric(curr):
            consumed += 1
            if current + consumed < self.eof:
                curr = self.input[current+consumed]
            else:
                break
        if consumed != 0:
            return consumed, Token(Type.INT, self.input[current:current+consumed])
        return 0, None

    def tokenizeString(self, current):
        """Tokenize a string"""

        if self.input[current] == '"':
            consumed = 1
            curr = self.input[current + consumed]
            while curr != '"':
                consumed += 1
                if current + consumed < self.eof:
                    curr = self.input[current+consumed]
                else:
                    break
            if curr == '"':
                return consumed + 1, Token(Type.STRING, self.input[current+1:current+consumed])
            else:
                return 0, None
        return 0, None
    
    def tokenizeName(self, current):
        """Tokenize a user defined symbol (name)"""

        consumed = 0
        while self.isalpha(self.input[current + consumed]):
            if current + consumed + 1 < self.eof:
                consumed += 1
            else:
                break
        if consumed != 0:
            return consumed, Token(Type.NAME, self.input[current:current+consumed])
        return 0, None

    def tokenize(self):
        """Return list of tokens from input"""

        # look through and try each tokenizer in our list of tokenizers
        # the tokenizers are ordered to make sure we capture language 
        # specific symbol names before variable names
        # if a tokenizer is successful it will return a number 
        # of consumed tokens and a token from Type
        # we continue consuming tokens until there are no
        # more tokens left in the input

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
        while current < self.eof:
            tokenized = False
            for tokenizer in tokenizers:
                if tokenized:
                    break
                consumed, token = tokenizer(current)
                if consumed != 0:
                    current += consumed
                    tokenized = True
                if token:
                    tokens.append(token)
            if not tokenized:
                raise Exception("Unreadable or invalid character %c during tokenization" % (input[current]))
        tokens.append(Token(Type.EOF, None))
        return tokens 