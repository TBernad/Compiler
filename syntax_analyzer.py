#### File: syntax_analyzer.py
#### Authors: Team 31 - BERNAD Thomas (50221636) & GUICHARD Lucas (50221623)
#### Date: June 8, 2023 (Spring Semester)
#### Description: 2023 Compiler Term Project - Chung Ang University
#### Professor: KIM Hyosu
#### Submission file: team_<your_team_number>.zip or .tar.gz


# Regular expressions module
import re
# Sys module to get program's arguments
import sys


# Token class
class Token:
    def __init__(self, type: str, value: str, line_number: int):
        self.type = type
        self.value = value
        self.line_number = line_number


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
        # Used to detect comment
        ('comment', r'//.*'),
        # id for the identifiers of variables and functions
        ('id', r'[A-Za-z_]\w*'),
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
    # Initialize the line number
    line_number = 1

    # Iterate over matches found in the source code
    for match in re.finditer(combined_pattern, source_code):
        # Get the type of the matched token
        token_type = match.lastgroup
        # Get the value of the matched token
        token_value = match.group(token_type)

        # Exclude whitespace tokens
        if token_type != 'whitespace' and token_type != 'comment':
            # Add the token to the list
            tokens.append(Token(token_type, token_value, line_number))

        # Update the line number if a newline character is encountered
        if '\n' in token_value:
            line_number += token_value.count('\n')

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


