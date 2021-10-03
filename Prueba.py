# Tokens
from typing import Text


DIGITS = '0123456789'
ALPHABET = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'


T_INT = 'T_INT'  # Entero*
T_FLT = 'T_FLT'  # Flotante*
T_SUMA = 'T_SUM'  # Suma*
T_MENOS = 'T_MENOS' #menos
T_MULT = 'T_MULT' #multiplicacion
T_DIV = 'T_DIV' #Divicion
T_OPE = 'T_OPE' # expreciones(<,>,==,&,|)*
T_FOR = 'T_FOR'    # for*
T_WHILE = 'T_WHILE'   # while*
T_DO = 'T_DO' #do*
T_CHAR = 'T_CHAR' #char
T_IF = 'T_IF' #if*
T_ELSE = 'T_ELSE' #else*
T_TO = 'T_TO' #to*
T_WRITE = 'WRITE'#write*
T_READ = 'T_READ' #read*
T_LBRA = 'T_LBRA' #braket Izquierdo*
T_RBRA = 'T_RBRA' #braket Derecho*
T_LLIS = 'T_LLIS' #[
T_RLIS = 'T_RIS' #]
T_LP = 'T_LP'  # Parentesis izquierdo*
T_RP = 'T_RP'  # Parentesis derecho*
T_TIPO = 'T_TIPO'  # Tipo de variable*
T_FUNC = 'T_FUNC'  # Function*
T_VOID = 'T_VOID'  # Void*
T_RETURN = 'T_RETURN' #return*
T_VARIABLE = 'T_VARIABLE' # Variable
T_EQUALS = 'T_EQUALS' #equals
T_EOF = 'T_EOF' #end of file



#Clase de Tokens
class Token: 
    def __init__(self,type,value = None):
        self.type = type
        self.value = value

    def __repr__(self):
        if self.value: return f'{self.type}:{self.value}'
        return f'{self.type}'

# Nodos para el arbol de syntaxis
class AST(object):
    pass

class UnaryOp(AST):
    def __init__(self, op, expr):
        self.token = self.op = op
        self.expr = expr

class BinOp(AST):
    def __init__(self, left, op, right):
        self.left = left
        self.token = self.op = op
        self.right = right

class Num(AST):
    def __init__(self, token):
        self.token = token
        self.value = token.value


#Parser
class Parser:
    def __init__(self,tokens):
        self.tokens =tokens
        self.token_idx = -1
        self.advance()
    
    def error(self):
        print('Invalid syntax')

    def advance(self):
        self.token_idx +=1
        if self.token_idx < len(self.tokens):
            self.current_token = self.tokens[self.token_idx]
        return self.current_token


    def eat(self, token_type):
        # compare the current token type with the passed token
        # type and if they match then "eat" the current token
        # and assign the next token to the self.current_token,
        # otherwise raise an exception.
        if self.current_token.type == token_type:
            self.current_token = self.advance()
        else:
            self.error()
    
    def factor(self):
       # """factor : INTEGER | LPAREN expr RPAREN"""
        token = self.current_token
        if token.type == T_SUMA:
            self.eat(T_SUMA)
            node = UnaryOp(token, self.factor())
            return node
        elif token.type == T_MENOS:
          self.eat(T_MENOS)
          node = UnaryOp(token, self.factor())
          return node
        elif token.type == T_INT:
            self.eat(T_INT)
            return Num(token)
        elif token.type == T_LP:
            self.eat(T_LP)
            node = self.expr()
            self.eat(T_RP)
            return node


    def term(self):
       # """term : factor ((MUL | DIV) factor)*"""
        node = self.factor()

        while self.current_token.type in (T_MULT, T_DIV):
            token = self.current_token
            if token.type == T_MULT:
                self.eat(T_MULT)
            elif token.type == T_DIV:
                self.eat(T_DIV)

            node = BinOp(left=node, op=token, right=self.factor())

        return node

    def expr(self):
       
        node = self.term()

        while self.current_token.type in (T_SUMA, T_MENOS):
            token = self.current_token
            if token.type == T_SUMA:
                self.eat(T_SUMA)
            elif token.type == T_MENOS:
                self.eat(T_MENOS)

            node = BinOp(left=node, op=token, right=self.term())

        return node

    def parse(self):
        return self.expr()
    
class NodeVisitor(object):
    def visit(self, node):
        method_name = 'visit_' + type(node).__name__
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        raise Exception('No visit_{} method'.format(type(node).__name__))

#interprete
class Interpreter(NodeVisitor):
    def __init__(self, parser):
        self.parser = parser

    def visit_BinOp(self, node):
        if node.op.type == T_SUMA:
            return self.visit(node.left) + self.visit(node.right)
        elif node.op.type == T_MENOS:
            return self.visit(node.left) - self.visit(node.right)
        elif node.op.type == T_MULT:
            return self.visit(node.left) * self.visit(node.right)
        elif node.op.type == T_DIV:
            return self.visit(node.left) / self.visit(node.right)

    def visit_Num(self, node):
        return node.value

    def visit_UnaryOp(self, node):
        op = node.op.type
        if op == T_SUMA:
         return +self.visit(node.expr)
        elif op == T_MENOS:
         return -self.visit(node.expr)

    def interpret(self):
        tree = self.parser.parse()
        return self.visit(tree)


