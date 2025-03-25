from lark import Lark

# grammar

def parse(program):
    grammar = """
    start: statements
    statements: statement (NEWLINE statement)*
    statement: assignment_stmt | display_stmt | constant_stmt | func_stmt | logic_stmt | run_stmt | call_compile
    assignment_stmt: "v" LSQUARE VARIABLE RSQUARE ASSIGN (NUMBER | VARIABLE | arithmetic_expr | concatenation | QUOTED_STRING | input_stmt | run_stmt)
    constant_stmt: "c" LSQUARE VARIABLE RSQUARE ASSIGN (NUMBER | QUOTED_STRING)
    input_stmt: "i" LSQUARE (expression) RSQUARE
    display_stmt: DISPLAY LSQUARE (QUOTED_STRING | VARIABLE | concatenation) RSQUARE
    expression: NUMBER | VARIABLE | arithmetic_expr | concatenation | QUOTED_STRING
    concatenation: expression (ADD expression)*
    arithmetic_expr: (NUMBER | VARIABLE) ADD (NUMBER | VARIABLE)
	    | (NUMBER | VARIABLE) SUBTRACT (NUMBER | VARIABLE)
	    | (NUMBER | VARIABLE) MULTIPLY (NUMBER | VARIABLE)
	    | (NUMBER | VARIABLE) DIVIDE (NUMBER | VARIABLE)
	    | (NUMBER | VARIABLE) POWER (NUMBER | VARIABLE)
	    | SQRT LSQUARE (NUMBER | VARIABLE) RSQUARE

		condition: VARIABLE [((G_THAN | EQUIVALENT | L_THAN | G_THAN_EQ | L_THAN_EQ) VARIABLE)*]
		loop_condition: VARIABLE | NUMBER | 
		logic_stmt: "l" LSQUARE "con" EQUIVALENT (LOGIC | LOOP) RSQUARE BIG_ARROW "c" LBRA (condition | loop_condition) RBRA LITTLE_ARROW LCURL logic_statements RCURL
		
		logic_statements: statements
		func_statements: [statements [(func_return_stmt)*]]
		func_stmt: "f" LSQUARE FUNC_NAME LBRA parameters RBRA LITTLE_ARROW LCURL func_statements RCURL RSQUARE
		func_return_stmt: "r" LSQUARE (VARIABLE | BOOLEAN) ("," VARIABLE)* RSQUARE
		run_stmt: "r" LSQUARE (function | class) RSQUARE
		parameters: [(VARIABLE | NUMBER | QUOTED_STRING) ("," (VARIABLE | NUMBER | QUOTED_STRING))*]
		
		class: FUNC_NAME LCURL RCURL
		function: FUNC_NAME LBRA parameters RBRA
		BOOLEAN: "True"
		ASSIGN: "=="
		EQUIVALENT: "="
		LSQUARE: "["
		RSQUARE: "]"
		LBRA: "("
		RBRA: ")"
		LCURL: "{"
		RCURL: "}"
		BIG_ARROW: "==>"
		LITTLE_ARROW: "-->"
		DISPLAY: "display"
		ADD: "+"
		SUBTRACT: "-"
		MULTIPLY: "*"
		DIVIDE: "/"
		POWER: "^"
		SQRT: "sqrt"
		INTEGER: "int"
		FLOAT: "float"
		LOGIC: "logic"
		LOOP: "loop"
		G_THAN: ">"
		L_THAN: "<"
		G_THAN_EQ: ">="
		L_THAN_EQ: "<="
		NO_EQ: "!="
		AND: "&&"
		OR: "||"
		NOT: "!-"
		FUNC_NAME: /[a-zA-Z_][a-zA-Z0-9_]*/
		COMMENT: "!!" /.*/
		call_compile: COMPILE LITTLE_ARROW OCTANIUM "/" LSQUARE MAIN RSQUARE DOT
		COMPILE: "!COMPILE"
		OCTANIUM: "octanium"
		MAIN: "main"
		DOT: "."
		TOP_CLASS: "!" /.*/
		%import common.CNAME -> VARIABLE
		%import common.NEWLINE
		%import common.WS
		%import common.LETTER
		%import common.DIGIT
		%import common.INT -> NUMBER
		%import common.ESCAPED_STRING -> QUOTED_STRING
		%ignore COMMENT
		%ignore WS
		"""

    parser = Lark(grammar, start="start")

    tree = parser.parse(program)
    return tree
