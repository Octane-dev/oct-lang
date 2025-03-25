# -------------------------------------------------------- OCTANIUM BETA V 0.0.0.7 --------------------------------------------------------
# Main Compiling proccess
# Importing Seperate Phases
import lark
import os
import lexer as lx
import parser_1 as ps
from semantic import SemanticAnalyzer
import executer as ex
import errors as er
import sys

print(sys.version)
ver = "0.0.0.7 BETA"

# Current Syntax:
# v[variable_name] == 0 | 1 (operator) 1 | "hello"+"bob" - defining variables
# c[variable_name] == 0 | "text" - defining constant
# display["message"] - displays message
# display[variable] - displays variable
# display["{{variable}}"] - displays f-string
# v[variable_name] == i["input text" | "text {{variable}}" | variable] - input
# f[func_name(parameters (none,one or many) --> {statements})] - define function
# r[func_name(parameters)] - call/run function
# v[variable_name] == r[func_name(parameters)] - assign return of func to variable
# !!whatever - comments

# Notes:
# Adding, subtracting, multiplying, dividing and concatenation work.
# defining constants work, functionality not there yet.
# simple inputs now available - still need to implement different (str,int,float)
# functions and logic work. function params dont work just yet.

# NEXT STEPS:
# stackable concatenation and complex maths.
# can attempt to get constants (c[contant_name]) - usable but not changeable and global.
# read functions (pass-ins and returns)

# While being built, will read in file for ease
def read_file(filename):
	with open(filename, 'r') as file:
		file_contents = file.read()
	# print(file_contents)
	extension = os.path.splitext(filename)[1]
	if extension != ".oct":
		print("Failed to find executable file.\nExiting program")
		raise SystemExit(1)
	return file_contents

# Compile program
def compile_program(program):
	# LEXILE ANALYSIS
	lexer = lx.lexer

	lexer.input(program)
	while True:
		token = lexer.token()
		if not token:
			break
		# print(token)

	# PARSE TREE
	try:
		# The code that might raise a SyntaxError
		tree = ps.parse(program)  # This is where the parsing happens
	except lark.exceptions.UnexpectedCharacters as e:
		# Catch the specific error
		print(f"SyntaxError: Unexpected character '{e.char}' at line {e.line} column {e.column}.")
	except Exception as e:
		# Catch any other general exceptions (not just SyntaxErrors)
		print(f"Error: {e}")
	print(tree.pretty())
	#print(tree)

	# ANALYZE TREE
	analyzer = SemanticAnalyzer()
	try:
		analyzer.analyze(tree, filename, 'prog')
	except SyntaxError as e:
		print(f"SyntaxError: {e}\nExiting program.")
		# Stop further execution
		raise SystemExit(1)
	#except NameError as e:
	#    print(f"NameError: {e}\nExiting program.")
		# Stop further execution
	#    raise SystemExit(1)


	generated_code = analyzer.return_values()

	return generated_code

#    # CODE GENERATION
#    code_generator = cg.CodeGenerator()
#    generated_code = code_generator.generate_code(tree)
#    print(generated_code)

	#return generated_code

	#INTERPRET CODE AND EXECUTE
	#interpreter = cg.Interpreter()
	#interpreter.execute_code(generated_code)
	#return generated_code


# File and compile
if __name__ == "__main__":
	filename = "program.oct"
	file_contents = read_file(filename)
	generated_code = compile_program(file_contents)
	if generated_code:
		# print(generated_code)
		print(f"Running Octanium version {ver}\n{filename}\n----------")
		ex.execute(generated_code)
