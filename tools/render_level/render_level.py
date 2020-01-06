import sys, os
from PIL import Image

def parse_file(filename):
	map_data = []
	input_file = open(filename, "r")
	for line in input_file:
		map_data.append([])
		for char in line[:-1]:
			map_data[-1].append(char)
	return map_data

def load_tile_images(tiles):
    tile_dict = {}
    for t in tiles:
        symbol = t.split("/")[1].split(".")[0]
        tile_dict[symbol] = Image.open(t)
    return tile_dict

if __name__ == '__main__':
    filename = "input_level.txt"
    level = parse_file(filename)

    level_width = len(level[0])
    level_height = len(level)
    print("Rows: {}. Columns: {}".format(level_width, level_height))

    tiles = ["tiles/"+f for f in os.listdir("tiles/") if "png" in f]

    tile_dict = load_tile_images(tiles)

    tile_width = 17 #tile_dict[next(iter(tile_dict))].size[0]
    tile_height = 16 #tile_dict[next(iter(tile_dict))].size[1]
    print("tile width: {}".format(tile_width))
    print("tile height: {}".format(tile_height))

    image_width = tile_width*level_width
    image_height = tile_height*level_height
    print("image width: {}".format(image_width))
    print("image height: {}".format(image_height))

    new_im = Image.new('RGBA', (image_width, image_height))
    x_offset = 0; y_offset = 0

    for i in range(level_height):
        for j in range(level_width):
            new_im.paste(tile_dict[level[i][j]], (x_offset,y_offset))
            x_offset += tile_width
        y_offset += tile_height
        x_offset = 0

    new_im.save('output_level.png')
