import random, sys
import map_matrix
import grammar

# read folder that contains section maps
# associated with production rules
char_to_map = map_matrix.read_folder()

# get the handcrafted grammar production rules
production_rules = grammar.get_grammar_rules()

# generate a string using the production rules
grammar_string = grammar.generate_string(production_rules)

# convert the string into a matrix structure
matrix = grammar.string_to_map(grammar_string, char_to_map)

# save matrix structure into a file
map_matrix.save_map(matrix)

print("Generated string: {}".format(grammar_string))
map_matrix.print_map(matrix)

