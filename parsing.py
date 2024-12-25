import re

class ParseError(Exception):
    pass

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current = 0
        self.ids = []
    
    def peek(self):
        return self.tokens[self.current] if self.current < len(self.tokens) else None
    
    def advance(self):
        self.current += 1
        
    def retreat(self):
        self.current -= 1
    
    def match(self, *expected):
        token = self.peek()           
        if token in expected:
            self.current += 1
            return token
        elif token == "=" or token == ">" or token == "<":
            self.advance()
            next = self.peek()
            if next == "=":
                print("pp")
                return token + next
            else:
                self.retreat()
        return None
    
    def parse_program(self):
        return ["<program>", self.parse_statements()]
    
    def parse_statements(self):
        statements = []
        while self.peek() is not None:
            statements.append(self.parse_statement())
        return ["<statement>*", statements]
    
    def parse_statement(self):
        token = self.peek()
        
        if token in {"int", "float", "string"}:  # Declaration
            return self.parse_declaration()
        elif token == "if":  # If condition
            return self.parse_if_condition()
        elif token == "print":  # Print statement
            return self.parse_print()
        elif token == "for":
            return self.parse_for()
        elif token == "{":  # Handle block-like statements
            return self.parse_block()  # Parse the block of code after '{' until '}'
        elif token in self.ids:
            return self.parse_assignment()
        elif token == "do":
            return self.parse_do()
        elif token == "return":
            return self.parse_return()
        elif token == "call":
            return self.parse_call()
        else:
            raise ParseError(f"Unexpected input: {token}")

    def parse_declaration(self):
        datatype = self.match("int", "float", "string")
        identifier = self.parse_identifier()
        self.match("=")
        expression = self.parse_expression()  # Call to parse_expression
        self.match(";")
        return ["<declaration>", [
            "<var_declaration>", [
                "<datatype>", [datatype],
                "<identifier>", identifier,
                "=", 
                "<expression>", expression,
                ";"
            ]
        ]]
    
    def parse_assignment(self):
        identifier = self.parse_identifier()
        self.match("=")
        expression = self.parse_expression()  # Call to parse_expression
        self.match(";")
        return ["<assignment>", [
            "<var_assignment>", [
                "<identifier>", identifier,
                "=", 
                "<expression>", expression,
                ";"
            ]
        ]]
    
    def parse_identifier(self):
        token = self.peek()
        if token not in self.ids:
            self.ids.append(token)
        # Use a regex pattern to validate if the token is a valid identifier
        if re.match(r'^[_a-zA-Z][_a-zA-Z0-9]*$', token):
            self.current += 1  # Move to the next token
            return ["<identifier>", ["<begin>", [token[0]], "<name>*", [token[1:]]]]
        raise ParseError(f"Invalid identifier: {token}")
    
    def parse_expression(self):
        # First, parse the primary expression (identifier, number, string)
        primary_expr = self.parse_primary_expression()

        # Now, handle the tail of the expression (operators, logical operations)
        return self.parse_expression_tail(primary_expr)

    def parse_primary_expression(self):
        token = self.peek()
        current_number = ""

        # Build the number character by character
        while token and (token.isdigit() or token == "."):
            if token == ".":
                if "." in current_number:  # Prevent multiple dots in the same number
                    raise ParseError("Invalid number format with multiple decimal points.")
            current_number += token
            self.advance()  # Move to the next character
            token = self.peek()  # Update the current character

        if current_number:
            # Determine if it's a floating-point or integer number
            if "." in current_number:
                integer_part, fractional_part = current_number.split(".")
                return [
                    "<primary_expression>",
                    [
                        "<number>",
                        ["<integer_part>", [integer_part]],
                        ["<dot>", ["."]],
                        ["<fractional_part>", [fractional_part]],
                    ],
                ]
            else:
                return [
                    "<primary_expression>",
                    ["<number>", ["<digit>", current_number]],
                ]

        # Handle string (e.g., "hello")
        elif token.startswith('"') and token.endswith('"'):
            text = self.match(token)
            return ["<primary_expression>", ["<string>", ["<text>", text.strip('"')]]]

        # Handle identifier (e.g., x)
        elif re.match(r"[a-zA-Z_]", token):
            identifier = self.parse_identifier()

            # Check if it's followed by a single operator (e.g., ++, --)
            next_token = self.peek()
            self.advance()
            whole = next_token + self.peek()
            if whole in ["++", "--"]:
                single_op = self.match(next_token)
                return ["<primary_expression>", ["<identifier>", identifier, "<singleOp>", [whole]]]
            else:
                self.retreat()
            return ["<primary_expression>", identifier]

        else:
            raise ParseError(f"Invalid primary expression: {token}")

    def parse_expression_tail(self, left_expr):
        token = self.peek()

        # Handle arithmetic operations (e.g., x + 2)
        if token in ["+", "-", "*", "/"]:
            operator = self.match(token)
            right_expr = self.parse_primary_expression()  # Parse the right side of the operation
            # Recursively process further arithmetic operations
            return self.parse_expression_tail(["<expression>", [left_expr, "<operator>", operator, right_expr]])

        # Handle logical operations (e.g., "and", "or")
        elif token in ["and", "or"]:
            logic_op = self.match(token)
            right_expr = self.parse_expression()  # Parse the second expression
            return ["<expression>", [left_expr, "<logicOp>", logic_op, right_expr]]

        # No further expressions (base case)
        else:
            return left_expr
    
    def parse_if_condition(self):
        self.match("if")
        condition = self.parse_condition()
        block = self.parse_block()
        if self.match("else"):
            else_block = self.parse_block()
            return ["<if-condition>", ["if", condition, block, "else", else_block]]
        return ["<if-condition>", ["if", condition, block]]
    
    def parse_condition(self):
        left = self.parse_expression()  # Expression on the left side of comparison
        comp_op = self.match(">", "<", "==", "<>", ">=", "<=")
        if not comp_op:
            raise ParseError("Invalid condition operator.")
        right = self.parse_expression()  # Expression on the right side of comparison
        return ["<condition>", [left, "<compOp>", [comp_op], right]]
    
    def parse_for(self):
        self.match("for")  # Match the 'for' keyword

        # Expect '(' after 'for'
        self.match("(")

        # Parse the variable declaration
        var_declaration = self.parse_declaration()

        # Expect ';' after the variable declaration
        self.match(",")

        # Parse the condition part of the loop
        condition = self.parse_condition()

        # Expect ';' after the condition
        self.match(",")

        # Parse the expression part of the loop
        expression = self.parse_expression()

        # Expect ')' after the expression
        self.match(")")

        # Parse the block of statements inside the loop
        block = self.parse_block()

        return ["<loop>", ["for", var_declaration, condition, expression, block]]
    
    def parse_do(self):
        """Parses a 'do' statement."""
        self.match("do")  # Match the 'do' keyword
        identifier = self.parse_identifier()  # Parse the function identifier
        
        # Expect opening parenthesis for parameters
        self.match("(")
        
        parameters = []
        # Parse parameters (datatype identifier separator)*, stop at closing parenthesis
        while self.peek() not in [")", None]:
            datatype = self.match("int", "float", "string")  # Match datatype (int, float, string)
            identifier_param = self.parse_identifier()  # Parse the identifier (parameter name)
            parameters.append(["<parameter>", [datatype, identifier_param]])

            # If there's a separator (like a comma), consume it
            if self.peek() == ",":
                self.match(",")
        
        # Expect closing parenthesis after parameters
        self.match(")")
        
        # Parse the block of statements
        block = self.parse_block()
        
        return ["<function_declare>", [
            "do", 
            identifier, 
            "<parameters>", parameters, 
            "<block>", block
        ]]

    # Other methods...

    def parse_return(self):
        """Parses a 'return' statement."""
        self.match("return")  # Match the 'return' keyword
        expression = self.parse_expression()  # Parse the expression after 'return'
        self.match(";")  # Expect a semicolon after the expression
        return ["<return>", ["return", expression, ";"]]

    def parse_call(self):
        self.match("call")  # Match the "call" keyword
        function_name = self.parse_identifier()  # Parse the function name (an <identifier>)
        self.match("(")  # Match the opening parenthesis

        # Parse zero or more <identifier>s separated by commas
        arguments = []
        while self.peek() not in [")",None]:
            identifier_param = self.parse_identifier()  # Parse the identifier (parameter name)
            arguments.append(["<argument>", [identifier_param]])

            # If there's a separator (like a comma), consume it
            if self.peek() == ",":
                self.match(",")
        
        # Expect closing parenthesis after parameters
        self.match(")")

        return ["<call>", ["call", function_name, "(", arguments, ")", ";"]]


    def parse_block(self):
        # Start of block: '{'
        self.match("{")
        
        statements = []
        while True:
            token = self.peek()
            
            # End of block: '}' on a new line (must be on a separate line, not inline)
            if token == "}":  # Assuming `peek_next` checks next token or new line
                self.match("}")  # Accept the closing brace
                break
            elif token == None:
                raise ParseError("Unbalanced Code: missing }")
            # Parse individual statements
            statements.append(self.parse_statement())
            
        return ["<block>", statements]


    def parse_print(self):
        self.match("print")
        self.match("(")

        # Check for <call> or <expression>
        if self.peek() == "call":  # Assuming `current_token` points to the current token
            call = self.parse_call()  # Parse the <call>
            content = ["<call>", call]
        else:
            expression = self.parse_expression()  # Parse the <expression>
            content = ["<expression>", expression]

        if self.match(")") == None:
            raise ParseError("Unbalanced Code: missing )")
        self.match(";")
        return ["<print>", ["print", "(", content, ")", ";"]]


