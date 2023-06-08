class Token:
    def __init__(self, token_type, lexeme):
        self.type = token_type
        self.lexeme = lexeme

tokens = [
    Token('vtype', 'int'),
    Token('id', 'x'),
    Token('semi', ';'),
    Token('vtype', 'float'),
    Token('id', 'y'),
    Token('lparen', '('),
    Token('rparen', ')'),
    Token('lbrace', '{'),
    Token('if', 'if'),
    Token('lparen', '('),
    Token('boolstr', 'true'),
    Token('comp', '=='),
    Token('boolstr', 'false'),
    Token('rparen', ')'),
    Token('lbrace', '{'),
    Token('rbrace', '}'),
    Token('rbrace', '}'),
] # This is the list of tokens that the lexer would produce

class SyntaxAnalyzer:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current_token = None
        self.token_index = -1
        self.parse_tree = None

    def parse(self):
        self.advance()
        self.parse_tree = self.parse_decls()
        if self.current_token is not None:
            self.error('Unexpected token')

    def advance(self):
        self.token_index += 1
        if self.token_index < len(self.tokens):
            self.current_token = self.tokens[self.token_index]
        else:
            self.current_token = None

    def error(self, message):
        raise Exception(f'Parsing error: {message}')

    def match(self, token_type):
        if self.current_token is not None and self.current_token.type == token_type:
            self.advance()
        else:
            self.error(f'Expected {token_type}, found {self.current_token.type}')

    def parse_decls(self):
        parse_tree = self.create_node('CODE')
        while self.current_token is not None:
            decl = self.parse_decl()
            if decl is not None:
                parse_tree.add_child(decl)
        return parse_tree

    def parse_decl(self):
        if self.current_token.type == 'vtype':
            return self.parse_vdecl()
        elif self.current_token.type == 'class':
            return self.parse_cdecl()
        elif self.current_token.type == 'semi':
            self.match('semi')
            return None  # Represents an empty declaration
        elif self.current_token.type == 'lparen':
            self.match('lparen')
            parse_tree = self.parse_args()
            self.match('rparen')
            return parse_tree
        elif self.current_token.type == 'lbrace':
            self.match('lbrace')
            parse_tree = self.parse_block()
            self.match('rbrace')
            return parse_tree
        else:
            self.error(f'Invalid declaration: {self.current_token.type}')


    def parse_vdecl(self):
        parse_tree = self.create_node('VDECL')
        parse_tree.add_child(self.create_node(self.current_token.lexeme))
        self.match('vtype')
        if self.current_token.type == 'id':
            parse_tree.add_child(self.create_node(self.current_token.lexeme))
            self.match('id')
            if self.current_token.type == 'assign':
                parse_tree.add_child(self.parse_assign())
                self.match('semi')
        else:
            self.error(f'Invalid variable declaration: {self.current_token.type}')
        return parse_tree

    def parse_assign(self):
        parse_tree = self.create_node('ASSIGN')
        parse_tree.add_child(self.create_node(self.current_token.lexeme))
        self.match('id')
        self.match('assign')
        parse_tree.add_child(self.parse_rhs())
        return parse_tree

    def parse_rhs(self):
        parse_tree = self.create_node('RHS')
        if self.current_token.type in ['id', 'num', 'literal', 'character', 'boolstr']:
            parse_tree.add_child(self.create_node(self.current_token.lexeme))
            self.advance()
        else:
            self.error(f'Invalid right-hand side: {self.current_token.type}')
        return parse_tree

    def parse_fdecl(self):
        parse_tree = self.create_node('FDECL')
        parse_tree.add_child(self.create_node(self.current_token.lexeme))
        self.match('vtype')
        parse_tree.add_child(self.create_node(self.current_token.lexeme))
        self.match('id')
        self.match('lparen')
        parse_tree.add_child(self.parse_args())
        self.match('rparen')
        self.match('lbrace')
        parse_tree.add_child(self.parse_block())
        parse_tree.add_child(self.parse_return())
        self.match('rbrace')
        return parse_tree

    def parse_args(self):
        parse_tree = self.create_node('ARGS')
        if self.current_token.type == 'vtype':
            parse_tree.add_child(self.create_node(self.current_token.lexeme))
            self.match('vtype')
            parse_tree.add_child(self.create_node(self.current_token.lexeme))
            self.match('id')
            parse_tree.add_child(self.parse_moreargs())
        else:
            parse_tree.add_child(None)  # Epsilon production
        return parse_tree

    def parse_moreargs(self):
        parse_tree = self.create_node('MOREARGS')
        if self.current_token.type == 'comma':
            parse_tree.add_child(self.create_node(self.current_token.lexeme))
            self.match('comma')
            parse_tree.add_child(self.create_node(self.current_token.lexeme))
            self.match('vtype')
            parse_tree.add_child(self.create_node(self.current_token.lexeme))
            self.match('id')
            parse_tree.add_child(self.parse_moreargs())
        else:
            parse_tree.add_child(None)  # Epsilon production
        return parse_tree

    def parse_block(self):
        parse_tree = self.create_node('BLOCK')
        if self.current_token.type in ['vtype', 'id', 'if', 'while']:
            parse_tree.add_child(self.parse_stmt())
            parse_tree.add_child(self.parse_block())
        else:
            parse_tree.add_child(None)  # Epsilon production
        return parse_tree

    def parse_stmt(self):
        parse_tree = self.create_node('STMT')
        if self.current_token.type == 'vtype':
            parse_tree.add_child(self.parse_vdecl())
        elif self.current_token.type == 'id':
            parse_tree.add_child(self.parse_assign())
            self.match('semi')
        elif self.current_token.type == 'if':
            parse_tree.add_child(self.parse_ifstmt())
        elif self.current_token.type == 'while':
            parse_tree.add_child(self.parse_whilestmt())
        else:
            self.error(f'Invalid statement: {self.current_token.type}')
        return parse_tree


    def parse_ifstmt(self):
        parse_tree = self.create_node('IFSTMT')
        self.match('if')
        self.match('lparen')
        parse_tree.add_child(self.parse_cond())
        self.match('comp')
        self.match('boolstr')
        self.match('rparen')
        parse_tree.add_child(self.parse_block())
        self.match('lbrace')
        parse_tree.add_child(self.parse_else())
        self.match('rbrace')
        return parse_tree

    def parse_else(self):
        parse_tree = self.create_node('ELSE')
        if self.current_token.type == 'else':
            self.match('else')
            self.match('lbrace')
            parse_tree.add_child(self.parse_block())
            self.match('rbrace')
        else:
            parse_tree.add_child(None)  # Epsilon production
        return parse_tree

    def parse_whilestmt(self):
        parse_tree = self.create_node('WHILESTMT')
        self.match('while')
        self.match('lparen')
        parse_tree.add_child(self.parse_cond())
        self.match('rparen')
        self.match('lbrace')
        parse_tree.add_child(self.parse_block())
        self.match('rbrace')
        return parse_tree

    def parse_cond(self):
        parse_tree = self.create_node('COND')
        if self.current_token.type == 'boolstr':
            parse_tree.add_child(self.create_node(self.current_token.lexeme))
            self.match('boolstr')
        elif self.current_token.type in ['id', 'num', 'literal', 'character']:
            parse_tree.add_child(self.parse_expr())
            parse_tree.add_child(self.create_node(self.current_token.lexeme))
            self.match('comp')
            parse_tree.add_child(self.parse_expr())
        else:
            self.error(f'Invalid condition: {self.current_token.type}')
        return parse_tree

    def parse_return(self):
        parse_tree = self.create_node('RETURN')
        self.match('return')
        parse_tree.add_child(self.parse_rhs())
        self.match('semi')
        return parse_tree

    def parse_cdecl(self):
        parse_tree = self.create_node('CDECL')
        parse_tree.add_child(self.create_node(self.current_token.lexeme))
        self.match('class')
        parse_tree.add_child(self.create_node(self.current_token.lexeme))
        self.match('id')
        self.match('lbrace')
        parse_tree.add_child(self.parse_odecl())
        self.match('rbrace')
        return parse_tree

    def parse_odecl(self):
        parse_tree = self.create_node('ODECL')
        if self.current_token.type in ['vtype', 'class']:
            parse_tree.add_child(self.parse_decl())
            parse_tree.add_child(self.parse_odecl())
        else:
            parse_tree.add_child(None)  # Epsilon production
        return parse_tree

    def create_node(self, label):
        return ParseTreeNode(label)


class ParseTreeNode:
    def __init__(self, label):
        self.label = label
        self.children = []

    def add_child(self, child):
        if child is not None:
            self.children.append(child)


analyzer = SyntaxAnalyzer(tokens)
analyzer.parse()
parse_tree = analyzer.parse_tree

# Printing the parse tree
def print_parse_tree(node, indent=''):
    print(indent + node.label)
    for child in node.children:
        print_parse_tree(child, indent + '  ')

print_parse_tree(parse_tree)