#Lexer para ver asignar los valores a ids
class Lexer:
    def __init__(self,text):
        self.text = text
        self.pos = -1
        self.cc = None
        self.advance()
    
    def advance(self):
        self.pos += 1
        self.cc = self.text[self.pos] if self.pos < len(self.text) else None
    
    def make_Tokens(self):
        
        tokens = []

        while self.cc != None:
            if self.cc in ' \t':
                self.advance()
            elif self.cc in DIGITS:
                tokens.append(self.make_number())
            elif self.cc == "'":
                tokens.append(self.make_char())
                self.advance()
            elif self.cc == '+':
                tokens.append(Token(T_SUMA))
                self.advance()
            elif self.cc == '-':
                tokens.append(Token(T_MENOS))
                self.advance()
            elif self.cc == '*':
                tokens.append(Token(T_MULT))
                self.advance()
            elif self.cc == '/':
                tokens.append(Token(T_DIV))
                self.advance()
            elif self.cc == '(':
                tokens.append(Token(T_LP))
                self.advance()
            elif self.cc == ')':
                tokens.append(Token(T_RP))
                self.advance()
            elif self.cc == '<' or self.cc == '>' or self.cc == '&'or self.cc == '|':
                tokens.append(Token(T_OPE))
                self.advance()
            elif self.cc == '=':
                tokens.append(self.equals_maker())
                self.advance()
            elif self.cc == '{':
                tokens.append(Token(T_LBRA))
                self.advance()
            elif self.cc == '}':
                tokens.append(Token(T_RBRA))
                self.advance()
            elif self.cc == '[':
                tokens.append(Token(T_LLIS))
                self.advance()
            elif self.cc == ']':
                tokens.append(Token(T_RLIS))
                self.advance()
            elif self.text == 'for':
                tokens.append(Token(T_FOR))
                self.pos += len('for')
                self.advance()
            elif self.text == 'if':
                tokens.append(Token(T_IF))
                self.pos += len('if')
                self.advance()
            elif self.text == 'else':
                tokens.append(Token(T_ELSE))
                self.pos += len('else')
                self.advance()
            elif self.text == 'while':
                tokens.append(Token(T_WHILE))
                self.pos += len('while')
                self.advance()
            elif self.text == 'do':
                tokens.append(Token(T_DO))
                self.pos += len('do')
                self.advance()
            elif self.text == 'to':
                tokens.append(Token(T_TO))
                self.pos += len('to')
                self.advance()
            elif self.text == 'write':
                tokens.append(Token(T_WRITE))
                self.pos += len('write')
                self.advance()
            elif self.text == 'read':
                tokens.append(Token(T_READ))
                self.pos += len('read')
                self.advance()
            elif self.text == 'function':
                tokens.append(Token(T_FUNC))
                self.pos += len('function')
                self.advance()
            elif self.text == 'void':
                tokens.append(Token(T_VOID))
                self.pos += len('void')
                self.advance()
            elif self.text == 'return':
                tokens.append(Token(T_RETURN))
                self.pos += len('return')
                self.advance()
            elif 'int:'  in self.text :
                tokens.append(Token(T_TIPO))
                self.pos += len('int')
                self.advance()
            elif 'float:'  in self.text :
                tokens.append(Token(T_TIPO))
                self.pos += len('float')
                self.advance()
            elif 'char:' in self.text :
                tokens.append(Token(T_TIPO))
                self.pos += len('char')
                self.advance()
            elif self.cc in ALPHABET:
                tokens.append(self.make_variable())
                self.advance()
            else:
                print("ERROR")
                self.advance()
                

        return tokens

    def make_variable(self):
        v_str = ''
       
        while self.cc != None and self.cc in ALPHABET + DIGITS:
            v_str += self.cc
            self.advance()
        
        return Token(T_VARIABLE, v_str)



    def equals_maker(self):
        e_str = ''
        
        if self.text[self.pos+1] == '=':
            e_str = '=='
            self.advance()
            return Token(T_OPE,e_str)
        else:
            self.advance()
            return Token(T_EQUALS,'=')


    def make_char(self):
        e_str=''
        print(self.pos)
        if self.text[self.pos +1] in ALPHABET and self.text != None:
            e_str += "'" + self.text[self.pos + 1] + "'"
            print(e_str)
            self.pos +=3
            return Token(T_CHAR, e_str )


    def make_number(self):
        num_str = ''
        dcount = 0

        while self.cc != None and self.cc in DIGITS + '.':
            if self.cc == '.':
                if dcount == 1: break
                dcount += 1
                num_str += '.'
            else:
                num_str += self.cc
            self.advance()

        if dcount == 0:
            return Token(T_INT, int(num_str))
        else:
            return Token(T_FLT, float(num_str))


    def run(text):
        lexer = Lexer(text)
        tokens = lexer.make_Tokens()

        parser = Parser(tokens)
        interpreter = Interpreter(parser)
        result = interpreter.interpret()

        return result

 

