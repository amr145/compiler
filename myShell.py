import runner
import First2
import follow
mytokens = []

def count_unique_tokens(tokens):
    unique_token_types = set()  # Set to store unique token types
    for token in tokens:
        unique_token_types.add(token[0])  # Add the token type to the set
    return len(unique_token_types)

def process_code(input_file, output_file):
    try:
        # Read code from the input file
        with open(input_file, 'r') as code_file:
            text = code_file.read()

        # Tokenize the input code
        tokens, error = runner.run('<code.txt>', text)

        # Write results to the output file
        with open(output_file, 'w') as out_file:
            if error:
                # Write the error message if any
                out_file.write(error.as_string() + '\n')
            else:
                # Write tokens and count unique token types
                out_file.write('_' * 15 + " Tokens Set " + '_' * 15 + '\n\n')
                out_file.write(f"Tokens:\n")
                for token in tokens:
                    mytokens.append(token)
                    out_file.write(f"{token}\n")
                unique_count = count_unique_tokens(tokens)
                out_file.write(f"\nNumber of unique token types: {unique_count}\n\n")

                # Compute and write FIRST sets for the relevant token types
                out_file.write('_' * 15 + " First Set " + '_' * 15 + '\n\n')
                printed_token_types = set()  # Track printed token types
                for token in tokens:
                    token_type = token[0]
                    if token_type not in printed_token_types:
                        printed_token_types.add(token_type)
                        
                        # Explicitly handle the number token type
                        # if token_type == "<number>":
                        #     first_set = [str(token.value)]  # Add the number value to the FIRST set
                        # else:
                        first_set = First2.FIRST.get(token_type, [token_type])

                        # Write the FIRST set
                        first_set_sorted = sorted(first_set)
                        out_file.write(f"FIRST({token_type}) = {{ {', '.join(first_set_sorted)} }}\n")


                out_file.write('_' * 15 + " Follow Set " + '_' * 15 + '\n\n')
                printed_token_types = set()  # Track printed token types
                for token in tokens:
                    token_type = token[0]
                    if token_type not in printed_token_types:
                        printed_token_types.add(token_type)
                        
                        
                        follow_set = follow.FOLLOW.get(token_type, [token_type])

                    
                        follow_set_sorted = sorted(follow_set)
                        out_file.write(f"FOLLOW({token_type}) = {{ {', '.join(follow_set_sorted)} }}\n")



        print(f"Processing completed. Output written to {output_file}")

    except FileNotFoundError as e:
        print(f"File error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

# Define input and output file paths
input_file_path = "code.txt"
output_file_path = "output.txt"

# Process the code
process_code(input_file_path, output_file_path)
