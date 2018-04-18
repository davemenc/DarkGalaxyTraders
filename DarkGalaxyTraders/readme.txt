Dark Galaxy Traders Readme

Welcome to Dark Galaxy Traders, the best trading game ever invented! (Really? No, not really. Just another damn trading game.)

Introduction
You are a trader in a mysterious galaxy in which solar systems are connected by wormholes. Every solar system has a name, a commodity it sells and one or more commodities it buys. 

Your mission is to fly your ship from system to system, buying and selling commodities until you get so rich that you retire (aka win).

Installing and Running The Game
The game runs in Python. You need to download python from somewhere to run the game. The game has a few "support files" that also must be present. At the time of this writing they include "commoditynames1.txt", "placenames1.txt", "help.txt", and "prices1.txt". 

If, for some reason, they are missing and you can't find a copy you can just create them in a text editor. Commoditynames has the names of commodities (a list of words). Placenames has the list of the names of the system (another list of words). Prices has the prices for the commodities (a list of numbers between 10 and 500). You need 21 of each of those but if you put in more it will simply randomly select among the numbers. Help has some subset of this readme that I think might be useful during the game. Knock yourself out. 

You install the game by putting the program (currently "DGT.py") and the support files in directory.

You run the game by typing "python <gamename>" on the command line. So "python DGT.py" should work. 

You can add an optional save game file after the game name and it will load and run the came from the save point of that file.

The Turn
This is a turn based game. Every turn you are told how much money you have, what, if any, cargo you have, what system you are in and the commodities bought and sold in that system.

Then you are given a "menu" of commands you can issue. You select one of the options on the menu and away you go. 

The Comands
The commands are mostly numbers. Why? Because letters (which might be easier to remember) can be upper or lower case. Probably easily solvable but you have to make choices and here we are. 

0: Quit the game. This automatically saves the game with a save game file with the date and time in it.
1: 