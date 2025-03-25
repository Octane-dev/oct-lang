from lark.tree import Tree
from lark.lexer import Token
import errors as er
import os

# checks to see if the code is an assignment or a display query (to be expanded later)

# creates f_string tree manually
def create_f_string_tree(prefix, variable, suffix):
	return Tree('f_string', [
		Token('ESCAPED_STRING_START', f'"{prefix}'),
		Token('VARIABLE', variable),
		Token('ESCAPED_STRING_END', f'{suffix}"')
	])

class SemanticAnalyzer:
	def __init__(self):
		self.symbol_table = {}
		self.code_array = []
		self.function_table = {}
		self.func_param_table = {}


	def analyze(self, tree, filename, source):
		statements = tree.children[0].children

		# Checks for compiler.
		if source == 'prog':
			first_statement = statements[0]
			if isinstance(first_statement, Tree):
				first_statement_type = first_statement.children[0].data
				if first_statement_type != "call_compile":
					raise SystemExit("Compile Error.\nNo compiler found.\nExiting program.")

		for line_number, statement in enumerate(statements, start=1):
			if isinstance(statement, Tree):
				statement_type = statement.children[0].data
				if statement_type == "assignment_stmt":
					self.analyze_assignment(statement.children[0],filename,line_number,source)
				elif statement_type == "display_stmt":
					self.analyze_display(statement.children[0],filename,line_number,source)
				elif statement_type == "constant_stmt":
					self.analyze_constant(statement.children[0],filename,line_number,source)
				elif statement_type == "logic_stmt":
					self.analyze_logic(statement.children[0],filename,line_number,source)
				elif statement_type == "func_stmt":
					self.analyze_function(statement.children[0],filename,line_number,source)
				elif statement_type == "run_stmt":
					self.analyze_run(statement.children[0],filename,line_number,source)
				elif statement_type == "func_return_stmt":
					self.analyze_return(statement.children[0],filename,line_number,source)

	
	def is_number(self,s):
		try:
				int(s)
				return True
		except ValueError:
				try:
						float(s)
						return True
				except ValueError:
						return False
	def convert_to_number(self,s):
		try:
				return int(s)
		except ValueError:
				return float(s)


	def analyze_logic(self,logic,filename,line_number,source):
		logic_value = False
		# get logic type (either 'logic' or 'loop')
		logic_type = logic.children[2]
		logic_condition = logic.children[6]
		logic_content = logic.children[10]

		if logic_type == "logic":
			# do logic stuff (=,>,< etc)
			if isinstance(logic_condition,Tree):
				logic_left = logic_condition.children[0]
				logic_op = logic_condition.children[1].type
				logic_right = logic_condition.children[2]
				if source in self.function_table:
					params = self.func_param_table[source]
					if logic_left not in params:
						print(f"Error, {logic_left} is not defined.")
						raise SystemExit(1)
					if logic_right not in params:
						print(f"Error, {logic_right} is not defined.")

				# get value from symbol table if is variable
				if logic_left.type == "VARIABLE":
					logic_left = self.symbol_table[logic_left]
				if logic_right.type == "VARIABLE":
					logic_right = self.symbol_table[logic_right]

				# check if number and change
				if self.is_number(logic_left):
					logic_left = self.convert_to_number(logic_left)
				if self.is_number(logic_right):
					logic_right = self.convert_to_number(logic_right)

				# check which operator and get value
				if logic_op == "EQUIVALENT":
					if logic_left == logic_right:
						logic_value = True
				elif logic_op == "G_THAN":
					if logic_left > logic_right:
						logic_value = True
				elif logic_op == "L_THAN":
					if logic_left < logic_right:
						logic_value = True
				elif logic_op == "G_THAN_EQ":
					if logic_left >= logic_right:
						logic_value = True
				elif logic_op == "L_THAN_EQ":
					if logic_left <= logic_right:
						logic_value = True
				else:
					print(f"Error. Unsupported operator.")
				#print(logic_left,logic_op,logic_right,logic_value)
			else:
				# check if value exists
				if logic_condition.children[0] in self.symbol_table:
					logic_value = True
		if logic_type == "loop":
			loop_end = logic_condition.children[0]
			if isinstance(loop_end, Token):
				# handle simple token (variable,number)
				loop_end_value = loop_end.value

				if loop_end.type == "VARIABLE":
					loop_end_value = self.symbol_table[loop_end_value]

				# check if number and change
				if self.is_number(loop_end_value):
					loop_end_value = self.convert_to_number(loop_end_value)

				# loop analyze
				for i in range(loop_end_value):
					self.analyze(logic_content,filename,"logic")
			else:
				# complex stuff, ie. len(variable) or whatever yes
				pass
		#print(logic_condition)
		if logic_value == True:
			self.analyze(logic_content,filename,"logic")


	def analyze_function(self,function,filename,line_number,source):
		# get function name, parameters and the inner statements
		func_name = function.children[1].value
		parameters = function.children[3].children
		if None in parameters:
			parameters = []
		function_content = function.children[7]
		# if nothing inside.
		if not function_content: 
			print(f"Warning. Function '{func_name}' is empty.")

		# add statements and params to tables.
		self.function_table[func_name] = function_content
		self.func_param_table[func_name] = parameters


	def run_function(self,func_name,call_params,filename,line_number,source):
		# get function tree and params from the table
		function_tree = self.function_table[func_name]
		function_params = self.func_param_table[func_name]
		# checks for valid number of params
		if len(function_params) != len(call_params):
			print(f"Error. Function '{func_name}' expected {len(function_params)} parameters but {len(call_params)} were given.\nExiting program.")
			raise SystemExit(1)
		# print(function_tree)


		# CHECK PARAMS (only variables passed in are useable.)
		# if function_params not in self.symbol_table 

		# analyzes all inner statements
		self.analyze(function_tree,filename,func_name)


	def analyze_run(self, function, filename, line_number,source):
		# get function name and parameters
		func_name = function.children[1].children[0].value
		parameters = function.children[1].children[2].children
		# check that function exists
		# parameters = [None]
		# extra step for visual studio as no params = [None] not []
		if None in parameters:
			parameters = []
		if func_name in self.function_table:
			for parameter in parameters:
				if parameter not in self.symbol_table:
					print(f"Error. Parameter '{parameter}' is not defined at line {line_number}.\nExiting program.")
					raise SystemExit(1)
			# run function
			#print(parameters)
			self.run_function(func_name, parameters, filename, line_number,source)
		else:
			print(f"Error. No such function '{func_name}'.\nExiting program.")
			raise SystemExit(1)



	# def check_if_constant(self,assignment,filename,line_number):
		# will check to see if a previous constant is overwritten (if so, error it)

	def evaluate_input(self,value):
		# if func_value == "int" -- check for int,str,float.

		# gets filler text
		filler_text = value.children[1].children[0]

		# checks and removes quotation makrs
		if '"' not in filler_text:
			filler_text = self.symbol_table[filler_text]

		if filler_text.startswith('"') and filler_text.endswith('"'):
			filler_text = filler_text[1:-1]

		# check for variable, f-string or quote
		if "{{" in filler_text and "}}" in filler_text:
			# Replace variable placeholders with their values
			message = self.replace_placeholders(filler_text)
			final_value = input(message)
		else:
			final_value = input(filler_text)

		# the input

		return f'"{final_value}"'


	def analyze_constant(self, assignment,filename,line_number,source):
		# gets the variable name and the expression
		variable_name = assignment.children[1]
		value = assignment.children[4]

		# checks to make sure value is a token
		if isinstance(value, Token):
			# defines value as the value of value
			value = value.value

			# appends to the symbol table and the code array
			self.symbol_table[variable_name] = value
			self.code_array.append(f"{variable_name} = {value}")
		else:
			# if structure is a tree (as constants only work as a number or text.)
			raise SyntaxError(f"Invalid syntax of '{variable_name}' at line {line_number} in {filename}.")

	def analyze_return(self,ret,filename,line_number,source):
		print("B",ret)

	def analyze_assignment(self, assignment, filename, line_number,source):
		# defines variable value and variable name
		value = assignment.children[4]
		variable_name = assignment.children[1]
		#print(value, variable_name)
		# --------------- needs to skip if assignment is inside func. ---------------
		# if source in self.function_table:
		# 	params = self.func_param_table[source]
		# 	if variable_name not in params:
		# 			print(f"Error, {value} is not defined.")
		# 			raise SystemExit(1)

			# look for params, if variable not in then error.
		# Check if the value is an expression tree
		if isinstance(value, Tree):
			# print(expr)
			# Handle the case where the value is an expression tree
			if value.data == "arithmetic_expr":
				value = self.evaluate_arithmetic(value)
			elif value.data == "concatenation":
				value = self.evaluate_concatenation(value)
			elif value.data == "input_stmt":
				value = self.evaluate_input(value)
			elif value.data == "run_stmt":
				value = '0'
				#value = self.evaluate_function(value)
			# value = self.evaluate_arithmetic(value)
			#return
		else:
			# Handle the case where the value is a simple token
			value = value.value

		# Store the value in the symbol table under the variable name
		self.symbol_table[variable_name] = value
		self.code_array.append(f"{variable_name} = {value}")


	def replace_placeholders(self, raw_string):
		parts = raw_string.split("{{")
		formatted_parts = [parts[0]]
		for part in parts[1:]:
			variable, suffix = part.split("}}", 1)
			if variable in self.symbol_table:
				value = str(self.symbol_table[variable])
				# Check if the value is a string literal and remove surrounding quotation marks
				if value.startswith('"') and value.endswith('"'):
					value = value[1:-1]  # Remove the first and last characters (quotation marks)
				formatted_parts.append(value)
			else:
				print(f"Error: Variable '{variable}' is not defined.")
				raise SyntaxError("Invalid syntax", 10, "example.oct")
				return None
			formatted_parts.append(suffix)
		return ''.join(formatted_parts)



	def analyze_display(self, display, filename, line_number,source):
		content = display.children[2]
		if isinstance(content, Token): # Handle f-string or variable
			raw_string = content.value
			if "{{" in raw_string and "}}" in raw_string:
				# Replace variable placeholders with their values
				message = self.replace_placeholders(raw_string)
				self.code_array.append(f'print({message})')
			else:
				if content.type == 'QUOTED_STRING':
					# If it's a quoted string, remove the surrounding quotes
					message = raw_string[1:-1]
				elif content.type == 'VARIABLE':
					variable_name = content.value
					if source in self.function_table:
						params = self.func_param_table[source]
						if variable_name not in params:
								print(f"Error, {variable_name} is not defined.")
								raise SystemExit(1)
					if variable_name not in self.symbol_table:
						raise NameError(f"Variable '{variable_name}' is not defined.")
					if self.symbol_table[variable_name].startswith('"') and self.symbol_table[variable_name].endswith('"'):
						self.symbol_table[variable_name] = self.symbol_table[variable_name][1:-1]
					# Use the variable value from the symbol table
					message = self.symbol_table[variable_name]
				else:
					raise NameError(f"Invalid content type '{content.type}'")
				self.code_array.append(f'print("{message}")')

		else:
			raise NameError(f"Variable '{content}' is not defined in file '{filename}' at line {line_number}.")
			return


		# Generate the print statement with the formatted message


	def analyze_f_string(self, f_string_tree):
		pre_text = f_string_tree.children[0].value[1:]  # Remove the leading quote
		variable_name = f_string_tree.children[1].value
		post_text = f_string_tree.children[2].value[:-1]  # Remove the trailing quote
		if variable_name in self.symbol_table:
			variable_value = self.symbol_table[variable_name]
			message = f"{pre_text}{variable_value}{post_text}"
			print(f"Displaying message: {message}")
			self.code_array.append(f'print("{message}")')
		else:
			print(f"Error: Variable '{variable_name}' is not defined.")

	def parse_f_string(self, raw_string):
		# Assuming f-string format: "prefix{{variable}}suffix"
		parts = raw_string.split("{{")
		prefix = parts[0][1:]  # Remove the leading quote
		variable_and_suffix = parts[1].split("}}")
		variable = variable_and_suffix[0]
		suffix = variable_and_suffix[1][:-1]  # Remove the trailing quote
		return prefix, variable, suffix


	def analyze_expression(self, expr):
		if isinstance(expr, Tree):
			if expr.data == "arithmetic_expr":
				return self.evaluate_arithmetic(expr)
			elif expr.data == "concatenation":
				return self.evaluate_concatenation(expr)
		elif isinstance(expr, Token):
			if expr.type == "NUMBER":
				return int(expr.value)
			elif expr.type == "VARIABLE":
				variable_name = expr.value
				if variable_name in self.symbol_table:
					return self.symbol_table[variable_name]
				else:
					print(f"Error: Variable '{variable_name}' is not defined.")
					return None
			elif expr.type == "QUOTED_STRING":
				return expr.value[1:-1]  # Remove the surrounding quotes
		return None


	def evaluate_arithmetic(self, expr):
		operator = expr.children[1].type
		operand1 = self.analyze_expression(expr.children[0])
		operand2 = self.analyze_expression(expr.children[2])

		if expr.children[0].type == "VARIABLE":
			vari_name = expr.children[0].value
			vari_value = self.symbol_table[vari_name]
			operand1 = vari_value
			if self.is_number(operand1):
				operand1 = self.convert_to_number(operand1)

		if expr.children[2].type == "VARIABLE":
			vari_name = expr.children[0].value
			vari_value = self.symbol_table[vari_name]
			operand2 = vari_value
			if self.is_number(operand2):
				operand2 = self.convert_to_number(operand2)


		#print("Operand 1:", operand1)
		#print("Operator:", operator)
		#print("Operand 2:", operand2)

		# Ensure that the expression has enough children
		if len(expr.children) < 3:
			# Handle error
			print("Error: Arithmetic expression is incomplete.")
			return None

		# Check if any of the components are None
		if operand1 is None or operand2 is None or operator is None:
			# Handle error
			print("Error: Unable to evaluate operands or operator.")
			return None

		# Perform arithmetic operation based on the operator
		if operator == 'ADD':
			return f'{operand1 + operand2}'
		elif operator == 'SUBTRACT':
			return f'{operand1 - operand2}'
		elif operator == 'MULTIPLY':
			return f'{operand1 * operand2}'
		elif operator == 'DIVIDE':
			try:
				return f'{operand1 / operand2}'
			except ZeroDivisionError as e:
				print(f"Error: {e}.\nExiting program.")
				raise SystemExit(1)

		elif operator == "POWER":
			return f'{operand1 ** operand2}'
		# elif operator == "SQRT":
			# return f'{sqrt(operand1)}'
		else:
			# Handle error: Unsupported operator
			print("Error: Unsupported operator.")
			return None


	def evaluate_concatenation(self, expr):
		# left = self.analyze_expression(expr.children[0].children)
		# right = self.analyze_expression(expr.children[2].children)
		#print(expr.children[2].children[0])
		left = expr.children[0].children[0]
		right = expr.children[2].children[0]
		if left.startswith('"') and left.endswith('"'):
			left = left[1:-1]  # Remove the first and last characters (quotation marks)
		if right.startswith('"') and right.endswith('"'):
			right = right[1:-1]  # Remove the first and last characters (quotation marks)
		# print(self.analyze_expression(expr.children))

		if left is not None and right is not None:
			#print(str(left)+str(right))
			return f'"{str(left) + str(right)}"'
		return None



	def return_values(self):
		return self.code_array

#class Token:
#    def __init__(self, token_type, value):
#        self.type = token_type
#        self.value = value
