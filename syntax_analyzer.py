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

# Example usage
file_path = 'examples/Adder.java'
tokens = parse_java_code(file_path)

for token in tokens:
    print(token.type)
