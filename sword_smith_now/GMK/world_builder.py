from PIL import Image
import random, os, numpy
class builder(object):
	def __init__(self):
		pass
	def get_floors(self):
		floor_dir = os.listdir("./images/world_pieces/sized/floors")
		if floor_dir.__contains__("Thumbs.db"):
			# pesky windows feature
			floor_dir.pop(floor_dir.index("Thumbs.db"))
		##floors = {}
		##for i in floors:
		##	floors[i.split(".")[-1]] = i
		##self.floors = floors
		return floor_dir
	def generate_matrix(self):
		chunk_matrix = numpy.empty([6,6],dtype=object)
		for y in range(0,len(chunk_matrix)):
			for x in range(0,len(chunk_matrix[y])):
				chunk_matrix[y][x] = "_"
		width = random.randrange(2,5)
		height = random.randrange(2,5)
		floor_index = self.get_floors()
		biome = random.randrange(0,len(floor_index))
		for y in range(0,height):
			for x in range(0,width):
				chunk_matrix[y][x] = floor_index[biome]
		new_index = floor_index
		new_index.pop(biome)
		biome = random.randrange(0,len(new_index))
		w2 = 6 - width
		h2 = random.randrange(height,5)
		for y in range(0,h2):
			for x in range(width,width + w2):
				chunk_matrix[y][x] = new_index[biome]
		if h2 == height:
			w3 = random.randrange(2,6)
		else:
			#since we need to fit another chunk inside the height gaps of the two previous biomes
			w3 = width
		if 2 == 6-height:
			h3 = 2
		else:
			h3 = random.randrange(2,6-height)	
		biome = random.randrange(0,len(floor_index))
		for y in range(height,6):
			for x in range(0,w3):
				chunk_matrix[y][x] = floor_index[biome]
		biome = random.randrange(0,len(floor_index))
		for y in range(0,6):
			for x in range(0,6):
				if chunk_matrix[y][x] == '_':
					chunk_matrix[y][x] = floor_index[biome]
		return chunk_matrix
	def level(self,matrix):
		base = Image.new("RGB",(14400,14400),(255,255,255))
		index = {}
		for i in self.get_floors():
			index[i] = Image.open("./images/world_pieces/sized/floors/" + i)
		for yoff in range(0,len(matrix)):
			for xoff in range(0,len(matrix[yoff])):
				#the size of a chunk, multiplied by which chunk it is in the row
				x = 2400 * xoff
				y = 2400 * yoff
				##print(x,y)
				img = index[matrix[yoff][xoff]]
				base.paste(img,(x,y))
		return base
	def build(self):
		m = self.generate_matrix()
		img = self.level(m)
		return img
if __name__ == '__main__':
	b = builder()
	print("Building matrix...")
	m = b.generate_matrix()
	print("Pasting images...")
	img = b.level(m)
	print("Saving...")
	img.save("./saves/new_chunk.png")
	print("Saved.")
