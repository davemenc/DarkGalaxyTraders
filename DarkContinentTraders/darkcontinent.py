import os, pygame, sys,json,time,copy
from pygame.locals import *
from pygame.compat import geterror
from mapcreator import *
if not pygame.font: 
	print ('Warning, fonts disabled')
	exit()
if not pygame.mixer: print ('Warning, sound disabled')
main_dir = os.path.split(os.path.abspath(__file__))[0]
data_dir = os.path.join(main_dir, 'MASS')

BLUE = (45,70,255)
RED = (255,24,24)
BLACK = (  0,   0,   0)
WHITE = (255, 255, 255)
GREEN = (  0, 255,   0)
YELLOW = ( 255, 255, 0)
GREY = (128,128,128)

gamedata = {}
MAP_UNKNOWN = -1
MAP_CITY = 2
MAP_PLAYER=3
MAP_PLAYER2=4
MAP_PLAYER3=5

START_CASH = int(50)

SQUARE_UNKNOWN_COLOR = BLACK
SQUARE_PLAYER_COLOR = WHITE
SQUARE_PLAYER2_COLOR = BLACK
SQUARE_PLAYER3_COLOR = GREY
SQUARE_LAND_COLOR = GREEN
SQUARE_WATER_COLOR = BLUE
SQUARE_CITY_COLOR = RED

	
def load_game(fname):
	global gamedata
	fin = open(fname,"rt")
	s = fin.read()
	fin.close()
	try: 
		savedata = json.loads(s)	
	except:
		print "LOAD FAILED!",fname
		print s
		exit()
	for key in  savedata.keys():
		print key, type (savedata[key])
	oldmap = savedata['map']
	map = {}
	for key in oldmap:
		l  = key.split(",")
		map[(int(l[0]),int(l[1]))] = oldmap[key]
	savedata['known_commodities'] = set (savedata['known_commodities'])
	s = set()
	for l in savedata['known']:
		tup = (l[0],l[1])
		s.add(tup)
	savedata['known'] = s
	for key in  savedata.keys():
		gamedata[key] = savedata[key]
	
	
def save_game(fname):
	global gamedata
	print
	
	#print gamedata.keys()
	savedata = copy.deepcopy(gamedata)
	del savedata['DISPLAYSURF']
	savedata['known_commodities'] = list(savedata['known_commodities'])
	savedata['known'] = list(savedata['known'])
	map = savedata['map']
	newmap = {}
	for loc in map:
		s = str(loc[0])
		s += ","
		s += str(loc[1])
		newmap[s] = map[loc]

	savedata['map'] = newmap
	try:
		string = json.dumps(savedata)
		fout = open(fname,"wt")
		fout.write(string)
		fout.close()
		print "Saved Game To {}".format(fname)

	except:
		print "Save game failed"

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
	"""
	Goal: make sure that every commodity is bought in 4 different cities.
	Strategy: use the 4 cities whose numbers are right after the sell city (which has the same number as the commodity)
	So commodity 4 is sold in city 4 and bought in 5, 6, 7 and 8. Always bought in 4 cities, never in the city it's sold in. 
	"""
	if cityno<citycount-4:
		demandlist = [cityno+1,cityno+2,cityno+3,cityno+4]
	elif cityno==citycount-4:
		demandlist = [cityno+1,cityno+2,cityno+3,0]
	elif cityno==citycount-3:
		demandlist = [cityno+1,cityno+2,1,0]
	elif cityno==citycount-2:
		demandlist = [cityno+1,2,1,0]
	elif cityno==citycount-1:
		demandlist = [3,2,1,0]
	random.shuffle(demandlist)
	return demandlist
	
