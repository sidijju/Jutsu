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
        self.ast = ASTNode("Program", "")
        self.tokens = tokens
        current = 0
        while current < len(tokens):
            current, node = self.parseStatement(current)
            if node:
                self.ast.push(node)

    def expect(self, current, toktype):
        token = self.tokens[current]
        if token.toktype != toktype:
            raise Exception("Unexpected token during parsing - %s" % (self.tokens[current]))

    def parseStatement(self, current):
        # statement:
        # | compound_stmt NEWLINE
        # | simple_stmt NEWLINE
        # | NEWLINE
        try:
            return self.parseCompoundStatement(current)
        except Exception:
            try:
                return self.parseSimpleStatement(current)
            except Exception:
                self.expect(current, 'NEWLINE')
                return current+1, None
        
    def parseSimpleStatement(self, current):
        # simple_stmt:
        # | assignment
        # | expression
        try:
            return self.parseAssignment(current)
        except Exception:
            return self.parseExpression(current)

    def parseAssignment(self, current):
        # assignment:
        # | NAME '=' expression
        # | NAME '+=' expression
        # | NAME '-=' expression
        # | NAME '*=' expression
        # | NAME '/=' expression
        # | NAME '//=' expression
        # | NAME '**=' expression
        
        self.expect(current, 'NAME')
        node = ASTNode("Assignment", "")
        name = ASTNode("Variable", self.tokens[current].value)
        node.push(name)   
        op = self.tokens[current+1]
        current, rexpr = self.parseExpression(current+2)  
        if op.toktype != 'EQ':
            opnode = ASTNode("BinaryOperation", op.value[:-2])
            opnode.push(name)
            opnode.push(rexpr)
            node.push(opnode)
        else:
            node.push(rexpr)
        return current, node

    def parseExpression(self, current):
        # expression:
        # | unary_primitive
        # | binary_primitive
        # | atom
        raise NotImplementedError

    def parseCompoundStatement(self, current):
        raise NotImplementedError                    

    def parseArgs(self, current):
        current += 1 # skip left parentheses
        curr = self.tokens[current]
        node = ASTNode("Args", "")
        if curr.toktype == 'RPAREN': # no argument case
            return node

        # parse first argument
        current, arg = self.parseExpression(current)
        node.push(arg)

        # if there are more arguments, will be in comma separated list
        while curr.toktype == 'COMMA':
            current, arg = self.parseExpression(current)
            node.push(arg)
            
        # if the token is not a comma, it should be the end of the list
        if curr.toktype != 'RPAREN':
            raise Exception("Invalid function arguments during parsing")
        return current+1, node 

    def parseBinaryOp(self, current):
        #TODO fix to account for order of operations
        node = ASTNode("BinaryOperation", self.tokens[current].value)
        current, rexpr = self.parseExpression(current+1)
        lexpr = self.ast.pop()
        node.push(lexpr)
        node.push(rexpr)
        return current, node

    def parseDefinition(self, current):
        # TODO add function definition parsing logic
        raise NotImplementedError
    
    def parseListBody(self, current):
        # TODO add list body parsing logic
        raise NotImplementedError

    def parseAtom(self, current):
        # atom:
        # | INT
        # | STRING
        # | NAME
        # | TRUE
        # | FALSE
        token = self.tokens[current]
        if token.toktype == 'INT':
            return current+1, ASTNode("Integer", token.value)
        elif token.toktype == 'STRING':
            return current+1, ASTNode("String", token.value)
        elif token.toktype == 'NAME':
            return current+1, ASTNode("Variable", token.value)
        elif token.toktype == 'TRUE':
            return current+1, ASTNode("Boolean", token.value)
        elif token.toktype == 'FALSE':
            return current+1, ASTNode("Boolean", token.value)
        else:
            raise Exception("Unexpected token during parsing - %s" % (token.value))