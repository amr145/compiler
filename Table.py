import re

class SymbolTable:
    def __init__(self):
        self.table = []
        self.counter = 0
        self.address = 0
        self.data_type_sizes = {'int': 2, 'float': 4, 'string': 8, 'void': 0}  # Added 'void' size
        self.references = {}

    def add_variable(self, var_name, data_type, line_decl, is_function=False, num_args=0):
        dimensions = num_args if is_function else 0
        variable_entry = {
            'Counter': self.counter,
            'Variable Name': var_name,
            'Address': self.address,
            'Data Type': data_type,
            'No. of Dimensions': dimensions,
            'Line Declaration': line_decl,
            'Reference Line': '{}'
        }
        self.table.append(variable_entry)
        self.references[var_name] = {'declared_at': line_decl, 'references': []}
        self.counter += 1
        self.address += self.data_type_sizes[data_type]

    def update_reference(self, var_name, line_ref):
        if var_name in self.references:
            self.references[var_name]['references'].append(line_ref)
            for entry in self.table:
                if entry['Variable Name'] == var_name:
                    if entry['Reference Line'] == '{}':
                        entry['Reference Line'] = f'{line_ref}'
                    else:
                        entry['Reference Line'] += f', {line_ref}'

    def print_symbol_table(self, file):
        file.write(f"{'Counter':<10}{'Variable Name':<20}{'Address':<10}{'Data Type':<15}{'No. of Dimensions':<20}{'Line Declaration':<20}{'Reference Line'}\n")
        file.write("=" * 95 + "\n")
        for entry in self.table:
            file.write(f"{entry['Counter']:<10}{entry['Variable Name']:<20}{entry['Address']:<10}{entry['Data Type']:<15}{entry['No. of Dimensions']:<20}{entry['Line Declaration']:<20}{entry['Reference Line']}\n")

def read_code_from_file(filename):
    try:
        with open(filename, 'r') as file:
            return file.read()
    except FileNotFoundError:
        print(f"File {filename} not found.")
        return None

def parse_code(code):
    symbol_table = SymbolTable()
    lines = code.splitlines()
    for line_num, line in enumerate(lines, start=1):
        var_decl_match = re.match(r"(int|float|string)\s+([a-zA-Z0-9_]+)\s*=\s*(.*);", line)
        if var_decl_match:
            data_type = var_decl_match.group(1)
            var_name = var_decl_match.group(2)
            symbol_table.add_variable(var_name, data_type, line_num)

        func_decl_match = re.match(r"do\s+([a-zA-Z0-9_]+)\s*\((.*)\)\s*{", line)
        if func_decl_match:
            func_name = func_decl_match.group(1)
            params = func_decl_match.group(2).split(',')
            num_args = len(params) if params != [''] else 0
            symbol_table.add_variable(func_name, 'void', line_num, is_function=True, num_args=num_args)

        func_call_match = re.match(r"call\s+([a-zA-Z0-9_]+)\s*\((.*)\)\s*;", line)
        if func_call_match:
            func_name = func_call_match.group(1)
            symbol_table.update_reference(func_name, line_num)

        var_ref_match = re.findall(r"\b([a-zA-Z0-9_]+)\b", line)
        for var_name in var_ref_match:
            if var_name not in ['int', 'float', 'string', 'do', 'return', 'if', 'else', 'for', 'call', 'print']:
                symbol_table.update_reference(var_name, line_num)

    return symbol_table

def calculate_hash(variable_name, hash_max):
    variable_length = len(variable_name)
    ascii_sum = sum(ord(char) for char in variable_name[0])
    hash_value = (variable_length + ascii_sum) % hash_max
    return hash_value

def main():
    filename = 'code.txt'
    output_file = 'Table.txt'

    with open(output_file, 'w') as file:
        code = read_code_from_file(filename)
        if code:
            symbol_table = parse_code(code)
            symbol_table.print_symbol_table(file)
            file.write("\nHash Symbol Table:\n")
            hash_max = 4
            symbol_table_dict = {}
            for line in code.splitlines():
                match = re.match(r"^\s*\w+\s+(\w+)\s*=", line)
                if match:
                    variable_name = match.group(1)
                    hash_value = calculate_hash(variable_name, hash_max)
                    symbol_table_dict[variable_name] = hash_value

            file.write(f"{'Variable Name':<15}{'Hash Value'}\n")
            for variable_name, hash_value in symbol_table_dict.items():
                file.write(f"{variable_name:<15}{hash_value}\n")

if __name__ == "__main__":
    main()