# Our syntax analyzer object
class SyntaxAnalyzer:
    def __init__(self, tokens):
        # List of tokens to be analyzed
        self.tokens = tokens
        # Current token being processed
        self.current_token = None
        # Index of the current token
        self.token_index = -1
        # The resulting parse tree
        self.parse_tree = None

    # To advance in our tree (analyze the next token)
    def advance(self):
        self.token_index += 1
        if self.token_index < len(self.tokens):
            self.current_token = self.tokens[self.token_index]
        else:
            self.current_token = None

    def parse(self):
        # Start by advancing to the first/next token
        self.advance()
        # Parse declarations
        self.parse_tree = self.parse_decls()
        if self.current_token is not None:
            # If there are remaining tokens, raise an error
            self.error('Unexpected token')

    def error(self, message):
        raise Exception(f'Parsing error (L{self.current_token.line_number}): {message}')

    def match(self, token_type):
        if self.current_token is not None and self.current_token.type == token_type:
            # If the current token matches the expected type, move to the next token
            self.advance()
        else:
            self.error(f'Expected {token_type}, found {self.current_token.type}')

    def create_node(self, label):
        # Create a parse tree node with the given label
        return ParseTreeNode(label)

    def parse_decls(self):
        # Create a root node for declarations
        parse_tree = self.create_node('CODE')
        while self.current_token is not None:
            # Parse a single declaration
            decl = self.parse_decl()
            if decl is not None:
                # Add the declaration to the parse tree
                parse_tree.add_child(decl)
        return parse_tree

    def parse_decl(self):
        # Match and consume any identifiers
        while self.current_token.type == 'id':
            self.match('id')
        # Parse variable declaration
        if self.current_token.type == 'vtype':
            return self.parse_vdecl()
        # Parse class declaration
        elif self.current_token.type == 'class':
            return self.parse_cdecl()
        # Match a semicolon for empty declaration
        elif self.current_token.type == 'semi':
            self.match('semi')
            return None # Represents an empty declaration
        elif self.current_token.type == 'lparen':
            self.match('lparen')
            # Parse function arguments
            parse_tree = self.parse_arg()
            self.match('rparen')
            return parse_tree
        elif self.current_token.type == 'lbrace':
            self.match('lbrace')
            # Parse block of code
            parse_tree = self.parse_block()
            self.match('rbrace')
            return parse_tree
        # Skip a closing brace for empty declaration
        elif self.current_token.type == 'rbrace':
            self.advance()
        else:
            self.error(f'Invalid declaration: {self.current_token.type}')

    def parse_vdecl(self):
        # Create a node for variable declaration
        parse_tree = self.create_node('VDECL')
        # Add variable type node
        parse_tree.add_child(self.create_node(self.current_token.value))
        # Match and consume the variable type token
        self.match('vtype')
        if self.current_token.type == 'id':
            # Add variable identifier node
            parse_tree.add_child(self.create_node(self.current_token.value))
            # Match and consume the variable identifier
            self.match('id')
            if self.current_token.type == 'assign':
                # Parse and add the assignment expression
                parse_tree.add_child(self.parse_assign())
                # Match and consume the semicolon token
                self.match('semi')
        else:
            self.error(f'Invalid variable declaration: {self.current_token.type}')
        return parse_tree

    def parse_assign(self):
        # Create a node for assignment expression
        parse_tree = self.create_node('ASSIGN')
        # Add assignment operator node
        parse_tree.add_child(self.create_node(self.current_token.value))
        # Match and consume the assignment operator
        self.match('assign')
        # Parse and add the expression on the right-hand side of the assignment
        parse_tree.add_child(self.parse_expr())
        return parse_tree

    def parse_rhs(self):
        # Create a node for right-hand side expression
        parse_tree = self.create_node('RHS')
        if self.current_token.type in ['id', 'num', 'literal', 'character', 'boolstr']:
            # Add the token value as a child node
            parse_tree.add_child(self.create_node(self.current_token.value))
            # Move to the next token
            self.advance()
        else:
            self.error(f'Invalid right-hand side: {self.current_token.type}')
        return parse_tree

    def parse_fdecl(self):
        # Create a node for function declaration
        parse_tree = self.create_node('FDECL')
        # Add return type node
        parse_tree.add_child(self.create_node(self.current_token.value))
        # Match and consume the return type token
        self.match('vtype')
        # Add function name node
        parse_tree.add_child(self.create_node(self.current_token.value))
        # Match and consume the function name
        self.match('id')
        # Match and consume the left parenthesis for function arguments
        self.match('lparen')
        # Parse and add the function arguments
        parse_tree.add_child(self.parse_arg())
        # Match and consume the right parenthesis for function arguments
        self.match('rparen')
        # Match and consume the left brace for the function block
        self.match('lbrace')
        # Parse and add the function block
        parse_tree.add_child(self.parse_block())
        # Parse and add the return statement
        parse_tree.add_child(self.parse_return())
        # Match and consume the right brace for the function block
        self.match('rbrace')
        return parse_tree

    def parse_factor(self):
        # Create a node for a factor in an expression
        parse_tree = self.create_node('FACTOR')
        if self.current_token.type == 'lparen':
            # Match and consume the left parenthesis
            self.match('lparen')
            # Parse and add the expression within parentheses
            parse_tree.add_child(self.parse_expr())
            # Match and consume the right parenthesis
            self.match('rparen')
        elif self.current_token.type in ['id', 'num', 'literal', 'character', 'boolstr']:
            # Create a node for the right-hand side
            parse_tree = self.create_node('RHS')
            # Add the token value as a child node
            parse_tree.add_child(self.create_node(self.current_token.value))
            # Move to the next token
            self.advance()
        else:
            self.error(f'Invalid right-hand side: {self.current_token.type}')
        return parse_tree

    def parse_term(self):
        # Create a node for a term in an expression
        parse_tree = self.create_node('TERM')
        # Parse and add the first factor
        parse_tree.add_child(self.parse_factor())
        while self.current_token is not None and self.current_token.type in ['addsub', 'multdiv']:
            # Add the operator node
            parse_tree.add_child(self.create_node(self.current_token.value))
            # Move to the next token
            self.advance()
            # Parse and add the next factor
            parse_tree.add_child(self.parse_factor())
        return parse_tree

    def parse_expr(self):
        # Create a node for an expression
        parse_tree = self.create_node('EXPR')
        # Parse and add the first term
        parse_tree.add_child(self.parse_term())
        while self.current_token is not None and self.current_token.type in ['addsub']:
            # Add the operator node
            parse_tree.add_child(self.create_node(self.current_token.value))
            # Move to the next token
            self.advance()
            # Parse and add the next factor
            parse_tree.add_child(self.parse_factor())
            while self.current_token is not None and self.current_token.type in ['addsub', 'multdiv']:
                # Add the operator node
                parse_tree.add_child(self.create_node(self.current_token.value))
                # Move to the next token
                self.advance()
                if self.current_token.type == 'lparen':
                    # Match and consume the left parenthesis
                    self.match('lparen')
                    # Parse and add the expression within parentheses
                    parse_tree.add_child(self.parse_expr())
                    # Match and consume the right parenthesis
                    self.match('rparen')
                elif self.current_token.type == 'id':
                    # Add identifier node
                    parse_tree.add_child(self.create_node(self.current_token.value))
                    # Match and consume the identifier
                    self.match('id')
                elif self.current_token.type in ['num', 'literal', 'character', 'boolstr']:
                    # Add value node
                    parse_tree.add_child(self.create_node(self.current_token.value))
                    # Move to the next token
                    self.advance()
                else:
                    self.error(f'Invalid factor: {self.current_token.type}')
            # Add the parse tree of the subexpression
            parse_tree.add_child(self.parse_tree)
        return parse_tree

    def parse_arg(self):
        # Create a node for function arguments
        parse_tree = self.create_node('ARG')
        if self.current_token.type == 'vtype':
            # Add variable type node
            parse_tree.add_child(self.create_node(self.current_token.value))
            # Match and consume the variable type
            self.match('vtype')
            # Add variable identifier node
            parse_tree.add_child(self.create_node(self.current_token.value))
            # Match and consume the variable identifier
            self.match('id')
            # Parse and add any additional arguments
            parse_tree.add_child(self.parse_moreargs())
        elif self.current_token.type == 'id':
            # Epsilon production - parse expression as an argument
            parse_tree.add_child(self.parse_expr())
        return parse_tree

    def parse_moreargs(self):
        # Create a node for more function arguments
        parse_tree = self.create_node('MOREARGS')
        if self.current_token.type == 'comma':
            # Add comma node
            parse_tree.add_child(self.create_node(self.current_token.value))
            # Match and consume the comma token
            self.match('comma')
            # Add variable type node
            parse_tree.add_child(self.create_node(self.current_token.value))
            # Match and consume the variable type
            self.match('vtype')
            # Add variable identifier node
            parse_tree.add_child(self.create_node(self.current_token.value))
            # Match and consume the variable identifier
            self.match('id')
            # Recursively parse and add any additional arguments
            parse_tree.add_child(self.parse_moreargs())
        else:
            # Epsilon production - no more arguments
            parse_tree.add_child(None)
        return parse_tree

    def parse_block(self):
        # Create a node for a block
        parse_tree = self.create_node('BLOCK')
        if self.current_token.type in ['vtype', 'id', 'if', 'while']:
            # Parse and add a statement
            parse_tree.add_child(self.parse_stmt())
            # Recursively parse and add more statements
            parse_tree.add_child(self.parse_block())
        else:
            # Epsilon production - no more statements
            parse_tree.add_child(None)
        return parse_tree

    def parse_stmt(self):
        # Create a node for a statement
        parse_tree = self.create_node('STMT')
        if self.current_token.type == 'vtype':
            # Parse and add a variable declaration
            parse_tree.add_child(self.parse_vdecl())
        elif self.current_token.type == 'id':
            # Parse and add an assignment
            parse_tree.add_child(self.parse_assign())
            # Match and consume the semicolon
            self.match('semi')
        elif self.current_token.type == 'if':
            # Match and consume the 'if' keyword
            self.match('if')
            # Match and consume the left parenthesis
            self.match('lparen')
            # Parse and add the condition
            parse_tree.add_child(self.parse_cond())
            # Match and consume the comparison operator
            self.match('comp')
            # Match and consume the boolean value
            self.match('boolstr')
            # Match and consume the right parenthesis
            self.match('rparen')
            # Parse and add the if block
            parse_tree.add_child(self.parse_block())
            # Match and consume the left brace
            self.match('lbrace')
            # Parse and add the else block (if present)
            parse_tree.add_child(self.parse_else())
            # Match and consume the right brace
            self.match('rbrace')
            # Add the parse tree of the subexpression
            parse_tree.add_child(self.parse_tree)
        elif self.current_token.type == 'while':
            # Match and consume the 'while' keyword
            self.match('while')
            # Match and consume the left parenthesis
            self.match('lparen')
            # Parse and add the condition
            parse_tree.add_child(self.parse_cond())
            # Match and consume the right parenthesis
            self.match('rparen')
            # Match and consume the left brace
            self.match('lbrace')
            # Parse and add the while block
            parse_tree.add_child(self.parse_block())
            # Match and consume the right brace
            self.match('rbrace')
            # Add the parse tree of the subexpression
            parse_tree.add_child(self.parse_tree)
        else:
            self.error(f'Invalid statement: {self.current_token.type}')
        return parse_tree

    def parse_cond(self):
        # Create a node for a condition
        parse_tree = self.create_node('COND')
        if self.current_token.type == 'boolstr':
            # Add boolean value node
            parse_tree.add_child(self.create_node(self.current_token.value))
            # Match and consume the boolean value
            self.match('boolstr')
        elif self.current_token.type in ['id', 'num', 'literal', 'character']:
            # Parse and add the first expression
            parse_tree.add_child(self.parse_expr())
            # Add comparison operator node
            parse_tree.add_child(self.create_node(self.current_token.value))
            # Match and consume the comparison operator
            self.match('comp')
            # Parse and add the second expression
            parse_tree.add_child(self.parse_expr())
        else:
            self.error(f'Invalid condition: {self.current_token.type}')
        return parse_tree

    def parse_else(self):
        # Create a node for an else block
        parse_tree = self.create_node('ELSE')
        if self.current_token.type == 'else':
            # Match and consume the 'else' keyword
            self.match('else')
            # Match and consume the left brace
            self.match('lbrace')
            # Parse and add the else block
            parse_tree.add_child(self.parse_block())
            # Match and consume the right brace
            self.match('rbrace')
        else:
            # Epsilon production - no else block
            parse_tree.add_child(None)
        return parse_tree

    def parse_return(self):
        # Create a node for a return statement
        parse_tree = self.create_node('RETURN')
        # Match and consume the 'return' keyword
        self.match('return')
        # Parse and add the right-hand side of the return expression
        parse_tree.add_child(self.parse_rhs())
        # Match and consume the semicolon
        self.match('semi')
        return parse_tree

    def parse_cdecl(self):
        # Create a node for a class declaration
        parse_tree = self.create_node('CDECL')
        # Add the class name node
        parse_tree.add_child(self.create_node(self.current_token.value))
        # Match and consume the 'class' keyword
        self.match('class')
        # Add the class identifier node
        parse_tree.add_child(self.create_node(self.current_token.value))
        # Match and consume the class identifier
        self.match('id')
        # Match and consume the left brace
        self.match('lbrace')
        while (self.current_token.type != 'lbrace'):
            # Skip tokens until the left brace is encountered
            self.advance()
        # Match and consume the left brace
        self.match('lbrace')
        # Parse and add the declarations within the class
        parse_tree.add_child(self.parse_odecl())
        # Match and consume the right brace
        self.match('rbrace')
        return parse_tree

    def parse_odecl(self):
        # Create a node for object declarations within a class
        parse_tree = self.create_node('ODECL')
        while self.current_token.type == 'id':
            # Match and consume the object identifiers
            self.match('id')
        if self.current_token.type in ['vtype', 'class']:
            # Parse and add a declaration
            parse_tree.add_child(self.parse_decl())
            # Recursively parse and add more declarations
            parse_tree.add_child(self.parse_odecl())
            while self.current_token.type == 'id':
                # Match and consume the object identifiers
                self.match('id')
                # Parse and add the final declaration
            parse_tree.add_child(self.parse_decl())
        else:
            # Epsilon production - no more declarations
            parse_tree.add_child(None)
        return parse_tree


# Print the parse tree
def print_parse_tree(node, indent=''):
    print(indent + node.label)
    for child in node.children:
        print_parse_tree(child, indent + '  ')


# Main
if __name__ == "__main__":
    # Get java source code file path
    file_path = sys.argv[1]

    # Generate tokens from Java source code
    tokens = parse_java_code(file_path)
    # Print tokens' value and type
    print("----------TOKENS----------")
    for token in tokens:
        print(token.value + "\t(L" + str(token.line_number) + ")" + "\t--->\t" + token.type)

    # Init our SyntaxAnalyzer with the obtained tokens
    analyzer = SyntaxAnalyzer(tokens)

    # Parse them to generate our tree and print it
    analyzer.parse()
    print("----------PARSE TREE----------")
    print_parse_tree(analyzer.parse_tree)
