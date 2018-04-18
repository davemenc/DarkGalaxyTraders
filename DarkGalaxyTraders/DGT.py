import random,sys,datetime,json

def serialize_list(fout,list,count):
	for i in range(0,count):
		element = list[i]
		fout.write("{}\n".format(element))
	fout.write("~\n")

def deserialize_list(fin):
	list = []
	value = ""
	while value != "~":
		line = fin.readline()
		value = line.strip()
		if value == "~":
			break
		try:
		    value = int(value)
		except:
			pass
		list.append(value)
	return list
	
def save_game(savename,graph,placenames,commoditynames,prices,demand_prices,cargo,cash,turn,known,current):
	fname = "{fname}{timestamp}.sav".format(fname=savename,timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M'))
	data={}
	data['graph']=graph
	data['placenames']=placenames
	data['commoditynames']=commoditynames
	data['prices']=prices
	data['demand_prices']=demand_prices
	data['cargo']=cargo
	data['cash']=cash
	data['turn']=turn
	data['known']=known
	data['current']=current
	json_string = json.dumps(data)
	fout = open(fname,"wt")
	fout.write(json_string)
	fout.close()


def load_game(savename):
	fin = open(savename,"rt")
	json_string = fin.read()
	fin.close()
	data = json.loads(json_string)
	return data
	
def print_instructions():
	print "Sorry, no instructions yet."
	
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

def connect_nodes(graph,node1,node2):
	if node1>=len(graph) or node2>=len(graph):#node1 or 2 are bogus
		return #so give up
	if node1 not in graph[node2]:
		graph[node2].append(node1)
	if node2 not in graph[node1]:
		graph[node1].append(node2)
	
def create_loops(graph,loopcount):
	#we're going to try to connect nodes with only 1 link to each other
	#first, get a list of single-list nodes
	singles = []
	for i in range(0,len(graph)):
		if len(graph[i])==1:
			singles.append(i)
	#now randomize
	random.shuffle(singles)
	#fix the goal so it's possible
	if loopcount>len(singles)/2: 
		loopcount = len(singles)/2
	#now get the top loopcount nodes and connect them
	for i in range(0,loopcount):
		connect_nodes(graph, singles[i],singles[loopcount+i])
		
def add_node(graph,node):
	newnode = len(graph)
	graph[node].append(newnode)
	graph.append([])
	graph[newnode].append (node)

def pick_node(graph):
	return random.randint(0,len(graph)-1)

def find_weak_node(graph,node):
# this takes some explanation
# the idea is that we want to add new nodes to nodes that don't have many links
# but we don't want it to be totally deterministic (or it would always be the same)
# g is the graph
# n is the starting node
# links = l
# the probability of using this node is 1/(l+1)
# in no case will we have a node with more than 4 links
	l = len(graph[node])#links this node of the graph has
	p = 1.0/float(l+1)
	if l>=4 or random.random()>p: #not this one
		next = random.choice(graph[node])
		return find_weak_node(graph,next)
	else:
		#print "weak node: {}, {} but {}".format(node,l,len(graph[node]))
		return node #this is the one!

def get_demand_list(node,graphlen):
		if node<graphlen-4:
			demandlist = [node+1,node+2,node+3,node+4]
		elif node==graphlen-4:
			demandlist = [node+1,node+2,node+3,0]
		elif node==graphlen-3:
			demandlist = [node+1,node+2,1,0]
		elif node==graphlen-2:
			demandlist = [node+1,2,1,0]
		elif node==graphlen-1:
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
		
def print_all_node_info(graph, placenames,commoditynames,prices,demand_prices):
	for i in range(0,len(graph)):
		demandlist = get_demand_list(i,len(graph))
		name = placenames[i]
		commodity = commoditynames[i]
		links = graph[i]
		
		print "\n{} ({}) sells {} ({}) for ${}.".format(name,i,commodity,i,prices[i])
		print "{} demands".format(name)
		for demand in demandlist:
			print "     {} ({}) for ${}".format(commoditynames[demand],demand,demand_prices[demand])
		print "{} is linked to".format(name)
		for link in links:
			print "     {}".format(placenames[link])

def print_short_node_info(graph,node, placenames,commoditynames,prices,demand_prices):
	demandlist = get_demand_list(node,len(graph))
	name = placenames[node]
	commodity = commoditynames[node]
	links = graph[node]

	print "{}; sells {} for ${}.".format(name,commodity,prices[node])
	print "    demands: ",
	for demand in demandlist:
		print "{} (${});".format(commoditynames[demand],demand_prices[demand]),
	print
	print "    links: ",
	for link in links:
		print "{}".format(placenames[link]),
	print

def print_node_info(graph,node, placenames,commoditynames,prices,demand_prices):
	demandlist = get_demand_list(node,len(graph))
	name = placenames[node]
	commodity = commoditynames[node]
	links = graph[node]

	print "\n{} ({}) sells {} ({}) for ${}.".format(name,node,commodity,node,prices[node])
	print "{} demands".format(name)
	for demand in demandlist:
		print "     {} ({}) for ${}".format(commoditynames[demand],demand,demand_prices[demand])
	print "{} is linked to".format(name)
	for link in links:
		print "     {}".format(placenames[link])

def main():
	# CONSTANTS
	MAXNODES = 40
	MAXLOOPS = 25 #these are edges that connect to existing nodes instead of new nodes
	PLACE_NAME_FILE = "placenames1.txt"
	PRICE_FILE = "prices1.txt"
	COMMODITY_FILE = "commoditynames1.txt"
	STARTING_CASH = 2000
	WINNING_CASH = 10000
	
	#loadgame
	if len(sys.argv)>1:
		savegamename = sys.argv[1]
		data = load_game(savegamename)
		graph = data['graph']
		placenames = data['placenames']
		commoditynames = data['commoditynames']
		prices = data['prices']
		demand_prices = data['demand_prices']
		cargo = data['cargo']
		cash = data['cash']
		turn = data['turn']
		known = data['known']
		current = data['current']
	else:
		# GRAPH STUFF
		graph = [[]]
		for i in range(0,MAXNODES):
			r = pick_node(graph)		
			n = find_weak_node(graph,pick_node(graph))
			add_node(graph,n)
		create_loops(graph,MAXLOOPS)

		# GAME STUFF
		placenames = load_data(PLACE_NAME_FILE)
		commoditynames = load_data(COMMODITY_FILE)
		prices = load_data(PRICE_FILE)
		randomize_prices(prices)
		demand_prices = calc_demand_values(prices)

		#print_all_node_info(graph, placenames,commoditynames,prices,demand_prices)	
		start = pick_node(graph)
		known = [start]
		current = start
		cash = STARTING_CASH
		cargo = None
		turn = 0
	
	print "WELCOME TO THE DARK GALAXY!"
	done = False
	shipmoved = True
	while not done:
		cargo_price = find_cargo_price(graph,cargo,current,demand_prices)
		if shipmoved:
			turn += 1
			print "\n+++++++ Turn {} +++++++".format(turn)
			print "You are currently at {}.".format(placenames[current])
			print "You have ${}. ".format(cash)
			if cargo == None:
				print "You have no cargo."
			else:
				print "You are carrying {}.".format(commoditynames[cargo])
			print_node_info(graph,current, placenames,commoditynames,prices,demand_prices)
			shipmoved = False
			
		### MENU ###
		print "--- MENU --- "
		allowed = ["?","0","1"]
		print " ? For instructions."
		print " 0 Quit game."
		print " 1 See list of places you've been."
		if cargo != None and cargo_price != None:
			print " 2 Sell your {} for ${}.".format(commoditynames[cargo],cargo_price)
			allowed.append("2")
		else:
			print "<2 is not allowed because you have no cargo that can be sold here"

		if cargo == None and cash>=prices[current]:
			print " 3 Buy {} for ${}.".format(commoditynames[current],prices[current])
			allowed.append("3")
		else:
			print "<3 is not allowed because you either already have a cargo or you don't have enough money"

		links = graph[current]
		for i in range(0,len(links)):
			print " {} move to {}.".format(i+4,placenames[links[i]])
			allowed.append(str(i+4))
		allowstring=""
		for command in allowed:
			if len(allowstring)!=0:
				allowstring+=", "
			allowstring+=command
		order = None
		#### GET ORDER ####
		while order not in allowed:
			order = raw_input("Enter one of {} based on the menu: ".format(allowstring))
		if order not in allowed:
			print "{} is not in the list of allowed orders ({}). Something is wrong. Exiting!".format(order,allowed)
			done = True
		
		##### PROCESS ORDER #####
		if order == "0":
			done = True
			save_game("DGT",graph,placenames,commoditynames,prices,demand_prices,cargo,cash,turn,known,current)

		elif order == "?":
			print_instructions()
		elif order== "1":
			print "\nHere is your known galaxy"
			for loc in known:
				print_short_node_info(graph,loc, placenames,commoditynames,prices,demand_prices)
			print	
		elif order == "2":
			cargo = None
			cash += cargo_price
			print "Selling your cargo for {}. You now have {}.".format(cargo_price,cash)
		elif order == "3":
			print "Buying {} for ${}.".format(commoditynames[current],prices[current])
			cash += -prices[current]
			cargo = current
			if cash<0:
				print "Something is wrong. You now have ${}! Exiting!".format(cash)
				done = True
		else:
			newnode = links[int(order)-4]
			shipmoved = True
			nodename = placenames[newnode]
			print "Moving to {}.".format(nodename)
			if newnode not in links:
				print "You are moving to {} ({}) but there is no connection from here ({})! Something is wrong. Exiting!".format(nodename,newnode,links)
				done = True
			current = newnode
			if newnode not in known:
				known.append(newnode)
		if cash >= WINNING_CASH:		
			done = True
			print "You WON because you have ${} which is more than ${}. Congratulations! Exiting.".format(cash,WINNING_CASH)

#### GAME OVER ###
	print_node_info(graph,current, placenames,commoditynames,prices,demand_prices)
	print "The Game is over!"
	
if __name__ == "__main__":
    main()
