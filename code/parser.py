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
    
    def __init__(self, nodetype, value = None):
        self.nodetype = nodetype
        self.value = value
        self.children = []

    def __repr__(self):
        if self.value is not None:
            curr = "{" + str(self.nodetype) + ", " + str(self.value) + "}"
        else:
            curr = "{" + str(self.nodetype) + "}"

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

    atommap = {
        Type.INT: ASTNodeType.IntegerConst,
        Type.STRING: ASTNodeType.StringConst,
        Type.NAME: ASTNodeType.Variable,
        Type.TRUE: ASTNodeType.BooleanConst,
        Type.FALSE: ASTNodeType.BooleanConst
    }

    def __init__(self, tokens):
        self.tokens = tokens
        self.current = 0
        self.backtrack = 0

        try:
            self.parseProgram()
        except Exception as e:
            print("Exception during parsing:")
            print(e)

    def next(self) -> Token:
        """Peek the next token"""
        return self.tokens[self.current]
    
    def previous(self) -> Token:
        """Peek the previously consumed token"""
        return self.tokens[self.current - 1]
    
    def atEnd(self):
        """Check if we are at end of file"""
        return self.next().type == Type.EOF

    def consume(self) -> Token:
        """Consume a token"""
        if not self.atEnd():
            self.current += 1
        return self.previous()
    
    def check(self, type):
        """Checks if next token is of a certain type"""
        if self.atEnd():
            return False
        return self.next().type == type

    def expect(self, type):
        """Expects next token to be of a certain type"""
        if (self.check(type)):
            return self.consume()
        return False
        
    def accept(self, *types):
        """Accept and consume any type in types for the next token"""
        for type in types:
            if self.check(type):
                self.consume()
                return True
        return False
    
    def save(self):
        self.backtrack = self.current
    
    def restore(self):
        self.current = self.backtrack

    def error(self):
        raise Exception("Error while parsing token %s at line %d" % (self.next(), self.next().line))
    
    def parseProgram(self):
        """Parse program"""
        # program:
        # | [stmt+] EOF
        self.ast = ASTNode(ASTNodeType.Node)
        while not self.atEnd():
            node = self.parseStatement()
            if node:
                self.ast.push(node)
            if not self.atEnd() and not self.accept(Type.NEWLINE):
                self.error()

    def parseStatement(self):
        # stmt:
        # | simple_stmt
        # | compound_stmt
        self.save()
        node = self.parseSimpleStatement()
        if node:
            return node
        else:
            self.restore()
        
        node = self.parseCompoundStatement()
        if node:
            return node
        else:
            self.restore()
        
    def parseSimpleStatement(self):
        # simple_stmt:
        # | assignment
        # | expression
        # | return_stmt
        # | print_stmt

        self.save()
        node = self.parseAssignment()
        if node:
            return node
        
        self.restore()
        node = self.parseExpression()
        if node:
            return node
        
        self.restore()
        node = self.parseReturnStatement()
        if node:
            return node
        
        self.restore()
        node = self.parsePrintStatement()
        if node:
            return node
    
    def parseAssignment(self):
        # assignment:
        # NAME '=' expression
        # NAME augassign expression
        var = self.expect(Type.NAME)
        if var:
            node = ASTNode(ASTNodeType.AssignStmt)
            varnode = ASTNode(ASTNodeType.Variable, var.value)
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

    def parseAugAssign(self):
        # augassign:
        # | '+=' 
        # | '-=' 
        # | '*=' 
        # | '/=' 
        # | '//=' 
        # | '**='
        if self.accept(Type.PLUSEQ, Type.MINUSEQ, Type.MULTEQ, Type.DIVEQ, Type.IDIVEQ, Type.DSTAREQ):
            return ASTNode(ASTNodeType.BinaryOp, self.previous().type)

    def parseReturnStatement(self):
        # return_stmt:
        # 'release' expression
        if self.expect(Type.RETURN):
            node = ASTNode(ASTNodeType.ReturnStmt)
            expr = self.parseExpression()
            node.push(expr)
            return node
        
    def parsePrintStatement(self):
        # print_stmt:
        # 'print' expression
        if self.expect(Type.PRINT):
            node = ASTNode(ASTNodeType.CallStmt, self.previous().type)
            expr = self.parseExpression()
            node.push(expr)
            return node

    def parseCompoundStatement(self):
        # compound_stmt:
        # | function_def
        # | if_stmt
        self.save()
        node = self.parseFunctionDefinition()
        if node:
            return node
        
        self.restore()
        node = self.parseIfStatement()
        if node:
            return node

    def parseFunctionDefinition(self):
        # function_def:
        # | 'jutsu' NAME '(' NAME* ')' body
        if self.expect(Type.DEFINE):
            if self.expect(Type.NAME):
                func_def = ASTNode(ASTNodeType.AssignStmt, self.previous().value)
                if self.expect(Type.LPAREN):
                    num_args = 0
                    num_commas = 0
                    while not self.accept(Type.RPAREN):
                        varname = self.expect(Type.NAME)
                        if varname:
                            num_args += 1
                            arg = ASTNode(ASTNodeType.VarDecl, varname)
                            func_def.push(arg)
                        else:
                            return

                        if self.accept(Type.COMMA):
                            num_commas += 1

                    if num_args > 0 and num_commas != num_args - 1:
                        self.error()
                        return
                    
                    body = self.parseBody()
                    func_def.push(body)
                    return func_def
            

    def parseIfStatement(self):
        # if_statement:
        # | 'if' expression body
        if self.expect(Type.IF):
            expr = self.parseExpression()
            body = self.parseBody()
            node = ASTNode(ASTNodeType.IfStmt)
            if expr:
                node.push(expr)
            if body:
                node.push(body)
            return node
    
    def parseBody(self):
        # body:
        # | '{' body_prime
        if self.expect(Type.LCB):
            node = ASTNode(ASTNodeType.Body)
            self.parseBodyPrime(node)
            return node
    
    def parseBodyPrime(self, node):
        # body_prime:
        # | statement NEWLINE body_prime
        # | '}'
        if not self.accept(Type.RCB):
            statement = self.parseStatement()
            if statement:
                self.accept(Type.NEWLINE)
                node.push(statement)
                self.parseBodyPrime(node)

    def parseExpression(self):
        # expression:
        # | disjunction
        disj = self.parseDisjunction()
        if disj:
            node = ASTNode(ASTNodeType.Expr)
            node.push(disj)
            return node

    def parseDisjunction(self):
        # disjunction:
        # | conjunction ('or' conjunction)*
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
        # | inversion ('and' inversion)*
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
        # | '!' inversion 
        # | comparison
        if self.accept(Type.NOT):
            node = ASTNode(ASTNodeType.UnaryOp, self.previous().type)
            node.push(self.parseInversion())
            return node
        return self.parseComparison()
    
    def parseComparison(self):
        # comparison:
        # | sum (compare_op sum)*
        return_op = self.parseSum()
        compare_op = self.parseComparisonOperator()
        while(compare_op):
            compare_op.push(return_op)
            compare_op.push(self.parseSum())
            return_op = compare_op
            compare_op = self.parseComparisonOperator()
        return return_op
    
    def parseComparisonOperator(self):
        # compare_op:
        # | '=='
        # | '!='
        # | '<='
        # | '<'
        # | '>='
        # | '>'
        if self.accept(Type.DEQ, Type.NEQ, Type.LEQ, Type.LT, Type.GEQ, Type. GT):
            return ASTNode(ASTNodeType.BinaryOp, self.previous().type)

    def parseSum(self):
        # sum:
        # | sum '+' term
        # | sum '-' term
        # | term

        # Actual Implementation (Right Recursive)

        # sum:
        # | term sum_prime
        term = self.parseTerm()
        op_prime = self.parseSumPrime()
        if op_prime:
            op_prime.push(term)
            return op_prime
        return term
    
    def parseSumPrime(self):
        # sum_prime:
        # | e
        # | '+' term sum_prime
        # | '-' term sum_prime
        if self.accept(Type.PLUS, Type.MINUS):
            node = ASTNode(ASTNodeType.BinaryOp, self.previous().type)
            term = self.parseTerm()
            sum_prime = self.parseSumPrime()
            if sum_prime:
                sum_prime.push(term)
                node.push(sum_prime)
            else:
                node.push(term)
            return node
        
    def parseTerm(self):
        # term:
        # term '*' factor
        # term '/' factor
        # term '//' factor
        # term '%' factor
        # factor

        # Actual Implementation (Right Recursive)
        # term:
        # factor term_prime
        factor = self.parseFactor()
        term_prime = self.parseTermPrime()
        if term_prime:
            term_prime.push(factor)
            return term_prime
        return factor
    
    def parseTermPrime(self):
        # term_prime:
        # | e
        # | '*' factor term_prime
        # | '/' factor term_prime
        # | '//' factor term_prime
        # | '%' factor term_prime
        if self.accept(Type.MULT, Type.DIV, Type.IDIV, Type.PERCENT):
            node = ASTNode(ASTNodeType.BinaryOp, self.previous().type)
            factor = self.parseFactor()
            term_prime = self.parseTermPrime()
            if term_prime:
                term_prime.push(factor)
                node.push(term_prime)
            else:
                node.push(factor)
            return node
        
    def parseFactor(self):
        # factor:
        # | '-' factor
        # | power
        if self.accept(Type.MINUS):
            node = ASTNode(ASTNodeType.UnaryOp, self.previous().type)
            node.push(self.parseFactor())
            return node
        return self.parsePower()
    
    def parsePower(self):
        # power:
        # | primary '**' factor
        # | primary
        atom = self.parsePrimary()
        if self.accept(Type.DSTAR):
            node = ASTNode(ASTNodeType.BinaryOp, self.previous().type)
            node.push(atom)
            node.push(self.parseFactor())
            return node
        return atom
    
    def parsePrimary(self):
        # primary:
        # | NAME '(' (expression | (expression ',')+) ')'
        # | atom
        if self.accept(Type.NAME):
            func_name = self.previous().value
            if self.accept(Type.LPAREN):
                node = ASTNode(ASTNodeType.CallStmt, func_name)
                while not self.accept(Type.RPAREN):
                    arg = ASTNode(ASTNodeType.Argument)
                    expr = self.parseExpression()
                    if expr:
                        arg.push(expr)
                        node.push(arg)
                    else:
                        # could also error here
                        return
                    
                    self.accept(Type.COMMA)
                return node
            return ASTNode(ASTNodeType.Variable, func_name)
        return self.parseAtom()

    def parseAtom(self):
        # atom:
        # | INT
        # | STRING
        # | NAME
        # | TRUE
        # | FALSE
        # | '(' expression ')'
        if self.accept(Type.INT, Type.STRING, Type.NAME):
            return ASTNode(self.atommap[self.previous().type], self.previous().value)
        elif self.accept(Type.TRUE):
            return ASTNode(self.atommap[self.previous().type], 1)
        elif self.accept(Type.FALSE):
            return ASTNode(self.atommap[self.previous().type], 0)
        elif self.accept(Type.LPAREN):
            expr = self.parseExpression()
            if expr and self.accept(Type.RPAREN):
                return expr
    
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