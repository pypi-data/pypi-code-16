#!/usr/bin/env python

import os
import sys
import random
import inputs
from time import sleep
import timeit

# Python 2 or 3
if sys.version_info.major == 2:
    getInput = raw_input
else:
    getInput = input

def getButton():
    gp = inputs.devices.gamepads[0]
    count = 0
    while True:
        events = gp.read()
        if max([x.code.startswith('BTN_') and x.state == 0 for x in events]):
            return True

def setTermColor(back,fore):
    """Lame function to set background color of the terminal"""
    
    back = back.lower()
    fore = fore.lower()

    wincolor = {
        'black': '0',
        'blue': '1',
        'green': '2',
        'aqua': '3',
        'red': '4',
        'purple': '5',
        'yellow': '6',
        'white': '7',
        'gray': '8',
        'lightblue': '9',
        'lightgreen': 'A',
        'lightaqua': 'B',
        'lightred': 'C',
        'lightpurple': 'D',
        'lightyellow': 'E',
        'brightwhite': 'F'
    }
    
    # Treating Linux/Unix/Mac all the same
    if os.name == 'posix':
        os.system('setterm -background {0} -foreground {1}'.format(back,fore))
    
    # Windows
    elif os.name == 'nt':
        os.system('color {0}{1}'.format(wincolor[back],wincolor[fore]))
        
    else:
        raise Exception("What the heck are you running on?")

def clearScreen():
    if os.name == 'nt':
        os.system('cls')
        
    else:
        os.system('clear')
  
def main():
    setTermColor("white","black")
    clearScreen()

    print("Simple test of lag time for your game pad.")
    
    print("When I change the background color to Green, press a button on your controller. It will be randomized between 1 and 5 seconds.")

    print("We'll do this 10 times to get measurements.")

    print("Press button to start... ")

    getButton()
    times = []

    for i in range(10):
        setTermColor("yellow","black")
        clearScreen()
        sleeptime = random.randint(1000,5000)/1000

        sleep(sleeptime)
    
        setTermColor("green","black")
        clearScreen()
    
        times.append(timeit.timeit('getButton()',number=1,globals=globals()))

    setTermColor("black","white")
    clearScreen()
    print("Fastest: {0} seconds".format(min(times)))
    print("Slowest: {0} seconds".format(max(times)))
    print("Average: {0} seconds".format(sum(times)/len(times)))


if __name__ == "__main__":
    main()
