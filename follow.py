# Define the grammar as a dictionary
GRAMMAR = {
    "<program>": ["<statement>*"],
    "<statement>": ["<declaration>", "<call>", "<return>", "<print>", "<if-condition>", "<loop>", "<expression>"],
    "<declaration>": ["<var_declaration>", "<const_declaration>", "<function_declare>"],
    "<var_declaration>": ["<datatype> <identifier> = <expression> ;"],
    "<const_declaration>": ["<datatype> <identifier> = <number> ;"],
    "<identifier>": ["<begin> <name>*"],
    "<begin>": ["_", "<letter>"],
    "<name>": ["<letter>", "<digit>"],
    "<digit>": ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"],
    "<letter>": ["a-z", "A-Z"],
    "<expression>": ["<primary_expression> <expression_tail>"],
    "<expression_tail>": ["<operator> <primary_expression> <expression_tail>", "epsilon"],
    "<primary_expression>": ["<identifier>", "<number>", "<string>"],
    "<operator>": ["+", "-", "*", "/"],
    "<singleOp>": ["++", "--"],
    "<logicOp>": ["and", "or", "not"],
    "<number>": ["<digit>", "digit. digit"],
    "<string>": ['" <text> "'],
    "<text>": ['"<letter>+"'],
    "<function_declare>": ["do <identifier> (<datatype> <identifier>*) ;"],
    "<call>": ["call <identifier> (<identifier>*) ;"],
    "<return>": ["return <expression> ;"],
    "<print>": ["print ( <expression> ) ;"],
    "<if-condition>": [
        "if <condition> <statement>*",
        "if <condition> <statement>* elif <condition> <statement>*",
        "if <condition> <statement>* else <statement>*"
    ],
    "<condition>": ["<primary_condition> <condition_tail>"],
    "<condition_tail>": ["<logicOp> <primary_condition> <condition_tail>", "<compOp> <primary_condition>", "epsilon"],
    "<primary_condition>": ["<expression>"],
    "<compOp>": [">", "<", "==", "<>", ">=", "<="],
    "<loop>": ["for (<var_declaration>; <condition>; <expression>) <statement>*"],
    "<keyword>": ["do", "call", "return", "if", "elif", "else", "for", "break", "skip", "print"],
    "<LBracket>": ["("],
    "<RBracket>": [")", "}"],
    "<datatype>": ["int", "float", "string"],
    "<assign>" : ["="],
    "<separator>" : [',']
}

# Initialize NONTERMS, TERMS, epsilon, and FOLLOW sets
NONTERMS = [
    "<program>", "<statement>", "<declaration>", "<var_declaration>", "<const_declaration>", "<function_declare>", 
    "<identifier>", "<begin>", "<letter>", "<name>", "<digit>", "<expression>", "<expression_tail>", 
    "<primary_expression>", "<operator>", "<singleOp>", "<logicOp>", "<number>", "<string>", "<text>", 
    "<call>", "<return>", "<print>", "<if-condition>", "<condition>", "<condition_tail>", "<primary_condition>", 
    "<compOp>", "<loop>", "<keyword>", "<LBracket>", "<RBracket>", "<datatype>", "<assign>", "<separator>"
]

TERMS = [
    "(", ")", "*", "+", "-", "/", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", 
    ";", "<", "<=", "==", ">", ">=", "!=", "=", "A-Z", "a-z", "call", "do", 
    "else", "for", "if", "elif", "print", "return", "_", "{", "}", 
    "and", "or", "not", "\"", ">", "<", "<=", ">=", "<>", "int", "float", "string", "++", "--"
]

epsilon = "epsilon"

# Initialize FOLLOW sets
FOLLOW = {nt: set() for nt in NONTERMS}
FOLLOW["<program>"].add("$")  # Start symbol



# Helper functions
def compute_first(symbol):
    """Computes the FIRST set of a given symbol."""
    if symbol in TERMS:
        return {symbol}
    if symbol == epsilon:
        return {epsilon}
    
    first = set()
    for production in GRAMMAR.get(symbol, []):
        for token in production.split():
            token_first = compute_first(token)
            first.update(token_first - {epsilon})
            if epsilon not in token_first:
                break
        else:
            first.add(epsilon)
    return first
def compute_follow():
    """Computes the FOLLOW sets for all non-terminals."""
    updated = True
    while updated:
        updated = False
        for lhs, productions in GRAMMAR.items():
            for production in productions:
                tokens = production.split()
                for i, token in enumerate(tokens):
                    if token in NONTERMS:
                        follow_before = FOLLOW[token].copy()
                        # Add FIRST of the next token (if any)
                        for j in range(i + 1, len(tokens)):
                            next_first = compute_first(tokens[j])
                            FOLLOW[token].update(next_first - {epsilon})
                            if epsilon not in next_first:
                                break
                        else:
                            # Add FOLLOW of LHS if all remaining tokens derive epsilon
                            FOLLOW[token].update(FOLLOW[lhs])
                        if FOLLOW[token] != follow_before:
                            updated = True

# Manually add FOLLOW sets
FOLLOW["<keyword>"].add("(")
FOLLOW["<keyword>"].add("{")
FOLLOW["<keyword>"].add("call")
FOLLOW["<keyword>"].add("do")
FOLLOW["<keyword>"].add("return")
FOLLOW["<keyword>"].add("if")
FOLLOW["<keyword>"].add("elif")
FOLLOW["<keyword>"].add("else")
FOLLOW["<keyword>"].add("for")
FOLLOW["<keyword>"].add("break")
FOLLOW["<keyword>"].add("skip")
FOLLOW["<keyword>"].add("print")

FOLLOW["<singleOp>"].add(";")
FOLLOW["<singleOp>"].add(")")

FOLLOW["<LBracket>"].add(")")
FOLLOW["<LBracket>"].add("int")
FOLLOW["<LBracket>"].add("float")
FOLLOW["<LBracket>"].add("string")
FOLLOW["<separator>"].add("A-Z")
FOLLOW["<separator>"].add("a-z")
FOLLOW["<separator>"].add("_")
FOLLOW["<LBracket>"].add("\"")
FOLLOW["<assign>"].add(";")  # After an assignment, an expression or statement terminator may follow
# Compute FOLLOW sets
FOLLOW["<RBracket>"].add(";")
compute_follow()

# Print FOLLOW sets
# for nt in NONTERMS:
#     print(f"FOLLOW({nt}) = {FOLLOW[nt]}")

