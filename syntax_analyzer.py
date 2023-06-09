#### File: syntax_analyzer.py
#### Authors: Team 31 - BERNAD Thomas (50221636) & GUICHARD Lucas (50221623)
#### Date: June 8, 2023 (Spring Semester)
#### Description: 2023 Compiler Term Project - Chung Ang University
#### Professor: KIM Hyosu
#### Submission file: team_<your_team_number>.zip or .tar.gz


# Regular expressions module
import re


# Token class
class Token:
    def __init__(self, type: str, value: str):
        self.type = type
        self.value = value


def tokenize(source_code: str):
    # Define regular expressions for the 21 terminals
    patterns = [
        # vtype for the types of variables and functions
        ('vtype', r'int|double|boolean|char|String|void'),
        # num for signed integers
        ('num', r'-?\d+'),
        # character for a single character
        ('character', r"'.'"),
        # boolstr for Boolean strings
        ('boolstr', r'true|false'),
        # literal for literal strings
        ('literal', r'"[^"]*"'),
        # id for the identifiers of variables and functions
        ('id', r'[A-Za-z_]\w*'),
        # if for if statement
        ('if', r'if'),
        # else for else statement
        ('else', r'else'),
        # while for while statement
        ('while', r'while'),
        # return for return statement
        ('return', r'return'),
        # class for class declarations
        ('class', r'class'),
        # addsub for + and - arithmetic operators
        ('addsub', r'\+|-'),
        # multdiv for * and / arithmetic operators
        ('multdiv', r'\*|/'),
        # assign for assignment operators
        ('assign', r'='),
        # comp for comparison operators
        ('comp', r'==|!=|<=|>=|<|>'),
        # semi for semicolon
        ('semi', r';'),
        # comma for comma
        ('comma', r','),
        # lparen for (
        ('lparen', r'\('),
        # rparen for )
        ('rparen', r'\)'),
        # lbrace for {
        ('lbrace', r'{'),
        # rbrace for }
        ('rbrace', r'}'),
        # Used only for parsing
        ('whitespace', r'\s+')
    ]

    # Combine the regular expressions into a single pattern
    combined_pattern = '|'.join('(?P<%s>%s)' % pair for pair in patterns)

    # Initialize an empty list to store identified tokens
    tokens = []
    
    # Iterate over matches found in the source code
    for match in re.finditer(combined_pattern, source_code):
        # Get the type of the matched token
        token_type = match.lastgroup
        # Get the value of the matched token
        token_value = match.group(token_type)

        # Exclude whitespace tokens
        if token_type != 'whitespace':
            # Add the token to the list
            tokens.append(Token(token_type, token_value))

    # Return the list of identified tokens
    return tokens

def parse_java_code(file_path: str):
    # Open the file in read mode
    with open(file_path, 'r') as file:
        # Read the contents of the file
        source_code = file.read()
    # Call the `tokenize` function to extract tokens from the source code
    tokens = tokenize(source_code)
    # Return the list of tokens extracted from the source code
    return tokens


# ParseTreeNode class
# Basic structure for representing a parse tree
# Each node has a label and can have multiple children
class ParseTreeNode:
    def __init__(self, label):
        self.label = label
        self.children = []

    # Add the child to the list of children of the ParseTreeNode
    def add_child(self, child):
        if child is not None:
            self.children.append(child)


