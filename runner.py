# runner.py
from basic import lexer  # replace 'your_lexer_file_name' with the actual file name of your lexer code

# Run function
def run(fname, text):
    Lexer = lexer(fname, text)
    tokens, error = Lexer.make_tokens()
    return tokens, error
