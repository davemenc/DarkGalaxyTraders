import os, pygame, sys,json,time
from pygame.locals import *
from pygame.compat import geterror
from mapcreator import *
if not pygame.font: print ('Warning, fonts disabled')
if not pygame.mixer: print ('Warning, sound disabled')
main_dir = os.path.split(os.path.abspath(__file__))[0]
data_dir = os.path.join(main_dir, 'MASS')

BLUE = (45,70,255)
RED = (255,24,24)
BLACK = (  0,   0,   0)
WHITE = (255, 255, 255)
GREEN = (  0, 255,   0)

gamedata = {}
MAP_UNKNOWN = -1
MAP_CITY = 2
MAP_PLAYER=3

SQUARE_UNKNOWN_COLOR = BLACK
SQUARE_PLAYER_COLOR = WHITE
SQUARE_LAND_COLOR = GREEN
SQUARE_WATER_COLOR = BLUE
SQUARE_CITY_COLOR = RED

def randomize_prices(prices):
	for i in range(0,len(prices)):
		prices[i]=int(prices[i])+random.randint(-3,2)

def calc_demand_values(prices):
	demands = []
	for p in prices:
		demands.append(round(float(p)*1.33+37+random.randint(-2,3)))
	return demands
	
def load_data(filename):
	item_list = []
	fin = open(filename,'rt')
	for line in fin:
		item_list.append(line.strip())
	random.shuffle(item_list)
	return item_list

def get_demand_list(cityno,citycount):
		if cityno<graphlen-4:
			demandlist = [cityno+1,cityno+2,cityno+3,cityno+4]
		elif cityno==graphlen-4:
			demandlist = [cityno+1,cityno+2,cityno+3,0]
		elif cityno==graphlen-3:
			demandlist = [cityno+1,cityno+2,1,0]
		elif cityno==graphlen-2:
			demandlist = [cityno+1,2,1,0]
		elif cityno==graphlen-1:
			demandlist = [3,2,1,0]
		random.shuffle(demandlist)
		return demandlist
		
def find_cargo_price(graph,cargo,node,demand_prices):
	if cargo==None:
		return None
	demand_list = get_demand_list(node,len(graph))
	if cargo not in demand_list:
		return None
	return demand_prices[cargo]
		

def clear_known():
	global gamedata
	known = gamedata['known']
	for i in known:
		del known[i]
	
def set_known(square,dist=1):
	global gamedata
	known = gamedata['known']
	basex = square[0]
	basey = square[1]
	for off_x in range(-dist,dist+1):
		for off_y in range(-dist,dist+1):
			known.add((basex+off_x,basey+off_y))
	city_list = gamedata['city_list']
	if square in city_list:
		cityno = city_list.index(square)
		known_cities = gamedata['known_cities']
		known_cities.add(cityno)
			

def get_squaretype(location):
	global gamedata
	known = gamedata['known']
	if location not in known:
		return MAP_UNKNOWN
	city_list = gamedata['city_list']
	if location in city_list:
		return MAP_CITY
	map = gamedata['map']
	return map[location]

def flash_player_icon(player_state,player_location):
	global gamedata
	if player_state == 0:
		draw_map_square(player_location,MAP_PLAYER)
		return 1
	else:
		draw_map_square(player_location,get_squaretype(player_location))
		return 0
	
def draw_map_square(location,squaretype):
	global gamedata
	DISPLAYSURF = gamedata['DISPLAYSURF']
	SCREENX = gamedata['SCREENX']
	SCREENY = gamedata['SCREENY']
	limitx=SCREENX
	limity=SCREENY
	square_size = gamedata['square_size']
	square_size = gamedata['square_size']
	mapwidth = gamedata['mapwidth']
	mapheight = gamedata['mapheight']
	offsetx = gamedata['offsetx']
	offsety = gamedata['offsety']

	if squaretype == MAP_LAND: color = SQUARE_LAND_COLOR
	elif squaretype == MAP_WATER: color = SQUARE_WATER_COLOR
	elif squaretype == MAP_UNKNOWN: color = SQUARE_UNKNOWN_COLOR
	elif squaretype == MAP_CITY: color = SQUARE_CITY_COLOR
	elif squaretype == MAP_PLAYER: color = SQUARE_PLAYER_COLOR
	
	mapx = location[0]
	mapy = location[1]
	x = mapx*square_size+offsetx
	y = mapy*square_size+offsety
	pygame.draw.rect(DISPLAYSURF,color,(x+1,y+1,square_size-1,square_size-1),0)
	
