from tokenizer import Type, Token
from enum import Enum

class ASTNodeType(Enum):
    Argument = 1
    AssignStmt = 2
    BinaryOp = 3
    Body = 4
    BooleanConst = 5
    CallStmt = 6
    ExitStmt = 7
    Expr = 8
    ForStmt = 9
    IfStmt = 10
    IntegerConst = 11
    LoopStmt = 12
    NilConst = 13
    ReturnStmt = 14
    Stmt = 15
    StringConst = 16
    UnaryOp = 17
    VarDecl = 18
    Variable = 19
    WhileStmt = 20
    Node = 21

class ASTNode:
    """Represent node in AST (Abstract Symbol Tree)"""
    
    def __init__(self, nodetype, value = ""):
        self.nodetype = nodetype
        self.value = value
        self.children = []

    def __repr__(self):
        if self.value:
            curr = "{" + self.nodetype + ", " + str(self.value) + "}"
        else:
            curr = "{" + self.nodetype + "}"

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
        Type.GT: 3,
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

    assignmentTypes = [Type.EQ]

    def __init__(self, tokens):
        self.ast = ASTNode(ASTNodeType.Node)
        self.tokens = tokens
        self.line = 1
        self.parseProgram()

    def next(self) -> Token:
        """Peek the next token"""
        return self.tokens[0]

    def consume(self) -> Token:
        """Consume a token"""
        return self.tokens.pop(0)
        
    def accept(self, *types):
        """Accept any type in types for the next token"""
        token = self.next()
        if token.type not in types:
            return False
        else:
            self.consume()
            return True
    
    def expect(self, type) -> Token:
        """Expect a certain type for the next token"""
        token = self.next().type
        if token != type:
            raise Exception("Unexpected token %s during parsing at line %d" % (token.name, self.line))
        else:
            return self.consume()

    def associative(self, type):
        if type == Type.DSTAR:
            return 0
        return 1
    
    def parseProgram(self):
        """Parse program"""
        # program:
        # | [stmt+] EOF

        # recursive implementation so we don't have
        # infinite loop if theres no EOF token
        if not self.accept(Type.EOF):
            node = self.parseStatement()
            self.line += 1
            if node:
                self.ast.push(node)
            if self.accept(Type.NEWLINE):
                self.parseProgram()

    def parseStatement(self):
        # stmt:
        # | simple_stmt
        # | compound_stmt
        node = self.parseSimpleStatement()
        return node if node else self.parseCompoundStatement()
        
    def parseSimpleStatement(self):
        # simple_stmt:
        # | assignment
        # | return_stmt

        try:
            return self.parseAssignment()
        except:
            pass

        try:
            return self.parseReturnStatement()
        except:
            pass

        raise Exception("Unexpected token %s during parsing at line %d" % (self.next(), self.line))

    def parseAssignment(self):
        # assignment:
        # NAME '=' expression
        # NAME augassign expression
        var = self.expect(Type.NAME)
        node = ASTNode(ASTNodeType.AssignStmt)
        varnode = ASTNode(ASTNodeType.Variable, var.name)
        node.push(var)
        if self.accept(Type.EQ):
            node.push(self.parseExpression())
            return node
        else:
            op = self.parseAugAssign()
            if op:
                op.push(varnode)
                op.push(self.parseExpression())
                node.push(op)
                return node
        raise Exception("Unable to parse line %d, unrecognized operator" % self.line)

    def parseAugAssign(self):
        # augassign:
        # | '+=' 
        # | '-=' 
        # | '*=' 
        # | '/=' 
        # | '//=' 
        # | '**='
        next = self.next()
        if self.accept(Type.PLUSEQ, Type.MINUSEQ, Type.MULTEQ, Type.DIVEQ, Type.IDIVEQ, Type.DSTAREQ):
            op = ASTNode(ASTNodeType.BinaryOp, next.name)
            return op

    def parseReturnStatement(self):
        # return_stmt:
        # 'release' expression
        self.expect(Type.RETURN)
        expr = self.parseExpression()
        node = ASTNode(ASTNodeType.ReturnStmt)
        node.push(expr)
        return node

    def parseCompoundStatement(self):
        # compound_stmt:
        # | function_def
        # | if_stmt
        if self.accept(Type.DEFINE):
            return self.parseFunctionDefinition()
        elif self.accept(Type.IF):
            return self.parseIfStatement()
        else:
            raise Exception("Unexpected token %s during parsing at line %d" % (next, self.line))

    def parseFunctionDefinition(self):
        # TODO add function definition parsing logic
        raise NotImplementedError

    def parseIfStatement(self):
        # if_statement:
        # | 'if' expression body
        self.expect(Type.IF)
        expr = self.parseExpression()
        block = self.parseBody()
        node = ASTNode(ASTNodeType.IfStmt)
        node.push(expr)
        node.push(block)
        return node
    
    def parseBody(self):
        # body:
        # | '{' body_prime
        self.expect(Type.LCB)
        node = ASTNode(ASTNodeType.Body)
        self.parseBlockPrime(node)
        return node
    
    def parseBodyPrime(self, node):
        # body_prime:
        # | statement body_prime
        # | '}'
        if self.accect(Type.RCB):
            self.consume()
        else:
            node.push(self.parseStatement())
            self.parseBodyPrime(node)

    def parseExpression(self):
        # expression:
        # | disjunction
        node = ASTNode(ASTNodeType.Expr)
        node.push(self.parseDisjunction())
        return node

    def parseDisjunction(self):
        # disjunction:
        # | conjunction ('or' conjunction)+
        # | conjunction
        conj = self.parseConjunction()
        if self.accept(Type.OR):
            node = ASTNode(ASTNodeType.BinaryOp, 'Or')
            right_conj = self.parseConjunction()
            node.push(conj)
            node.push(right_conj)

            while self.accept(Type.OR):
                outer_node = ASTNode(ASTNodeType.BinaryOp, 'Or')
                right_conj = self.parseConjunction()
                outer_node.push(node)
                outer_node.push(right_conj)
                node = outer_node
            return node
        else:
            return conj

    def parseConjunction(self):
        # conjunction:
        # | inversion ('and' inversion)+
        # | inversion
        inv = self.parseInversion()
        if self.accept(Type.AND):
            node = ASTNode(ASTNodeType.BinaryOp, 'And')
            right_inv = self.parseInversion()
            node.push(inv)
            node.push(right_inv)

            while self.accept(Type.AND):
                outer_node = ASTNode(ASTNodeType.BinaryOp, 'And')
                right_inv = self.parseInversion()
                outer_node.push(node)
                outer_node.push(right_inv)
                node = outer_node
            return node
        else:
            return inv

    def parseInversion(self):
        # inversion:
        # | 'not' inversion 
        # | binary_op
        if self.accept(Type.NOT):
            node = ASTNode(ASTNodeType.UnaryOp, 'Not')
            node.push(self.parseInversion())
        return self.parseBinaryOperator()
    
    def parseBinaryOperator(self):
        return self.parseSum()
    
    def parseSum(self):
        # sum:
        # | sum '+' term
        # | sum '-' term
        # | term
        raise NotImplementedError

    # def parseExpression(self):
    #     # expression_prime:
    #     # | unary_primitive
    #     # | binary_primitive
    #     # | atom
    #     node = self.parseUnaryPrimitive()
    #     if not node:
    #         node = self.parseBinaryPrimitive()
    #         if not node:
    #             node = self.parseAtom()
    #     if not node:
    #         raise Exception("Parsing error at line %d" % self.line)
    #     return node

    # def parseUnaryPrimitive(self):
    #     # unary_primitive:
    #     # | unary_operator expression
    #     # | 'print' expression
    #     op = self.parseUnaryOperator()
    #     if op:
    #         rexpr = self.parseExpression()
    #         op.push(rexpr)
    #         return op
    #     elif self.next().type == Type.PRINT:
    #         self.consume()
    #         node = ASTNode(ASTNodeType.UnaryOp, "Print")
    #         rexpr = self.parseExpression()
    #         node.push(rexpr)
    #         return node
    #     else:
    #         return None

    # def parseUnaryOperator(self):
    #     # unary_operator
    #     # | '!' | '-'
    #     if self.next().type in self.unaryPrecedenceTable:
    #         token = self.consume().type
    #         return ASTNode(ASTNodeType.UnaryOp, token.name)  
    #     return None

    # def parseBinaryPrimitive(self):
    #     # binary_primitive:
    #     # | binary_precedence(0)
    #     return self.parseBinaryPrecedence(0)

    # def parseBinaryPrecedence(self, precedence):
    #     # binary_precedence:
    #     # | binary_atom {binary_operator binary_precedence}
    #     node = self.parseBinaryAtom()
    #     op = self.parseBinaryOperator()
    #     if op and op.value >= precedence:
    #         nextPrecedence = self.associative(op.nodetype) + op.value
    #         rexpr = self.parseBinaryPrecedence(nextPrecedence)
    #         op.push(node)
    #         op.push(rexpr)
    #         node = op
    #         op = self.parseBinaryOperator()
    #     return node

    # def parseBinaryAtom(self):
    #     # binary_atom:
    #     # | unary_operator binary_precedence(q)
    #     # | '(' binary_primitive ')'
    #     # | atom
    #     op = self.parseUnaryOperator()
    #     if op:
    #         rexpr = self.parseBinaryPrecedence(op.value)
    #         op.push(rexpr)
    #         return op
    #     elif self.accept(Type.LPAREN):
    #         expr = self.parseBinaryPrimitive()
    #         self.expect(Type.RPAREN)
    #         return expr
    #     else:
    #         return self.parseAtom()

    # def parseBinaryOperator(self):
    #     # binary_operator:
    #     # 'or' | 'and' | '+' | '-' | '*' | '/' | '//' | '%' | '**' | '==' | '!=' | '<' | '>'
    #     token = self.next().type
    #     if token in self.binaryPrecedenceTable:
    #         self.consume()
    #         return ASTNode(ASTNodeType.BinaryOp, token.name)
    #     return None

    def parseAtom(self):
        # atom:
        # | INT
        # | STRING
        # | NAME
        # | TRUE
        # | FALSE
        token = self.next()
        nodemap = {
            Type.INT: ASTNodeType.IntegerConst,
            Type.STRING: ASTNodeType.StringConst,
            Type.NAME: ASTNodeType.Variable,
            Type.TRUE: ASTNodeType.BooleanConst,
            Type.FALSE: ASTNodeType.BooleanConst
        }

        if token.type in nodemap:
            self.consume()
            return ASTNode(nodemap[token.type], token.value)
        else:
            raise Exception("Unable to parse atom %s at line %d" % (token.type.name, self.line))
    
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