class SyntaxAnalyzer:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current_token = None
        self.token_index = -1
        self.parse_tree = None

    def advance(self):
        self.token_index += 1
        if self.token_index < len(self.tokens):
            self.current_token = self.tokens[self.token_index]
        else:
            self.current_token = None

    def parse(self):
        self.advance()
        self.parse_tree = self.parse_decls()
        if self.current_token is not None:
            self.error('Unexpected token')

    def error(self, message):
        raise Exception(f'Parsing error: {message}')

    def match(self, token_type):
        if self.current_token is not None and self.current_token.type == token_type:
            self.advance()
        else:
            self.error(f'Expected {token_type}, found {self.current_token.type}')

    def create_node(self, label):
        return ParseTreeNode(label)

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
            return None # Represents an empty declaration
        elif self.current_token.type == 'lparen':
            self.match('lparen')
            parse_tree = self.parse_arg()
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
        parse_tree.add_child(self.create_node(self.current_token.value))
        self.match('vtype')
        if self.current_token.type == 'id':
            parse_tree.add_child(self.create_node(self.current_token.value))
            self.match('id')
            if self.current_token.type == 'assign':
                parse_tree.add_child(self.parse_assign())
                self.match('semi')
        else:
            self.error(f'Invalid variable declaration: {self.current_token.type}')
        return parse_tree

    def parse_assign(self):
        parse_tree = self.create_node('ASSIGN')
        parse_tree.add_child(self.create_node(self.current_token.value))
        self.match('id')
        self.match('assign')
        parse_tree.add_child(self.parse_rhs())
        return parse_tree

    def parse_rhs(self):
        parse_tree = self.create_node('RHS')
        if self.current_token.type in ['id', 'num', 'literal', 'character', 'boolstr']:
            parse_tree.add_child(self.create_node(self.current_token.value))
            self.advance()
        else:
            self.error(f'Invalid right-hand side: {self.current_token.type}')
        return parse_tree

    def parse_fdecl(self):
        parse_tree = self.create_node('FDECL')
        parse_tree.add_child(self.create_node(self.current_token.value))
        self.match('vtype')
        parse_tree.add_child(self.create_node(self.current_token.value))
        self.match('id')
        self.match('lparen')
        parse_tree.add_child(self.parse_arg())
        self.match('rparen')
        self.match('lbrace')
        parse_tree.add_child(self.parse_block())
        parse_tree.add_child(self.parse_return())
        self.match('rbrace')
        return parse_tree

    def parse_arg(self):
        parse_tree = self.create_node('ARG')
        if self.current_token.type == 'vtype':
            parse_tree.add_child(self.create_node(self.current_token.value))
            self.match('vtype')
            parse_tree.add_child(self.create_node(self.current_token.value))
            self.match('id')
            parse_tree.add_child(self.parse_moreargs())
        else:
            parse_tree.add_child(None) # Epsilon production
        return parse_tree

    def parse_moreargs(self):
        parse_tree = self.create_node('MOREARGS')
        if self.current_token.type == 'comma':
            parse_tree.add_child(self.create_node(self.current_token.value))
            self.match('comma')
            parse_tree.add_child(self.create_node(self.current_token.value))
            self.match('vtype')
            parse_tree.add_child(self.create_node(self.current_token.value))
            self.match('id')
            parse_tree.add_child(self.parse_moreargs())
        else:
            parse_tree.add_child(None) # Epsilon production
        return parse_tree

    def parse_block(self):
        parse_tree = self.create_node('BLOCK')
        if self.current_token.type in ['vtype', 'id', 'if', 'while']:
            parse_tree.add_child(self.parse_stmt())
            parse_tree.add_child(self.parse_block())
        else:
            parse_tree.add_child(None) # Epsilon production
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
            parse_tree.add_child(self.create_node(self.current_token.value))
            self.match('boolstr')
        elif self.current_token.type in ['id', 'num', 'literal', 'character']:
            parse_tree.add_child(self.parse_expr())
            parse_tree.add_child(self.create_node(self.current_token.value))
            self.match('comp')
            parse_tree.add_child(self.parse_expr())
        else:
            self.error(f'Invalid condition: {self.current_token.type}')
        return parse_tree

    def parse_else(self):
        parse_tree = self.create_node('ELSE')
        if self.current_token.type == 'else':
            self.match('else')
            self.match('lbrace')
            parse_tree.add_child(self.parse_block())
            self.match('rbrace')
        else:
            parse_tree.add_child(None) # Epsilon production
        return parse_tree

    def parse_return(self):
        parse_tree = self.create_node('RETURN')
        self.match('return')
        parse_tree.add_child(self.parse_rhs())
        self.match('semi')
        return parse_tree

    def parse_cdecl(self):
        parse_tree = self.create_node('CDECL')
        parse_tree.add_child(self.create_node(self.current_token.value))
        self.match('class')
        parse_tree.add_child(self.create_node(self.current_token.value))
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
            parse_tree.add_child(None) # Epsilon production
        return parse_tree


#### EXAMPLE USAGE

# Generate tokens from Java source code
file_path = 'examples/Adder.java'
tokens = parse_java_code(file_path)

# Init our SyntaxAnalyzer with the obtained tokens
analyzer = SyntaxAnalyzer(tokens)

# Parse them to generate our tree
analyzer.parse()

# Print the parse tree
def print_parse_tree(node, indent=''):
    print(indent + node.label)
    for child in node.children:
        print_parse_tree(child, indent + '  ')
print_parse_tree(analyzer.parse_tree)
