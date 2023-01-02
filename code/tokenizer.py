class Token:
    def __init__(self, toktype, value):
        self.toktype = toktype
        self.value = value

    def __repr__(self):
        return "{" + self.toktype + ", " + self.value + "}"
class Tokenizer:

    leftlevels = {
        '(': "LPAREN",
        '[': "LSQB",
        '{': "LCB",
    }

    rightlevels = {
        ')': "RPAREN",
        ']': "RSQB",
        '}': "RCB",
    }

    symbols = {
        ':': "COLON",
        '!': "NOT",
        '+': "PLUS",
        '-': "MINUS",
        '*': "MULT",
        '/': "DIV",
        '%': "PERCENT",
        '<': "LT",
        '>': "GT",
        '=': "EQ",
        ',': "COMMA"
    }

    multicharSymbols = {
        '//': "IDIV",
        '**': "DSTAR",
        '==': "DEQ",
        '!=': "NEQ",
        '<=': "LEQ",
        '>=': "GEQ",
        'or': "OR",
        'and': "AND",
        '+=': "PLUSEQ",
        '-=': "MINUSEQ",
        '*=': "MULTEQ",
        '/=': "DIVEQ",
        '//=': "IDIVEQ",
        '**=': "DSTAREQ",
        'no jutsu': "DEFINE",
        'True': "TRUE",
        'False': "FALSE",
        'if': "IF",
        'elif': "ELIF",
        'else': "ELSE",
        'release': "RETURN",
        'print': "PRINT"
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
                return 1, Token("NEWLINE", input[current])
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
            return consumed, Token("INT", input[current:current+consumed])
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
                return consumed + 1, Token("STRING", input[current+1:current+consumed])
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
            return consumed, Token("NAME", input[current:current+consumed])
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
        return tokens