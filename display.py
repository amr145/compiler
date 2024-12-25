import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import runner
import First2
import follow
import parsing  # Import the parsing module
from Table import SymbolTable
import Table

mytokens = []

def count_unique_tokens(tokens):
    unique_token_types = set()
    for token in tokens:
        unique_token_types.add(token[0])
    return len(unique_token_types)

def browse_input_file(entry):
    file_path = filedialog.askopenfilename(title="Select Input File", filetypes=[("Text Files", "*.txt")])
    entry.delete(0, tk.END)
    entry.insert(0, file_path)

def display_file_content(entry, display_text_widget):
    try:
        file_path = entry.get()
        with open(file_path, 'r') as file:
            content = file.read()
        display_text_widget.delete('1.0', tk.END)
        display_text_widget.insert(tk.END, content)
    except FileNotFoundError:
        messagebox.showerror("Error", "File not found. Please select a valid file.")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

def display_tokens(input_file, output_text_widget):
    try:
        with open(input_file, 'r') as file:
            text = file.read()
        tokens, error = runner.run('<code.txt>', text)
        
        if error:
            output_text_widget.delete('1.0', tk.END)
            output_text_widget.insert(tk.END, error.as_string())
            return
        
        if not tokens:
            output_text_widget.delete('1.0', tk.END)
            output_text_widget.insert(tk.END, "No tokens generated.\n")
            return

        output_text_widget.delete('1.0', tk.END)
        output_text_widget.insert(tk.END, "Tokens:\n")
        for token in tokens:
            output_text_widget.insert(tk.END, f"{token}\n")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

def display_first_sets(input_file, output_text_widget):
    try:
        with open(input_file, 'r') as file:
            text = file.read()
        tokens, _ = runner.run('<code.txt>', text)
        printed_token_types = set()
        output_text_widget.delete('1.0', tk.END)
        output_text_widget.insert(tk.END, "First Sets:\n")
        for token in tokens:
            token_type = token[0]
            if token_type not in printed_token_types:
                printed_token_types.add(token_type)
                first_set = First2.FIRST.get(token_type, [token_type])
                output_text_widget.insert(tk.END, f"FIRST({token_type}) = {{ {', '.join(sorted(first_set))} }}\n")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

def display_follow_sets(input_file, output_text_widget):
    try:
        with open(input_file, 'r') as file:
            text = file.read()
        tokens, _ = runner.run('<code.txt>', text)
        printed_token_types = set()
        output_text_widget.delete('1.0', tk.END)
        output_text_widget.insert(tk.END, "Follow Sets:\n")
        for token in tokens:
            token_type = token[0]
            if token_type not in printed_token_types:
                printed_token_types.add(token_type)
                follow_set = follow.FOLLOW.get(token_type, [token_type])
                output_text_widget.insert(tk.END, f"FOLLOW({token_type}) = {{ {', '.join(sorted(follow_set))} }}\n")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

# New function to create the parse tree window
def display_parse_tree(input_file):
    try:
        # Assuming the parsing module has a method to generate the parse tree
        with open(input_file, 'r') as file:
            text = file.read()
        code = parsing.tokenize(text)
        parse = parsing.Parser(code)  # Placeholder for actual parse tree generation method
        parse_tree= parse.parse_program()
        # Create a new window for the parse tree
        parse_tree_window = tk.Toplevel()
        parse_tree_window.title("Parse Tree")
        parse_tree_window.geometry("600x400")

        parse_tree_text = scrolledtext.ScrolledText(parse_tree_window, wrap=tk.WORD, width=80, height=20)
        parse_tree_text.pack(pady=20)

        # Display the parse tree in the text widget
        parse_tree_text.insert(tk.END, parsing.pretty_print(parse_tree))
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while generating the parse tree: {e}")
        
def display_symbol_table(input_file, output_text_widget):
    try:
        # Read the input file content
        with open(input_file, 'r') as file:
            text = file.read()

        # Create an instance of SymbolTable
        symbol_table = SymbolTable()
        symbol_table = Table.parse_code(text)  # Use the 'parse_code' function to parse the code and populate the symbol table

        # Create a temporary file to hold the symbol table output
        symbol_table_output = "symbol_table_output.txt"
        with open(symbol_table_output, 'w') as file:
            symbol_table.print_symbol_table(file)

        # Display the symbol table in the output text widget
        output_text_widget.delete('1.0', tk.END)
        output_text_widget.insert(tk.END, "Symbol Table:\n")
        with open(symbol_table_output, 'r') as file:
            output_text_widget.insert(tk.END, file.read())
        
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

