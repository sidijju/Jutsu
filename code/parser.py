class ASTNode:
    def __init__(self, nodetype, value):
        self.nodetype = nodetype
        self.value = value
        self.children = []

    def __repr__(self):
        curr = "{" + self.nodetype + ", " + self.value + "}"
        for c in self.children:
            curr += "\n\t" + c.__repr__
        return curr

    def push(self, node):
        self.children.append(node)

class Parser:

    binaryops = [
    "PLUS", 
    "MINUS", 
    "MULT", 
    "DIV", 
    "PERCENT", 
    "LT", 
    "GT", 
    "EQ", 
    "IDIV", 
    "DSTAR", 
    "DEQ",
    "NEQ",
    "LEQ",
    "GEQ",
    "PLUSEQ",
    "MINUSEQ",
    "DIVEQ",
    "IDIVEQ",
    "DSTAREQ",
    "OR",
    "AND"
    ]

    def __init__(self, tokens):
        self.ast = ASTNode("Program", "")
        current = 0
        while current < len(tokens):
            current, node = self.parseToken(tokens, current)
            self.ast.push(node)

    def parseToken(self, tokens, current):
        token = tokens[current]
        if token.toktype == 'INT':
            return self.parseInteger(tokens, current)
        elif token.toktype == 'STRING':
            return self.parseString(tokens, current)
        elif token.toktype in self.binaryops:
            node = ASTNode("BinaryOperation", token.value)
            current, rexpr = self.parseExpression(tokens, current + 1)
            lexpr = self.ast.pop()
            node.push(lexpr)
            node.push(rexpr)
            return current, node
        # TODO add other token types

    def parseInteger(self, tokens, current):
        return current + 1, ASTNode("Integer", tokens[current].value)

    def parseString(self, tokens, current):
        return current + 1, ASTNode("String", tokens[current].value)

    def parseExpression(self, tokens, current):
        # TODO add expression parsing logic
        raise NotImplementedError

    def parseLongExpression(self, tokens, current):
        # TODO add multi-line expression parsing logic
        raise NotImplementedError