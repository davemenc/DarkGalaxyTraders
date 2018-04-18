from PIL import Image
import random,sys,math,json

def save_data(filename,data):
	fout = open(filename,"wt")
	json_string = json.dumps(data)
	fout.write(json_string)
	fout.close()
def load_data(filename):
	fin = open(filename,"rt")
	json_string = fin.read()
	fin.close()
	data = json.loads(json_string)
	return data

IMAGE_BLACK = 0
IMAGE_WHITE = 1
MAP_WATER = 1
MAP_LAND = 0

def copy_black(target,source,offset):
	ssize = source.size
	tsize = target.size
	if ssize[0]!=500 or ssize[1]!=500:
		print "source is wrong size!"
		source = source.resize((500,500))
	if tsize[0]!=750 or tsize[1]!=750:
		target =target.resize((750,750))
	spix = source.load()
	tpix = target.load()
	offx = offset[0]
	offy = offset[1]
	#print "ssize,tsize,offset",ssize,tsize,offset
	#print
	for x in range(0,ssize[0]):
		for y in range(0,ssize[1]):
			if spix[x,y] == IMAGE_BLACK: # this is black
				#print x,y,offx,offy,x+offx,y+offy
				tpix[x+offx,y+offy] = IMAGE_BLACK
			
def gen_landmass():
	#define some lists

	imagelist = ["mass60.png","mass64.png","mass65.png","mass68.png","mass69.png","mass70.png","mass71.png","mass72.png","mass73.png","mass74.png","mass75.png","mass76.png","mass77.png","mass78.png","mass79.png","mass80.png","mass81.png","mass82.png","mass83.png","mass84.png","mass85.png","mass86.png","mass87.png","mass88.png","mass89.png","mass90.png","mass91.png","mass92.png","mass93.png","mass94.png","mass95.png","mass96.png","mass97.png","mass98.png","mass99.png"]
	rotatelist = [0,90,270,180]
	methodlist = [Image.FLIP_LEFT_RIGHT,Image.FLIP_TOP_BOTTOM,"DONTFLIP"]
	offsets=[(0,0),(250,0),(0,250),(250,250)]

	final = Image.new("1", (750, 750), "white")#get me a blank slate
	pix = final.load() #get the pixels
	for i in range(0,4): #add 4 landmasses
		newimage = "MASS/"
		fname = random.choice(imagelist)#pick which one at randome    
		#print fname
		newimage = newimage + fname
		im = Image.open(newimage) #open it
		
		method = random.choice(methodlist) #transpose it (or not)
		if method!="DONTFLIP":
			im = im.transpose(method)
		im = im.rotate(random.choice(rotatelist)) #rotate it (or not)
		offset = offsets[i] #get the amount to offset (images overlap 250 pix)
		#print "i:{}; deg:{}; newimage:{}; offset:{}".format(i,deg,newimage,offset)

		copy_black(final,im,offset) #copy the black pix into final -- white is transparent
	return final

def create_map(width,height):
	map = {}
	for x in range(0,width):
		for y in range(0,height):
			map[(x,y)] = MAP_WATER #sea squares
	return map

def add_landmass_to_map(landmass,map,width,height,offset):
	pix = landmass.load()
	lm_size = landmass.size
	#print "add_landmass: width:{} height:{} offset:{}".format(width,height,offset)
	for x in range(0,lm_size[0]):
		for y in range(0,lm_size[1]):
			mapx = x + offset[0]
			mapy = y + offset[1]
			if pix[x,y]==IMAGE_BLACK:
				map[mapx,mapy] = MAP_LAND #land squares
	return map

def print_map(map,width,height):
	for y in range(0,height):
		print
		for x in range(0,width):
			print map[x,y],
			
	print			