def draw_known_map():
	global gamedata
	known = gamedata['known']
	map = gamedata['map']
	for location in map:
		if location in known:
			draw_map_square(location,map[location])
	citylist = gamedata['city_list']
	for location in citylist:
		if location in known:
			draw_map_square(location,MAP_CITY)
	draw_grid(BLACK)
	
def draw_whole_map():
	global gamedata
	map = gamedata['map']
	for location in map:
		draw_map_square(location,map[location])
	citylist = gamedata['city_list']
	for location in citylist:
		draw_map_square(location,MAP_CITY)
	draw_grid(BLACK)

	

def draw_grid(color):
	global gamedata
	DISPLAYSURF = gamedata['DISPLAYSURF']
	SCREENX = gamedata['SCREENX']
	SCREENY = gamedata['SCREENY']
	offsetx = gamedata['offsetx']
	offsety = gamedata['offsety']
	square_size = gamedata['square_size']
	mapwidth = gamedata['mapwidth']
	mapheight = gamedata['mapheight']
	limitx=square_size*mapwidth+offsetx
	limity=square_size*mapheight+offsety
	for ix in range(0,mapwidth):
		for iy in range(0,mapheight):
			x = ix*square_size+offsetx
			y = iy*square_size+offsety
		
			pygame.draw.line(DISPLAYSURF,color,(x,offsety),(x,limity),1)
			pygame.draw.line(DISPLAYSURF,color,(offsetx,y),(limitx,y),1)	

	
	# draw the edges
	pygame.draw.line(DISPLAYSURF,color,(offsetx,limity),(limitx,limity),2)
	pygame.draw.line(DISPLAYSURF,color,(limitx,offsety),(limitx,limity),2)	
	pygame.draw.line(DISPLAYSURF,color,(offsetx,offsety),(limitx,offsety),2)
	pygame.draw.line(DISPLAYSURF,color,(offsetx,offsety),(offsetx,limity),2)	

def draw_square(gamex,gamey,color):
	global gamedata
	RECTSIZE=10
	drawx = gamex*linespace+offsetx+linespace/2+1
	drawy = gamey*linespace+offsety+linespace/2+1
	pygame.draw.rect(Surface, color, [drawx,drawy,drawx+RECTSIZE,drawy+RECTSIZE], width=0)
	
def move_player_location(key,player_location):
	global gamedata
	x = player_location[0]
	y = player_location[1]
	if key == K_q or key == K_KP7: #up/left
		x+=-1
		y+=-1
	elif key == K_w or key == K_KP8: #up
		x+=0
		y+=-1
	elif key == K_e or key == K_KP9: #up/right
		x+=1
		y+=-1
	elif key == K_a or key == K_KP4: #left
		x+=-1
		y+=0
	elif key == K_f or key == K_KP6: #right
		x+=1
		y+=0
	elif key == K_z or key == K_KP1: #down/left
		x+=-1
		y+=1
	elif key == K_x or key == K_KP2: #down
		x+=0
		y+=+1
	elif key == K_c or key == K_KP3: #down right
		x+=1
		y+=1
	map = gamedata['map']
	if map[x,y]== MAP_LAND:
		return (x,y)
	else: 
		return player_location

