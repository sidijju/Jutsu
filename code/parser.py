from tokenizer import Type
class ASTNode:
    def __init__(self, nodetype, value):
        self.nodetype = nodetype
        self.value = value
        self.children = []

    def __repr__(self):
        curr = "{" + self.nodetype + ", " + str(self.value) + "}"
        for c in self.children:
            s = c.__repr__()
            s = s.split('\n')
            s = ['\t' + line for line in s]
            s = '\n'.join(s)
            curr += "\n" + s
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
        # | statement program
        # | EOF
        self.ast = ASTNode("Program", "")
        self.tokens = tokens
        self.line = 1
        while self.next().type != Type.EOF:
            node = self.parseStatement()
            self.line += 1
            if node:
                self.ast.push(node)
            if self.accept(Type.NEWLINE):
                continue

    def next(self):
        return self.tokens[0]

    def consume(self):
        return self.tokens.pop(0)

    def accept(self, type):
        token = self.next()
        if token.type != type:
            return False
        else:
            self.consume()
            return True
    
    def expect(self, type):
        token = self.next().type
        if token != type:
            raise Exception("Unexpected token %s during parsing at line %d" % (token.name, self.line))
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
        # | 'release' expression NEWLINE
        # | expression NEWLINE
        next = self.next()
        if next.type == Type.IF:
            return self.parseIfStatement()
        elif next.type == Type.DEFINE:
            return self.parseDefinition()
        elif next.type == Type.RETURN:
            self.consume()
            expr = self.parseExpression()
            node = ASTNode("Return", "")
            node.push(expr)
            return node
        else:
            return self.parseExpression()

    def parseExpression(self):
        # expression:
        # | expression_prime {assignment}
        expr = self.parseExpressionPrime()
        if self.next().type in self.assignmentTypes:
            if expr.nodetype != 'Id':
                raise Exception("Parsing error at line %d" % self.line)
            return self.parseAssignment(expr)
        return expr

    def parseExpressionPrime(self):
        # expression_prime:
        # | unary_primitive
        # | binary_primitive
        # | atom
        node = self.parseUnaryPrimitive()
        if not node:
            node = self.parseBinaryPrimitive()
            if not node:
                node = self.parseAtom()
        if not node:
            raise Exception("Parsing error at line %d" % self.line)
        return node

    def parseUnaryPrimitive(self):
        # unary_primitive:
        # | unary_operator expression
        # | 'print' expression
        op = self.parseUnaryOperator()
        if op:
            rexpr = self.parseExpression()
            op.push(rexpr)
            return op
        elif self.next().type == Type.PRINT:
            self.consume()
            node = ASTNode("UnaryOperation", "Print")
            rexpr = self.parseExpression()
            node.push(rexpr)
            return node
        else:
            return None

    def parseUnaryOperator(self):
        # unary_operator
        # | '!' | '-'
        if self.next().type in self.unaryPrecedenceTable:
            token = self.consume()
            return ASTNode(token, self.unaryPrecedenceTable[token])
        return None

    def parseBinaryPrimitive(self):
        # binary_primitive:
        # | binary_precedence(0)
        return self.parseBinaryPrecedence(0)

    def parseBinaryPrecedence(self, precedence):
        # binary_precedence:
        # | binary_atom {binary_operator binary_precedence}
        node = self.parseBinaryAtom()
        op = self.parseBinaryOperator()
        while op and op.value >= precedence:
            nextPrecedence = self.associative(op.nodetype) + op.value
            rexpr = self.parseBinaryPrecedence(nextPrecedence)
            op.push(node)
            op.push(rexpr)
            node = op
            op = self.parseBinaryOperator()
        return node

    def parseBinaryAtom(self):
        # binary_atom:
        # | unary_operator binary_precedence(q)
        # | '(' binary_primitive ')'
        # | atom
        op = self.parseUnaryOperator()
        if op:
            rexpr = self.parseBinaryPrecedence(op.value)
            op.push(rexpr)
            return op
        elif self.accept(Type.LPAREN):
            expr = self.parseBinaryPrimitive()
            self.expect(Type.RPAREN)
            return expr
        else:
            return self.parseAtom()

    def parseBinaryOperator(self):
        # binary_operator:
        # 'or' | 'and' | '+' | '-' | '*' | '/' | '//' | '%' | '**' | '==' | '!=' | '<' | '>' | '<=' | '>='
        token = self.next().type
        if token in self.binaryPrecedenceTable:
            self.consume()
            return ASTNode(token.name, self.binaryPrecedenceTable[token])
        return None

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
    
    def parseAssignment(self, assignee):
        # assignment:
        # ('=' | '+=' | '-=' | '*=' | '/=' | '//=' | '**=') expression
        assert assignee.nodetype == 'Id'
        token = self.consume().type
        node = ASTNode("Assignment", "")
        node.push(assignee)
        expr = self.parseExpression()
        if token == Type.EQ:
            node.push(expr)
            return node
        elif token.type in [Type.PLUSEQ, Type.MINUSEQ, Type.MULTEQ, Type.DIVEQ, Type.IDIVEQ, Type.DSTAREQ]:
            op = ASTNode(token.name, "")
            op.push(assignee)
            op.push(expr)
            node.push(op)
        else:
            raise Exception("Unable to parse atom at line %d, unrecognized operator" % self.line)
    
    def parseIfStatement(self):
        raise NotImplementedError

    def parseDefinition(self):
        # TODO add function definition parsing logic
        raise NotImplementedError
    
    def parseListBody(self):
        # TODO add list body parsing logic
        raise NotImplementedError           

    def parseArgs(self):
        self.consume() # skip left parentheses
        node = ASTNode("Args", "")
        if self.accept(Type.RPAREN): # no argument case
            return node

        # parse first argument
        node.push(self.parseExpression())

        # if there are more arguments, will be in comma separated list
        while self.accept(Type.COMMA):
            node.push(self.parseExpression())
            
        # if the token is not a comma, it should be the end of the list
        self.expect(Type.RPAREN)
        return node