def get_city_list(comm):
	global gamedata
	citycount = len(gamedata['city_list'])
	if comm==0:
		cities = [citycount-1,citycount-2,citycount-3,citycount-4]
	elif comm==1:
		cities = [citycount-1,citycount-2,citycount-3,0]
	elif comm==2:
		cities = [citycount-1,citycount-2,0,1]
	elif comm==3:
		cities = [citycount-1,0,1,2]
	elif comm>=4:
		cities = [comm-4,comm-3,comm-2,comm-1]
	return cities

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
		trade_db = gamedata['trade_db']
		trade_db[cityno]['known'] = True
		known_commodities = gamedata['known_commodities']
		known_commodities.add(cityno)
		demands = trade_db[cityno]['demands']
		for com in demands:
			known_commodities.add(com)

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
	elif player_state == 1:
		draw_map_square(player_location,MAP_PLAYER2)
		return 0
	else:
		#draw_map_square(player_location,get_squaretype(player_location))
		draw_map_square(player_location,MAP_PLAYER3)
		return 0
	
def draw_map_square(location,squaretype):
	global gamedata
	DISPLAYSURF = gamedata['DISPLAYSURF']
	SCREENX = gamedata['SCREENX']
	SCREENY = gamedata['SCREENY']
	limitx=SCREENX
	limity=SCREENY
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
	elif squaretype == MAP_PLAYER2: color = SQUARE_PLAYER2_COLOR
	elif squaretype == MAP_PLAYER3: color = SQUARE_PLAYER3_COLOR
	
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

def location_type_name(loc):
	global gamedata
	if loc in gamedata['city_list']:
		return "City"
	type = gamedata['map'][loc]
	if type == MAP_LAND:
		return 'Land'
	elif type == MAP_WATER:
		return 'Water'
	elif type == MAP_UNKNOWN:
		return 'Unknown'
	
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
def draw_text(str,font,position):
	global gamedata
	text = font.render(str,1,BLACK)
	gamedata['DISPLAYSURF'].blit(text,position)