def tokenize(code):
    tokens = re.findall(r'[a-zA-Z_][a-zA-Z0-9_]*|[{}();=<>]|"[^"]*"|\d+|\S', code)
    return tokens

def pretty_print(tree, level=0, prefix="└──"):
    """Pretty prints the parse tree with indentation and tree-like symbols."""
    if isinstance(tree, list):
        # If the tree is a list, it represents a branch. We need to handle it differently.
        result = ""
        for idx, item in enumerate(tree):
            # Use '├──' for intermediate branches and '└──' for the last branch.
            child_prefix = "├──" if idx < len(tree) - 1 else "└──"
            result += pretty_print(item, level + 1, child_prefix)
        return result
    else:
        # For leaf nodes (strings or tokens), print with indentation and arrow for values.
        if isinstance(tree, str) and "->" not in tree:
            return f"{'│   ' * level}{prefix} {tree}\n"
        elif isinstance(tree, str):
            # Handle the token with an arrow (e.g., "-> 'x'")
            return f"{'│   ' * level}{prefix} {tree}\n"
        else:
            return f"{'│   ' * level}{prefix} {tree}\n"

if __name__ == "__main__":
    with open("code.txt", "r") as f:
        code = f.read()
    tokens = tokenize(code)
    try:
        parser = Parser(tokens)
        parse_tree = parser.parse_program()  # Call to parse_program to start parsing
        print("Parse Tree:")
        print(pretty_print(parse_tree))  # Use pretty_print for formatted output
    except ParseError as e:
        print(f"Syntax error: '{e}'")