def gen_map(mapwidth,mapheight,type=0,subtype=0):
	basemap = create_map(mapwidth,mapheight)
	#print "Gen_map: width: {}, height: {}".format(mapwidth,mapheight)
	#how many landmasses on the map? (it's water between the land masses)
	if type == 0:#pick type at random
		type = random.randint(0,1)+random.randint(0,1)+random.randint(0,1)+random.randint(0,1)
		if type == "0":
			type = "2"

	#print "Gen_map: maptype = {}".format(type)
	leftedge = 1
	topedge = 1
	if type == 1: #one huge landmass
		width = mapwidth-leftedge*2
		height = mapheight-2
		offsetx = leftedge
		offsety = topedge
		add_landmass_to_map(gen_landmass().resize((width,height)),basemap,mapwidth,mapheight,(offsetx,offsety))
		
	elif type == 2:
		#print "type 2"
		width = (mapwidth-leftedge*3)/2
		height = mapheight-topedge*2
		offsetx = leftedge
		offsety = topedge
		add_landmass_to_map(gen_landmass().resize((width,height)),basemap,mapwidth,mapheight,(offsetx,offsety))
		offsetx = width+leftedge*2
		offsety = topedge
		add_landmass_to_map(gen_landmass().resize((width,height)),basemap,mapwidth,mapheight,(offsetx,offsety))
	elif type == 3:
		if subtype == 0:
			subtype = random.randint(0,2)
		print "Type 3, subtype = {}".format(subtype)
		if subtype == 0:#two top, one bottom
			width = (mapwidth-2)/2
			height = (mapheight-2)/2
			offsetx = leftedge
			offsety = topedge
			add_landmass_to_map(gen_landmass().resize((width,height)),basemap,mapwidth,mapheight,(offsetx,offsety))
			offsetx=width+leftedge
			offsety = topedge
			add_landmass_to_map(gen_landmass().resize((width,height)),basemap,mapwidth,mapheight,(offsetx,offsety))
			offsetx = leftedge
			offsety = topedge*2+height
			width = mapwidth-leftedge*2
			add_landmass_to_map(gen_landmass().resize((width,height)),basemap,mapwidth,mapheight,(offsetx,offsety))

		elif subtype == 1:#one top, two bottom
			width = mapwidth-leftedge*2
			height = (mapheight-4)/2
			offsetx = leftedge
			offsety = topedge
			add_landmass_to_map(gen_landmass().resize((width,height)),basemap,mapwidth,mapheight,(offsetx,offsety))
			width = (mapwidth-2)/2
			offsetx = leftedge*3
			offsety = height+topedge*2
			add_landmass_to_map(gen_landmass().resize((width,height)),basemap,mapwidth,mapheight,(offsetx,offsety))
			offsetx = width+4
			offsety = height+1
			add_landmass_to_map(gen_landmass().resize((width,height)),basemap,mapwidth,mapheight,(offsetx,offsety))
			
		elif subtype == 2:# three in a row
			width = (mapwidth-leftedge*3)/3
			height = mapheight-4
			offsetx = leftedge
			offsety = topedge
			add_landmass_to_map(gen_landmass().resize((width,height)),basemap,mapwidth,mapheight,(offsetx,offsety))
			offsetx= leftedge*2+width
			offsety = topedge
			add_landmass_to_map(gen_landmass().resize((width,height)),basemap,mapwidth,mapheight,(offsetx,offsety))
			offsetx =leftedge*3+width*2
			offsety = topedge
			add_landmass_to_map(gen_landmass().resize((width,height)),basemap,mapwidth,mapheight,(offsetx,offsety))
			
	elif type == 4:# two and two
		width = (mapwidth-4)/2
		height = (mapheight-4)/2
		offsetx = leftedge
		offsety = topedge
		add_landmass_to_map(gen_landmass().resize((width,height)),basemap,mapwidth,mapheight,(offsetx,offsety))
		offsetx= width+leftedge*2
		offsety = topedge
		add_landmass_to_map(gen_landmass().resize((width,height)),basemap,mapwidth,mapheight,(offsetx,offsety))
		offsetx=leftedge
		offsety = height+topedge*2
		add_landmass_to_map(gen_landmass().resize((width,height)),basemap,mapwidth,mapheight,(offsetx,offsety))
		offsetx= width+leftedge*2
		offsety = height+topedge*2
		add_landmass_to_map(gen_landmass().resize((width,height)),basemap,mapwidth,mapheight,(offsetx,offsety))
	return basemap


def make_cities(map,mapwidth,mapheight,city_count):
	city_side = int(math.sqrt(city_count))
	horizontalsquares = mapwidth/city_side
	verticalsquares = mapheight/city_side
	regionlist = []
	for sx in range(0,city_side):
		for sy in range(0,city_side):
			regionlist.append((sx,sy))
	random.shuffle(regionlist)
	#print "mapw: {} maph: {} citycount: {}, city_side: {}, horizontalsquares: {}, verticalsquares: {} ".format(mapwidth,mapheight,city_count,city_side,horizontalsquares,verticalsquares)
	city_list = []
	while len(city_list)<city_count and len(regionlist)>0:
		region = regionlist[-1]
		del regionlist[-1]
		#x and y are the region values times the size of a region plus some portion of that size
		city_x = region[0] * horizontalsquares + random.randint(0,horizontalsquares)
		city_y = region[1] * verticalsquares + random.randint(0,verticalsquares)
		if map[city_x,city_y] == MAP_LAND:
			city_list.append((city_x,city_y))
		else: #can't put the city in water; find the nearest land
			distances = {}
			for x in range(city_x,0,-1):
				if map[x,city_y]==MAP_LAND:
					distances[(x,city_y)] = city_x - x + 1
					break
			for x in range(city_x,mapwidth):
				if map[x,city_y]==MAP_LAND:
					distances[(x,city_y)] = x - city_x + 1
					break
			for y in range(city_y,mapheight):
				if map[city_x,y]==MAP_LAND:
					distances[(city_x,y)] =  y - city_y + 1
					break
			for y in range(city_y,0,01):
				if map[city_x,y]==MAP_LAND:
					distances[(city_x,y)] = city_y - y + 1
					break
			bestdist = 1000
			best = -1
			for loc in distances:
				if distances[loc]<bestdist:
					best = loc
					bestdist = distances[loc]
			city_list.append(best)
	return city_list


#todo: change the map printer to add cities (just for fun and debugging); add a list of "known squares" modularize this ; create and display a map
#now combine the graph game to this; pick a starting point; add some UI, away we go...


	