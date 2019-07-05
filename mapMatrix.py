def initializeMap():
	map = []
	for y in range(16):
		row = []
		for x in range(150):
			row.append("-")
		map.append(row)
	map[-2][2] = "M"
	return map

def printMap(map):
	for line in map:
		string = ""
		for char in line:
			string += char
		print(string)

def saveMap(map, map_filename="map.txt"):
	output_file = open(map_filename, "w")
	
	for line in map:
		string = ""
		for char in line:
			string += char
		print(string, sep='', file=output_file)
	output_file.close()