def draw_ui():
	global gamedata
	SCREENX = gamedata['SCREENX']
	SCREENY = gamedata['SCREENY']
	DISPLAYSURF = gamedata['DISPLAYSURF']
	city_list = gamedata['city_list']
	commoditynames = gamedata['commoditynames']
	ui_regions = gamedata['ui_regions']
	trade_db = gamedata['trade_db']

	RIGHT_UI_WIDTH = gamedata['RIGHT_UI_WIDTH'] 
	TOP_UI_HEIGHT = gamedata['TOP_UI_HEIGHT']
	
	RIGHT_UI_WIDTH = 165
	TOP_UI_HEIGHT = 100
	
	FONT_SIZE = 24
	RIGHT_MARGIN = 15
	COM_WIDTH = 150
	COM_HEIGHT = 18
	COM_MARGIN = 20
	#RIGHT_RESERVE = COM_WIDTH+RIGHT_MARGIN*2
	#COM_LEFT = SCREENX-RIGHT_RESERVE+RIGHT_MARGIN
	#COM_TOP = SCREENY- (COM_HEIGHT*CITIES)-22
	SIDE_RECT_X = SCREENX -RIGHT_UI_WIDTH
	SIDE_RECT_Y = TOP_UI_HEIGHT
	TOP_RECT = (0,0,SCREENX,TOP_UI_HEIGHT)
	
	SIDE_RECT = (SIDE_RECT_X,0,RIGHT_UI_WIDTH,SCREENY)
	pygame.draw.rect(DISPLAYSURF,WHITE,ui_regions['topblank'],0)
	pygame.draw.rect(DISPLAYSURF,WHITE,ui_regions['leftblank'],0)
	
	#Commodity buttons
	com_title_h = 20
	#com_title1 = (SIDE_RECT_X+5,SIDE_RECT_Y)
	#com_title2 = (SIDE_RECT_X+5,SIDE_RECT_Y+com_title_h)
	font1 = pygame.font.Font(None, 26)
	text = font1.render("KNOWN", 1, BLACK)
	DISPLAYSURF.blit(text, ui_regions['com_title1'])
	text = font1.render("COMMODITIES", 1, BLACK)
	DISPLAYSURF.blit(text, ui_regions['com_title2'])
	
	com_top = SIDE_RECT_Y+com_title_h*2
	font2 = pygame.font.Font(None, 24)
	
	known_commodities = gamedata['known_commodities']
	temp = {}
	sorted_comms = []
	for c in known_commodities:
		temp[c] = commoditynames[c]
	for key, value in sorted(temp.iteritems(), key=lambda (k,v): (v,k)):
		sorted_comms.append({"key":key,"value":value})
	gamedata['sorted_comms'] = 	sorted_comms

	trade_db = gamedata['trade_db']

	for i in range(0,len(sorted_comms)):
		commno = sorted_comms[i]['key']
		name = commoditynames[commno]
		text = font2.render(name, 1, BLACK)
		sorted_comms[i]["height"] = text.get_height()
		posx = SIDE_RECT_X+COM_MARGIN
		posy =  COM_HEIGHT * i + com_top
		sorted_comms[i]["posy"] = posy
		sorted_comms[i]["posx"] = posx
		DISPLAYSURF.blit(text, (posx,posy))
	
	loc = gamedata['player_location']
	
	draw_text("Location: {}, {}".format(str(loc[0]),str(loc[1])),font2,ui_regions['location'])

	draw_text(location_type_name(loc),font2,ui_regions['squaretype'])
	
	hold = gamedata['hold']
	if hold == None:
		holdtxt = "Nothing"
	else:
		holdtxt = commoditynames[hold]
	draw_text("In Truck: {}".format(holdtxt),font2,ui_regions['hold'])
	
	draw_text("Cash: ${}".format(int(gamedata['cash'])),font2,ui_regions['cash'])
	
	if loc in city_list:
		city = city_list.index(loc)
		draw_text(trade_db[city]['cityname'],font2,ui_regions['cityname'])
		
		offer = trade_db[city]['offer']
		offername = commoditynames[offer]
		offerprice = trade_db[city]['offerprice']
		draw_text(offername,font2,ui_regions['offer_name'])

		draw_text("$"+str(offerprice),font2,ui_regions['offer_price'])
		
		if hold == None and offerprice<gamedata['cash']:
			draw_text("[Buy]",font2,ui_regions['offer_button'])
		demands = trade_db[city]['demands']
		rects = ui_regions['demands']
		for i in range(0,len(trade_db[city]['demands'])):
			draw_text(commoditynames[demands[i]],font2,rects[i]['name'])
			draw_text("$"+str(int(gamedata['demand_values'][demands[i]])),font2,rects[i]['price'])
			if hold == demands[i]:
				draw_text("[SELL]",font2,rects[i]['button'])
				#TODO Sometimes (when it's the last one listed?) it doesn't show the button


	pygame.display.update()

def create_trading_db():
	global gamedata
	PRICE_FILE = "prices1.txt"
	CITY_NAME_FILE ="citynames1.txt"
	COMMODITY_FILE = "commoditynames2.txt"
	commoditynames = load_data(COMMODITY_FILE)
	prices = load_data(PRICE_FILE)
	randomize_prices(prices)
	gamedata['demand_values'] = calc_demand_values(prices)
	
	citynames = load_data(CITY_NAME_FILE)
	trade_db = []
	city_list = gamedata['city_list']
	city_count = len(city_list)
	known_commodities = set()
	for i in range(0,len(city_list)):
		record = {}
		record['cityloc'] = city_list[i]
		record['cityname'] = citynames[i]
		record['offer'] = i
		record['offerprice'] = prices[i]
		record['known'] = False
		demands = get_demand_list(i,city_count)
		record['demands'] = demands
		trade_db.append(record)
	gamedata['trade_db'] = trade_db
	gamedata['commoditynames'] = commoditynames
	gamedata['known_commodities'] = known_commodities	

def pt_in_rect(pt,rect):
	x= pt[0]
	y=pt[1]
	left = rect[0]
	top = rect[1]
	right = left+rect[2]
	bottom = top+rect[3]
	return x>=left and x<=right and y>=top and y<=bottom
	