def main():
	global gamedata
	
	# CONSTANTS #
	SCREENX = 1680
	SCREENY = 1050
	RIGHT_RESERVE = 250
	COM_WIDTH = 110
	COM_HEIGHT = 18
	COM_LEFT = SCREENX-RIGHT_RESERVE+5
	MAPTYPE = 1
	PRICE_FILE = "prices1.txt"
	CITY_NAME_FILE ="citynames1.txt"
	COMMODITY_FILE = "commoditynames2.txt"
	CITIES = 50

	# IMPORTANT VARIABLES #
	square_size = 10
	mapwidth =  (SCREENX-RIGHT_RESERVE-2*square_size)/square_size
	mapheight = (SCREENY-2*square_size)/square_size
	offsetx = (SCREENX - mapwidth*square_size-RIGHT_RESERVE)/2
	offsety = (SCREENY - mapheight*square_size)/2
	map = gen_map(mapwidth,mapheight,type=MAPTYPE)

	city_list = make_cities(map,mapwidth,mapheight,CITIES)
	player_location = random.choice(city_list)
	known = set()
	known_cities = set()
	
	gamedata = {'map':map,'city_list':city_list,'known':known,'SCREENX':SCREENX,'SCREENY':SCREENY, 'mapwidth':mapwidth,'mapheight':mapheight}
	gamedata['square_size'] = square_size
	gamedata['offsetx'] = offsetx
	gamedata['offsety'] = offsety
	gamedata['player_location'] = player_location
	gamedata['known_cities'] = known_cities

	citynames = load_data(CITY_NAME_FILE)
	commoditynames = load_data(COMMODITY_FILE)
	prices = load_data(PRICE_FILE)
	randomize_prices(prices)
	demand_prices = calc_demand_values(prices)

	set_known(player_location,2)
	if player_location in city_list:
		cityno = city_list.index(player_location)
		known_cities.add(cityno)
	
	##set up game
	#Initialize Everything
	pygame.init()
	DISPLAYSURF = pygame.display.set_mode(( SCREENX, SCREENY),pygame.FULLSCREEN)
	DISPLAYSURF.fill(BLACK)
	gamedata['DISPLAYSURF']=DISPLAYSURF

	pygame.display.set_caption('Trading Game')
	pygame.mouse.set_visible(0)
	clock = pygame.time.Clock()
	draw_known_map()
	#draw_whole_map()
	draw_map_square(player_location,MAP_PLAYER)
	pygame.draw.rect(DISPLAYSURF,WHITE,(SCREENX-RIGHT_RESERVE,0,RIGHT_RESERVE,SCREENY),0)
	pygame.display.update()
	old_player_location = player_location

	#Main Loop
	going = True
	player_state = 1
	while going:
		clock.tick(20)
		player_state = flash_player_icon(player_state,player_location)
		#Handle Input Events
		for event in pygame.event.get():
			if event.type == QUIT:
				going = False
			elif event.type == KEYDOWN and event.key == K_ESCAPE:
				going = False
			elif event.type == KEYDOWN:
				player_location = move_player_location(event.key,player_location)

		#Draw Everything
		if old_player_location != player_location:
			set_known(player_location,2)
			draw_known_map()
			old_player_location = player_location
		pygame.draw.rect(DISPLAYSURF,WHITE,(SCREENX-RIGHT_RESERVE,0,RIGHT_RESERVE,SCREENY),0)
		
		if pygame.font:
			font = pygame.font.Font(None, 24)
			maxwidth = -1
			maxheight = -1
			for i in range(0,len(city_list)):
				name = commoditynames[i]
				text = font.render(name, 1, BLACK)
				width = text.get_width()
				height = text.get_height()
				if width>maxwidth:
					maxwidth = width
				if height>maxheight:
					maxheight = height
				textpos = (COM_LEFT, COM_HEIGHT * i)
				DISPLAYSURF.blit(text, textpos)
		pygame.display.update()

	pygame.quit()
#Game Over
	print city_list
	print known_cities
#this calls the 'main' function when this script is executed
if __name__ == '__main__':
    main()

