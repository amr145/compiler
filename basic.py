# Token types for data types
INT = "<number>"
FLOAT = "<number>"
STRING = "<string>"
Type = "<datatype>"
PLUS = "<operator>"
MINUS = "<operator>"
MUL = "<operator>"
DIV = "<operator>"
LP = "<LBracket>"
RP = "<RBracket>"
block = "<block>"
kword = "<keyword>"
id = "<identifier>"
logicOp = "<logicOp>"
compOp = "<compOp>"
separator = "<separator>"
assign = "<assign>"
increament = "<singleOp>"
decreament = "<singleOp>"

# Constants (literals)
Digits = '0123456789'
Keywords = ["do", "call", "return", "if", "elif", "else", "for", "break", "skip", "print"]
logical_OPs = ["and", "or", "not"]
comparison = ['>', '<', "==", "<>", ">=", "<="]
data_types = ["int", "float", "string", "bool"]  # Added supported data types

# Errors
class Error:
    def __init__(self, pos_start, pos_end, error_name, details):
        self.pos_start = pos_start
        self.pos_end = pos_end
        self.error_name = error_name
        self.details = details
        
    def as_string(self):
        result = f'{self.error_name}:  {self.details}'
        if self.pos_start:
            result += f' File {self.pos_start.fname}, line {self.pos_start.line + 1}, column {self.pos_start.col + 1}'
        return result

class IllegalCharError(Error):
    def __init__(self, pos_start, pos_end, details):
        super().__init__(pos_start, pos_end, "Illegal Character", details)

class UnclosedStringError(Error):
    def __init__(self, pos_start, pos_end, details):
        super().__init__(pos_start, pos_end, "Unclosed String", details)

# Position of line
class Position:
    def __init__(self, index, line, col, fname, ftxt):
        self.index = index
        self.line = line
        self.col = col
        self.fname = fname
        self.ftxt = ftxt
    def advance(self, current_char):
        self.index += 1
        self.col += 1
        
        if current_char == '\n':
            self.line += 1
            self.col = 0
        
        return self

    def copy(self):
        return Position(self.index, self.line, self.col, self.fname, self.ftxt)
        
# Get tokens
class Token:
    def __init__(self, type, value=None):
        self.type = type
        self.value = value
    
    def show(self):
        if self.value: 
            return (self.type, self.value)
        return (self.type,)

# Lexer
class lexer:
    def __init__(self, fname, text):
        self.fname = fname
        self.text = text
        self.pos = Position(-1, 0, -1, fname, text)
        self.current_char = None
        self.advance()
        
    def advance(self):
        self.pos.advance(self.current_char)
        self.current_char = self.text[self.pos.index] if self.pos.index < len(self.text) else None  
    
    def make_tokens(self):
        tokens = []
        
        while self.current_char is not None:
            if self.current_char in ' \t':  # Ignore spaces and tabs
                self.advance()
                
            elif self.current_char == '\n':  # Skip newlines
                self.advance()
                
            elif self.current_char == '/' and self.peek_next() == '/':  # Ignore single-line comments
                self.advance()
                self.advance()  # Skip the first two slashes
                while self.current_char is not None and self.current_char != '\n':  # Skip until end of line
                    self.advance()
                
            elif self.current_char == '/' and self.peek_next() == '*':  # Ignore multi-line comments
                self.advance()
                self.advance()  # Skip the first two characters of '/*'
                while self.current_char is not None and not (self.current_char == '*' and self.peek_next() == '/'):  # Skip until '*/'
                    self.advance()
                self.advance()  # Skip the '*' character
                self.advance()  # Skip the '/' character
            
            elif self.current_char in Digits:  # Numbers
                tokens.append(self.make_number().show())
            
            elif self.current_char == '+':
                self.advance()
                if self.current_char == '+':    
                    tokens.append(Token(increament, "++").show())
                    self.advance()
                else:
                    tokens.append(Token(PLUS, "+").show())
            
            elif self.current_char == '-':
                self.advance()
                if self.current_char == '-':    
                    tokens.append(Token(decreament, "--").show())
                    self.advance()
                else:
                    tokens.append(Token(MINUS, "-").show())
            
            elif self.current_char == '*':
                tokens.append(Token(MUL, "*").show())
                self.advance()
            
            elif self.current_char == '/':
                tokens.append(Token(DIV, "/").show())
                self.advance()
                
            elif self.current_char == ',':
                tokens.append(Token(separator, ',').show())
                self.advance()
                
            elif self.current_char in '[(':
                tokens.append(Token(LP, self.current_char).show())
                self.advance()
                
            elif self.current_char in ')]}':
                tokens.append(Token(RP, self.current_char).show())
                self.advance()
                
            elif self.current_char == '{':
                tokens.append(Token(block).show())
                self.advance()
                
            elif self.current_char == '"' or self.current_char == '\'':
                result = self.make_string()
                if isinstance(result, Error):
                    return [], result
                tokens.append(result.show())
            
            elif self.current_char.isalpha() or self.current_char == '_':
                tokens.append(self.check_keyword().show())
            
            elif self.current_char in comparison or self.current_char == '=':
                op = ""
                while self.current_char not in Digits and not self.current_char.isalpha() and self.current_char != ' ':
                    op += self.current_char
                    self.advance()
                if op == "=":
                    tokens.append(Token(assign, op).show())
                else:
                    tokens.append(Token(compOp, op).show())
            
            elif self.current_char in data_types:  # Handling data types
                dtype = self.make_data_type()
                tokens.append(Token(dtype).show())
                self.advance()
                
            elif self.current_char == ';':
                self.advance()
                
            else:
                pos_start = self.pos.copy()
                char = self.current_char
                self.advance()
                return [], IllegalCharError(pos_start, self.pos, f"'{char}'")
                
        return tokens, None

    
    def peek_next(self):
        """Returns the next character without advancing."""
        if self.pos.index + 1 < len(self.text):
            return self.text[self.pos.index + 1]
        return None

    def make_number(self):
        num_str = ''
        dot_count = 0
        
        while self.current_char is not None and self.current_char in Digits + '.':
            if self.current_char == '.':
                if dot_count == 1:
                    break
                dot_count += 1
                num_str += '.'
            else:
                num_str += self.current_char
        
            self.advance()
            
        if dot_count == 0:
            return Token(INT, int(num_str))
        else:
            return Token(FLOAT, float(num_str))
        
    def make_string(self):
        quote_char = self.current_char  # Track starting quote
        pos_start = self.pos.copy()
        self.advance()
        
        text = ''
        while self.current_char is not None and self.current_char != quote_char:
            text += self.current_char
            self.advance()
        
        # Handle unclosed string
        if self.current_char != quote_char:
            return UnclosedStringError(pos_start, self.pos, "String not closed")

        self.advance()  # Move past the closing quote
        return Token(STRING, text)
    
    def check_keyword(self):
        word = ""
        while self.current_char is not None and self.current_char not in ' */()[]!@#$%^&*-+=;.\t,':  # Correct character check for word boundaries
            word += self.current_char
            self.advance()
        if word in Keywords:
            return Token(kword, word)
        elif word in logical_OPs:
            return Token(logicOp, word)
        elif word in data_types:
            return Token(Type, word)
        else:
            return Token(id, word)
    
        # Now we return the correct token based on the data type string
        
        
