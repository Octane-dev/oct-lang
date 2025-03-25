import ply.lex as lex
#from tokens import tokens

# define tokens available
tokens = (
    'VARIABLE',
    'ASSIGN',
    'NUMBER',
    'DISPLAY',
    'LSQUARE',
    'RSQUARE',
    'STRING',
    'NEWLINE',
    'EQUALS',
    'ADD',
    'SUBTRACT',
    'MULTIPLY',
    'DIVIDE'
)

# define values of tokens
#t_VAR = r'v'
t_ASSIGN = r'=='
t_EQUALS = r'==='
t_LSQUARE = r'\['
t_RSQUARE = r'\]'
# t_ADD = r'+' ########## USED FOR MATHS AND CONCATENATION
# t_SUBTRACT = r'-'
# t_MULTIPLY = r'*'
# t_DIVIDE = r'/'
#t_ARROW = r'==>'
#t_SMALL_ARROW = r'-->'

t_ignore_COMMENT = r'\!!.*'  # comment is !!

def t_STRING(t):
    r'\"([^\"\n]|(\\\"))*\"|\'([^\'\n]|(\\\'))*\''
    t.value = t.value[1:-1]  # Extract the string value without the quotes
    return t

def t_VARIABLE(t):
    r'v\[[a-zA-Z_][a-zA-Z0-9_]*\]'
    t.value = t.value[2:-1]  # Extract the variable name from the token
    return t

def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t

def t_DISPLAY(t):
    r'display'
    return t

# Newline rule
def t_NEWLINE(t):
    r'\r?\n'
    t.lexer.lineno += 1
    return t

# Ignored characters (whitespace)
t_ignore = ' \t'

# Error handling
def t_error(t):
    # print(f"Invalid character: {t.value[0]}")
    t.lexer.skip(1)

# Build lexer
lexer = lex.lex()
#        print(token)

# Test the lexer with an input string
#test_lexer("v[variable_name] == 0")