def display_hash_table(input_file, output_text_widget):
    try:
        with open(input_file, 'r') as file:
            text = file.read()
        symbol_table = Table.parse_code(text)
        
        # Calculate the hash values for the variables
        hash_max = 4
        symbol_table_dict = {}
        for line in text.splitlines():
            match = Table.re.match(r"^\s*\w+\s+(\w+)\s*=", line)
            if match:
                variable_name = match.group(1)
                hash_value = Table.calculate_hash(variable_name, hash_max)
                symbol_table_dict[variable_name] = hash_value

        # Display the hash table in the output widget
        output_text_widget.delete('1.0', tk.END)
        output_text_widget.insert(tk.END, "Hash Symbol Table:\n")
        output_text_widget.insert(tk.END, f"{'Variable Name':<15}{'Hash Value'}\n")
        for variable_name, hash_value in symbol_table_dict.items():
            output_text_widget.insert(tk.END, f"{variable_name:<15}{hash_value}\n")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while generating the hash table: {e}")

def create_gui():
    root = tk.Tk()
    root.title("Compiler Design")
    root.geometry("1500x1000")
    
    # Set background color to #F3D9DC
    root.config(bg="#F3D9DC")

    title_label = tk.Label(root, text="Compiler Design", font=("Arial", 24), bg="#F3D9DC")
    title_label.pack(pady=10)

    input_frame = tk.Frame(root, bg="#F3D9DC")
    input_frame.pack(pady=10)

    input_label = tk.Label(input_frame, text="Input File:", bg="#F3D9DC")
    input_label.pack(side=tk.LEFT, padx=5)

    input_entry = tk.Entry(input_frame, width=60)
    input_entry.pack(side=tk.LEFT, padx=5, ipady=5)

    browse_button = tk.Button(input_frame, text="Browse", command=lambda: browse_input_file(input_entry), bg="#744253", fg="white")
    browse_button.pack(side=tk.LEFT, padx=5)

    display_button = tk.Button(input_frame, text="Display", command=lambda: display_file_content(input_entry, input_text), bg="#744253", fg="white")
    display_button.pack(side=tk.LEFT, padx=5)

    output_label = tk.Label(root, text="Output File:", bg="#F3D9DC")
    output_label.pack(pady=5)

    output_entry = tk.Entry(root, width=60)
    output_entry.insert(0, "output.txt")
    output_entry.pack(pady=5, ipady=5)

    text_frame = tk.Frame(root, bg="#F3D9DC")
    text_frame.pack(pady=10)

    input_text = scrolledtext.ScrolledText(text_frame, wrap=tk.WORD, width=40, height=30)
    input_text.pack(side=tk.LEFT, padx=5)

    output_text = scrolledtext.ScrolledText(text_frame, wrap=tk.WORD, width=120, height=30)
    output_text.pack(side=tk.LEFT, padx=5)

    button_frame = tk.Frame(root, bg="#F3D9DC")
    button_frame.pack(pady=10)

    tokens_button = tk.Button(button_frame, text="Display Tokens", command=lambda: display_tokens(input_entry.get(), output_text), bg="#744253", fg="white", width=15, height=1, font=1)
    tokens_button.pack(side=tk.LEFT, padx=5)

    first_sets_button = tk.Button(button_frame, text="First Sets", command=lambda: display_first_sets(input_entry.get(), output_text), bg="#744253", fg="white", width=15, height=1, font=1)
    first_sets_button.pack(side=tk.LEFT, padx=5)

    follow_sets_button = tk.Button(button_frame, text="Follow Sets", command=lambda: display_follow_sets(input_entry.get(), output_text), bg="#744253", fg="white", width=15, height=1, font=1)
    follow_sets_button.pack(side=tk.LEFT, padx=5)

    parse_tree_button = tk.Button(button_frame, text="Parse Tree", command=lambda: display_parse_tree(input_entry.get()), bg="#744253", fg="white", width=15, height=1, font=1)
    parse_tree_button.pack(side=tk.LEFT, padx=5)

    symbol_table_button = tk.Button(button_frame, text="Symbol Table", command=lambda: display_symbol_table(input_entry.get(), output_text), bg="#744253", fg="white", width=15, height=1, font=1)
    symbol_table_button.pack(side=tk.LEFT, padx=5)

    hash_table_button = tk.Button(button_frame, text="Hash Table", command=lambda: display_hash_table(input_entry.get(), output_text), bg="#744253", fg="white", width=15, height=1, font=1)
    hash_table_button.pack(side=tk.LEFT, padx=5)

    root.mainloop()

# Run the GUI
create_gui()
