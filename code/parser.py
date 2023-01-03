from tokenizer import Type
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

    binaryPrecedenceTable = {
        Type.OR: 0,
        Type.AND: 1,
        Type.DEQ: 3,
        Type.NEQ: 3,
        Type.LT: 3,
        Type.LEQ: 3,
        Type.GT: 3,
        Type.GEQ: 3,
        Type.PLUS: 4,
        Type.MINUS: 4,
        Type.MULT: 5,
        Type.DIV: 5,
        Type.IDIV: 5,
        Type.PERCENT: 5,
        Type.DSTAR: 7
    }

    unaryPrecedenceTable = {
        Type.NOT: 2,
        Type.MINUS: 6
    }

    assignmentTypes = [Type.EQ, Type.DEQ, Type.PLUSEQ, Type.MINUSEQ, Type.MULTEQ, Type.DIVEQ, Type.IDIVEQ, Type.DSTAREQ]

    def __init__(self, tokens):
        # program:
        # | statement NEWLINE program
        # | EOF
        self.ast = ASTNode("Program", "")
        self.tokens = tokens
        self.line = 0
        while self.next().type != Type.EOF:
            node = self.parseStatement()
            self.expect(Type.NEWLINE)
            self.line += 1
            if node:
                self.ast.push(node)

    def next(self):
        return self.tokens[0]

    def consume(self):
        return self.tokens.pop(0)

    def accept(self, type):
        token = self.next()
        if token.type != type:
            return False
        else:
            return True
    
    def expect(self, type):
        token = self.next()
        if token.type != type:
            raise Exception("Unexpected token during parsing at line %d" % (self.line))
        else:
            self.consume()

    def associative(self, type):
        if type == Type.DSTAR:
            return 0
        return 1

    def parseStatement(self):
        # statement:
        # | 'if' if_definition
        # | 'jutsu' function_definition
        # | 'release' expression
        # | expression
        raise NotImplementedError

    def parseExpression(self):
        # expression:
        # | expression_prime {assignment}
        expr = self.parseExpressionPrime()
        if self.next() in self.assignmentTypes:
            if expr.nodetype != 'Id':
                raise Exception("Parsing error at line %d" % self.line)
            return self.parseAssignment(expr)
        return expr

    def parseAssignment(self, assignee):
        # assignment:
        # ('=' | '+=' | '-=' | '*=' | '/=' | '//=' | '**=') expression
        raise NotImplementedError

    def parseExpressionPrime(self):
        # expression_prime:
        # | unary_primitive
        # | binary_primitive
        # | atom
        current, node = self.parseUnaryPrimitive(current)
        if not node:
            current, node = self.parseBinaryPrimitive(current)
            if not node:
                current, node = self.parseAtom(current)
        return current, node

    def parseUnaryPrimitive(self):
        # unary_primitive:
        # | unary_operator expression
        # | 'print' expression
        current, op = self.parseUnaryOperator(current)
        if op:
            current, rexpr = self.parseExpression(current)
            op.push(rexpr)
            return current, op
        elif self.tokens[current].type == Type.PRINT:
            node = ASTNode("UnaryOperation", "Print")
            current, rexpr = self.parseExpression(current+1)
            node.push(rexpr)
            return current, node
        else:
            return current, None

    def parseUnaryOperator(self):
        # unary_operator
        # | '!' | '-'
        token = self.tokens[current].type
        if token in self.unaryPrecedenceTable:
            return current+1, ASTNode(token, self.unaryPrecedenceTable[token])
        return current, None

    def parseBinaryPrimitive(self):
        # binary_primitive:
        # | binary_precedence(0)
        return self.parseBinaryPrecedence(current, 0)

    def parseBinaryPrecedence(self, precedence):
        # binary_precedence:
        # | binary_atom {binary_operator binary_precedence}
        current, node = self.parseBinaryAtom(current)
        current, op = self.parseBinaryOperator(current)
        while op and op.value >= precedence:
            nextPrecedence = self.associative(op.nodetype) + op.value
            current, rexpr = self.parseBinaryPrecedence(current, nextPrecedence)
            op.push(node)
            op.push(rexpr)
            node = op
            current, op = self.parseBinaryOperator(current)
        return current, node

    def parseBinaryAtom(self):
        # binary_atom:
        # | unary_operator binary_precedence(q)
        # | '(' binary_primitive ')'
        # | atom
        current, op = self.parseUnaryOperator(current)
        if op:
            current, rexpr = self.parseBinaryPrecedence(current, op.value)
            op.push(rexpr)
            return current, op
        elif self.tokens[current].type == Type.LPAREN:
            current, expr = self.parseBinaryPrimitive(current+1)
            self.expect(current, 'RPAREN')
            return current+1, expr
        else:
            return self.parseAtom(current)

    def parseBinaryOperator(self):
        # binary_operator:
        # 'or' | 'and' | '+' | '-' | '*' | '/' | '//' | '%' | '**' | '==' | '!=' | '<' | '>' | '<=' | '>='
        token = self.tokens[current].toktype
        if token in self.binaryPrecedenceTable:
            return current+1, ASTNode(token, self.binaryPrecedenceTable[token])
        return current, None

    def parseAtom(self):
        # atom:
        # | INT
        # | STRING
        # | NAME
        # | TRUE
        # | FALSE
        token = self.next()
        nodemap = {
            Type.INT: "Integer",
            Type.STRING: "String",
            Type.NAME: "Id",
            Type.TRUE: "Boolean",
            Type.FALSE: "Boolean"
        }

        if token.type in nodemap:
            self.consume()
            return ASTNode(nodemap[token.type], token.value)
        else:
            raise Exception("Unable to parse atom at line %d" % self.line)

    def parseDefinition(self):
        # TODO add function definition parsing logic
        raise NotImplementedError
    
    def parseListBody(self):
        # TODO add list body parsing logic
        raise NotImplementedError           

    def parseArgs(self):
        self.consume() # skip left parentheses
        node = ASTNode("Args", "")
        if self.accept('RPAREN'): # no argument case
            return node

        # parse first argument
        node.push(self.parseExpression())

        # if there are more arguments, will be in comma separated list
        while self.accept('COMMA'):
            node.push(self.parseExpression())
            
        # if the token is not a comma, it should be the end of the list
        self.expect('RPAREN')
        return node 
