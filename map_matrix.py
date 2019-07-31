def initialize_map(y_length=16,x_length=150):
	map = []
	for y in range(y_length):
		row = []
		for x in range(x_length):
			row.append("-")
		map.append(row)
	map[-2][2] = "M"
	return map

def print_map(map):
	for line in map:
		string = ""
		for char in line:
			string += char
		print(string)

def save_map(map, map_filename="map.txt"):
	output_file = open(map_filename, "w")
	
	for line in map:
		string = ""
		for char in line:
			string += char
		print(string, sep='', file=output_file)
	output_file.close()