NONTERMS = [
    "<program>",
    "<statement>",
    "<declaration>",
    "<var_declaration>",
    "<const_declaration>",
    "<function_declare>",
    "<identifier>",
    "<begin>",
    "<letter>",
    "<name>",
    "<digit>",
    "<expression>",
    "<expression_tail>",  # New non-terminal for handling right recursion
    "<primary_expression>",  # New non-terminal for primary expressions
    "<operator>",
    "<singleOp>",
    "<logicOp>",
    "<number>",
    "<string>",
    "<text>",
    "<block>",
    "<call>",
    "<return>",
    "<print>",
    "<if-condition>",
    "<condition>",
    "<condition_tail>",  # New non-terminal for handling logical operations in conditions
    "<primary_condition>",  # New non-terminal for the core condition expression
    "<compOp>",
    "<loop>",
    "<keyword>",
    "<LBracket>",
    "<RBracket>",
    "<datatype>"
]


TERMS = [
    "(", ")", "*", "+", "-", "/", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", 
    ";", "<", "<=", "==", ">", ">=", "!=", "=", "A-Z", "a-z", "call", "do", 
    "else", "for", "if", "elif", "print", "return", "_", "{", "}", 
    "and", "or", "not", "\"", ">", "<", "<=", ">=", "<>", "int", "float", "string","++","--"
]


epsilon = "epsilon"
FIRST = {}

grammar = {
    "<program>": ["<statement>*"],  # A program consists of zero or more statements.
    
    "<statement>": [
        "<declaration>",
        "<call>",
        "<return>",
        "<print>",
        "<if-condition>",
        "<loop>",
        "<expression>"
    ],

    "<declaration>": ["<var_declaration>", "<const_declaration>", "<function_declare>"],

    "<var_declaration>": ["<datatype> <identifier> = <expression> ;"],
    "<const_declaration>": ["<datatype> <identifier> = <number> ;"],

    "<identifier>": ["<begin> <name>*"],

    "<begin>": ["_", "<letter>"],

    "<name>": ["<letter>", "<digit>"],
    "<digit>": ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"],
    "<letter>": ["a-z", "A-Z"],

    "<expression>": [
        "<primary_expression> <expression_tail>"
    ],

    "<expression_tail>": [
        "<operator> <primary_expression> <expression_tail>",  # recursive part
        "epsilon"  # epsilon (empty production)
    ],

    "<primary_expression>": [
        "<identifier>",
        "<number>",
        "<string>"
    ],

    "<operator>": ["+", "-", "*", "/"],
    "<singleOp>": ["++", "--"],

    "<logicOp>": ["and", "or", "not"],

    "<number>": ["<digit>", "digit. digit"],  # Support for integers and floats
    "<string>": ['" <text> "'],  # String representation
    "<text>": ['"<letter>+"'],  # Sequence of letters

    "<function_declare>": ["do <identifier> ((<datatype><identifier><separator>)*) <block>"],

    "<block>": ["{ <statement>* }"],

    "<call>": ["call <identifier> (<identifier>*) ;"],
    "<return>": ["return <expression> ;"],
    "<print>": ["print ( <expression> ) ;","print ( <call> );"],

    "<if-condition>": [
        "if <condition> <block>",
        "if <condition> <block> elif <condition> <block>",
        "if <condition> <block> else <block>"
    ],

    "<condition>": [
        "<primary_condition> <condition_tail>"
    ],

    "<condition_tail>": [
        "<logicOp> <primary_condition> <condition_tail>",  # recursive part for logical operations
        "<compOp> <primary_condition>",  # comparison part (non-recursive)
        "epsilon"  # epsilon (empty production)
    ],

    "<primary_condition>": [
        "<expression>"
    ],

    "<compOp>": [">", "<", "==", "<>", ">=", "<="],  # Comparison operators

    "<loop>": [
        "for (<var_declaration>; <condition>; <expression>) <block>"
    ],

    "<keyword>": ["do", "call", "return", "if", "elif", "else", "for", "break", "skip", "print"],

    "<LBracket>": ["("],
    "<RBracket>": [")", "}"],

    "<datatype>": ["int", "float", "string"],  # Added data types
}



def computeFirst(g):
    # Initialize FIRST sets
    for terminal in TERMS:
        FIRST[terminal] = {terminal}

    for non_terminal in NONTERMS:
        FIRST[non_terminal] = set()

    # Compute FIRST sets iteratively
    for _ in range(len(NONTERMS)):  # Repeat until convergence
        for non_terminal in g:
            for production in g[non_terminal]:
                # Compute FIRST for the production
                symbols = production.split()  # Split production into symbols
                first_of_production = computeFirstOfList(symbols)
                FIRST[non_terminal].update(first_of_production)

def computeFirstOfList(symbols):
    result = set()
    for symbol in symbols:
        if symbol in TERMS:  # Terminal
            result.add(symbol)
            break
        elif symbol in NONTERMS:  # Non-terminal
            result.update(FIRST[symbol] - {epsilon})
            if epsilon not in FIRST[symbol]:
                break
    else:
        result.add(epsilon)  # Add epsilon if all symbols can derive epsilon
    return result

# Compute FIRST sets for the grammar
computeFirst(grammar)

# Print the FIRST sets in a clear format
# print("FIRST Sets:")
# for non_terminal in NONTERMS:
#     print(f"FIRST({non_terminal}) = {{ {', '.join(FIRST[non_terminal])} }}")

"""do sum (x,y){
    return x + y
    }
    s = call sum(3, 4)
    print(s)"""