def act_on_mouse(click_loc):
	global gamedata	
	trade_db = gamedata['trade_db']
	commoditynames = gamedata['commoditynames']
	city = gamedata['city_list'].index(gamedata['player_location'])
	ui_regions = gamedata['ui_regions']
	if gamedata['hold'] == None and trade_db[city]['offerprice']<gamedata['cash'] and pt_in_rect(click_loc,ui_regions['offer_button']):
		price = trade_db[city]['offerprice']
		gamedata['hold'] = trade_db[city]['offer']
		gamedata['cash'] += -price
	for i in range(0,len(ui_regions['demands'])):
		if trade_db[city]['demands'][i] == gamedata['hold'] and pt_in_rect(click_loc,ui_regions['demands'][i]['button']):
			#sell commodity in hold
			price = gamedata['demand_values'][gamedata['hold']]
			gamedata['hold'] = None
			gamedata['cash'] += price
	
	comm = find_comm(click_loc)
	if comm == None: return
	comm_name = commoditynames[comm]
	cities = get_city_list(comm)
	for i in range(len(cities)-1,-1,-1):
		if not trade_db[cities[i]]['known']:
			del cities[i]	
""" TODO: Finish this routine; react to mouse clicks on commodities, """	
	
def find_comm(click_loc):
	global gamedata
	sorted_comms = 	gamedata['sorted_comms']
	if len(sorted_comms)== 0: return None
	left = sorted_comms[0]["posx"]
	if click_loc[0]<left:
		return None
	height = sorted_comms[0]['height']
	for i in range(0,len(sorted_comms)):
		top = sorted_comms[i]['posy']
		bottom = top + height
		click_y = click_loc[1]
		if click_y>top and click_y < bottom:
			return sorted_comms[i]['key']
	return None
	
def write_gameschema():
	global gamedata
	skip = ['map','trade_db','known_commodities', "city_list","commoditynames","known"]
	fout = open("gameschema.txt","at")
	fout.write("Game Schema Information\n")
	fout.write("\nGameData\n")
	for key in gamedata.keys():
		if key in skip:
			fout.write("{} {}\n".format(key, type(gamedata[key]) ) )
		else:
			fout.write("{} ({}): {}\n".format(key,type(gamedata[key]),gamedata[key]))
	trade_db = gamedata['trade_db']
	example = trade_db[0]
	fout.write("\nTrade_db\n")

	for key in example.keys():
			fout.write("{} ({})\n".format(key,type(example[key])))
	fout.close()
	
def calc_scores():
	global gamedata
	profit = gamedata['cash']-START_CASH+10000
	squares = len(gamedata['known'])
	moves = gamedata['moves']
	trade_db = gamedata['trade_db']
	explored_cities = 0
	for i in range(0,len(trade_db)):
		if trade_db[i]['known']:
			explored_cities += 1
		p_score = 0.0
	c_score = 0.0
	p_score = 0.0
	s_score = 0.0
	if moves > 0 :
		c_score = round(float(explored_cities)/float(moves),3)
		p_score = round(float(profit)/float(moves),3)
		s_score = round(float(squares)/float(moves),3)
	print
	print
	print "Total Moves: {}".format(moves)
	print "Total Cities: {}".format(explored_cities)
	print "Total Profit: {}".format(profit)
	print "Total Squares: {}".format(squares)
	print
	return c_score,p_score,s_score
	
def display_stats():
	global gamedata
	c_score,p_score,s_score = calc_scores()
	
	print "city ratio: {}".format(c_score)
	print "profit ratio: {}".format(p_score)
	print "square ratio: {}".format(s_score)
	print p_score, 100-p_score
	print "city score: {}".format(int((1-c_score)*1000))
	print "profit score: {}".format(int((100-p_score)*10))
	print "square score: {}".format(int((9-s_score)*1000))

	
