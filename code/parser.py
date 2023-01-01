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

    def pop(self):
        return self.children.pop()
        
    def peek(self):
        return self.children[-1]
class Parser:

    def __init__(self, tokens):

        self.parseFunctions = {
            "INT": self.parseInteger,
            "STRING": self.parseString,
            "NAME": self.parseName,
            "PLUS": self.parseBinaryOp,
            "MINUS": self.parseBinaryOp, 
            "MULT": self.parseBinaryOp, 
            "DIV": self.parseBinaryOp, 
            "PERCENT": self.parseBinaryOp, 
            "LT": self.parseBinaryOp, 
            "GT": self.parseBinaryOp,  
            "IDIV": self.parseBinaryOp,  
            "DSTAR": self.parseBinaryOp,  
            "DEQ": self.parseBinaryOp, 
            "NEQ": self.parseBinaryOp, 
            "LEQ": self.parseBinaryOp, 
            "GEQ": self.parseBinaryOp, 
            "OR": self.parseBinaryOp, 
            "AND": self.parseBinaryOp, 
            "EQ": self.parseAssignmentOp,
            "PLUSEQ": self.parseAssignmentOp,
            "MINUSEQ": self.parseAssignmentOp,
            "DIVEQ": self.parseAssignmentOp,
            "IDIVEQ": self.parseAssignmentOp,
            "DSTAREQ": self.parseAssignmentOp,
            "DEFINE": self.parseDefinition
        }

        self.ast = ASTNode("Program", "")
        current = 0
        while current < len(tokens):
            current, node = self.parseToken(tokens, current)
            self.ast.push(node)

    def parseToken(self, tokens, current):
        # TODO add other token types
        token = tokens[current]
        if token.toktype in self.parseFunctions:
            return self.parseFunctions[token.toktype](tokens, current)
        else:
            raise Exception("Invalid expression at %s during parsing" % (tokens[current]))
        
    def parseInteger(self, tokens, current):
        return current+1, ASTNode("Integer", tokens[current].value)

    def parseString(self, tokens, current):
        return current+1, ASTNode("String", tokens[current].value)

    def parseExpression(self, tokens, current):
        # TODO add expression parsing logic
        raise NotImplementedError

    def parseArgs(self, tokens, current):
        current += 1 # skip left parentheses
        curr = tokens[current]
        node = ASTNode("Args", "")
        if curr.toktype == 'RPAREN': # no argument case
            return node

        # parse first argument
        current, arg = self.parseExpression(tokens, current)
        node.push(arg)

        # if there are more arguments, will be in comma separated list
        while curr.toktype == 'COMMA':
            current, arg = self.parseExpression(tokens, current)
            node.push(arg)
            
        # if the token is not a comma, it should be the end of the list
        if curr.toktype != 'RPAREN':
            raise Exception("Invalid function arguments during parsing")
        return current+1, node 

    def parseName(self, tokens, current):
        if tokens[current+1].toktype == 'LPAREN':
            node = ASTNode("Call", tokens[current].value)
            current, args = self.parseArgs(tokens, current+1)
            node.push(args)
            return current, node
        else:
            return current+1, ASTNode("Variable", tokens[current].value)

    def parseBinaryOp(self, tokens, current):
        #TODO fix to account for order of operations
        node = ASTNode("BinaryOperation", tokens[current].value)
        current, rexpr = self.parseExpression(tokens, current+1)
        lexpr = self.ast.pop()
        node.push(lexpr)
        node.push(rexpr)
        return current, node

    def parseAssignmentOp(self, tokens, current):
        node = ASTNode("Assignment", "")
        lexpr = self.ast.peek()
        node.push(lexpr)
        op = tokens[current]
        current, rexpr = self.parseExpression(tokens, current+1)  
        if op.toktype != 'EQ':
            opnode = ASTNode("BinaryOperation", op.value[:-2])
            opnode.push(lexpr)
            opnode.push(rexpr)
            node.push(opnode)
        else:
            node.push(rexpr)
        return current, node

    def parseDefinition(self, tokens, current):
        # TODO add function definition parsing logic
        raise NotImplementedError
    
    def parseListBody(self, tokens, current):
        # TODO add list body parsing logic
        raise NotImplementedError