def main():
	global gamedata
	if len(sys.argv)==1:
		# CONSTANTS #
		SCREENX = 1680
		SCREENY = 1050
		CITIES = 49
		MAPTYPE = 1
		RIGHT_UI_WIDTH = 165 
		TOP_UI_HEIGHT = 100

		# IMPORTANT VARIABLES #
		square_size = 10
		MAPSCREENX = (SCREENX-RIGHT_UI_WIDTH)
		MAPSCREENY = (SCREENY-TOP_UI_HEIGHT)
		mapwidth =  MAPSCREENX/square_size
		mapheight = MAPSCREENY/square_size
		offsetx = (MAPSCREENX - mapwidth*square_size)/2
		offsety = TOP_UI_HEIGHT #(MAPSCREENY - mapheight*square_size)/2
		map = gen_map(mapwidth,mapheight,type=MAPTYPE)
		city_list = make_cities(map,mapwidth,mapheight,CITIES)
		known = set()

		gamedata = {'map':map,'city_list':city_list,'known':known,'SCREENX':SCREENX,'SCREENY':SCREENY, 'mapwidth':mapwidth,'mapheight':mapheight}
		gamedata['player_location'] = random.choice(city_list)
		gamedata['square_size'] = square_size
		gamedata['offsetx'] = offsetx
		gamedata['offsety'] = offsety
		#gamedata['known_cities'] = known_cities
		gamedata['RIGHT_UI_WIDTH'] = RIGHT_UI_WIDTH 
		gamedata['TOP_UI_HEIGHT'] = TOP_UI_HEIGHT
		gamedata['cash'] = int(START_CASH)
		gamedata['moves'] = 0
		gamedata['hold'] = None
		
		create_trading_db()
		set_known(gamedata['player_location'],2)
	else:
		fname = sys.argv[1]
		loadgame(fname)
	
	#ui_regions are absolute point followed by width and height?
	COM_TITLE_H = 20
	COM_TITLE_MARGIN = 5
	COM_MARGIN = 20
	CHAR_WIDTH = 10
	STATUS_LEFT = 416
	STATUS_TOP = 3
	OFFER_LEFT = 680
	OFFER_TOP = STATUS_TOP
	DEMAND_LEFT=992
	TYPE_LEFT = 600
	DEMAND_TOP = STATUS_TOP
	LINE_H = 25
	COMMODITY_WIDTH = 100
	PRICE_WIDTH = 50
	BUTTON_WIDTH = 30
	tup = (MAPSCREENX,0,SCREENX-MAPSCREENX,SCREENY)
	ui_regions={
		"topblank":(0,0,SCREENX,TOP_UI_HEIGHT),
		"leftblank":(MAPSCREENX,0,SCREENX-MAPSCREENX,SCREENY),
		"com_title1":(SCREENX -RIGHT_UI_WIDTH+COM_TITLE_MARGIN, TOP_UI_HEIGHT, RIGHT_UI_WIDTH-COM_TITLE_MARGIN, COM_TITLE_H),
		"com_title2":(SCREENX -RIGHT_UI_WIDTH+COM_TITLE_MARGIN, TOP_UI_HEIGHT+COM_TITLE_H,RIGHT_UI_WIDTH-COM_TITLE_MARGIN, COM_TITLE_H),
		"known_comms":(SCREENX -RIGHT_UI_WIDTH+COM_MARGIN, TOP_UI_HEIGHT+COM_TITLE_H*2, RIGHT_UI_WIDTH-COM_MARGIN, SCREENY-(TOP_UI_HEIGHT+COM_TITLE_H*2)),
		"location":(STATUS_LEFT,STATUS_TOP,170,20),
		"squaretype":(TYPE_LEFT,STATUS_TOP,60,20),
		"cash":(STATUS_LEFT,STATUS_TOP+LINE_H,140,20),
		"hold":(STATUS_LEFT,STATUS_TOP+LINE_H*2,200,20),
		"cityname":(STATUS_LEFT,STATUS_TOP+LINE_H*3,100,20),
		"offer_name":(OFFER_LEFT,STATUS_TOP,COMMODITY_WIDTH,20),
		"offer_price":(OFFER_LEFT+COMMODITY_WIDTH,STATUS_TOP,PRICE_WIDTH,20),
		"offer_button":(OFFER_LEFT+COMMODITY_WIDTH+PRICE_WIDTH,STATUS_TOP,BUTTON_WIDTH,20),
		"demands":[
			{'name':(DEMAND_LEFT, STATUS_TOP,COMMODITY_WIDTH,20),
			'price':(DEMAND_LEFT+COMMODITY_WIDTH, STATUS_TOP, PRICE_WIDTH, 20),
			'button':(DEMAND_LEFT+COMMODITY_WIDTH+PRICE_WIDTH, STATUS_TOP, BUTTON_WIDTH, 20)},
			{'name':(DEMAND_LEFT,STATUS_TOP+LINE_H,COMMODITY_WIDTH,20),
			'price':(DEMAND_LEFT+COMMODITY_WIDTH,STATUS_TOP+LINE_H,PRICE_WIDTH,20),
			'button':(DEMAND_LEFT+COMMODITY_WIDTH+PRICE_WIDTH,28,BUTTON_WIDTH,20)},
			{'name':(DEMAND_LEFT,STATUS_TOP+LINE_H*2,COMMODITY_WIDTH,20),
			'price':(DEMAND_LEFT+COMMODITY_WIDTH,STATUS_TOP+LINE_H*2,PRICE_WIDTH,20),
			'button':(DEMAND_LEFT+COMMODITY_WIDTH+PRICE_WIDTH,STATUS_TOP+LINE_H*2,BUTTON_WIDTH,20)},
			{'name':(DEMAND_LEFT,STATUS_TOP+LINE_H*3,COMMODITY_WIDTH,20),
			'price':(DEMAND_LEFT+COMMODITY_WIDTH,STATUS_TOP+LINE_H*3,PRICE_WIDTH,20),
			'button':(DEMAND_LEFT+COMMODITY_WIDTH+PRICE_WIDTH,STATUS_TOP+LINE_H*3,BUTTON_WIDTH,20)}]
	}
	gamedata['ui_regions']=ui_regions

	##set up game
	#Initialize Everything
	pygame.init()
	DISPLAYSURF = pygame.display.set_mode(( SCREENX, SCREENY),pygame.FULLSCREEN)
	DISPLAYSURF.fill(BLACK)
	gamedata['DISPLAYSURF']=DISPLAYSURF

	pygame.display.set_caption('Trading Game')
	pygame.mouse.set_visible(1)
	clock = pygame.time.Clock()
	draw_known_map()
	#draw_whole_map()
	draw_map_square(gamedata['player_location'],MAP_PLAYER)
	draw_ui()
	old_player_location = gamedata['player_location']

	pygame.display.update()


	#Main Loop
	going = True
	player_state = 1
	while going:
		clock.tick(20)
		#Handle Input Events
		for event in pygame.event.get():
			if event.type == QUIT:
				going = False
			elif event.type == KEYDOWN and event.key == K_ESCAPE:
				going = False
			elif event.type == KEYDOWN:
				gamedata['moves'] += 1				
				gamedata['player_location'] = move_player_location(event.key,gamedata['player_location'])
			elif event.type == MOUSEBUTTONUP:
				click_location = event.pos
				act_on_mouse(click_location)
				draw_ui()


		#Draw Everything
		if old_player_location != gamedata['player_location']:
			set_known(gamedata['player_location'],2)
			draw_known_map()
			#draw_whole_map()
			draw_ui()
			old_player_location = gamedata['player_location']
		player_state = flash_player_icon(player_state,gamedata['player_location'])

		pygame.display.update()

	pygame.quit()
	#write_gameschema()
	
	save_game("testsave.txt")	
	display_stats()
#	load_game("testsave.txt")
	
#Game Over

#this calls the 'main' function when this script is executed
if __name__ == '__main__':
    main()

