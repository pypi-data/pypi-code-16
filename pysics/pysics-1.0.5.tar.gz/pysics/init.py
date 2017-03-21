import math,sys,os
try: import pygame
except ImportError:
	choice = input("The only dependency of this library is pygame. It seems like you haven't installed it though.\n do you want to install it now? Y/n")
	if choice == 'Y': import pip; pip.main(['install','pygame']); import pygame
	else: sys.exit()


class version:
	def __repr__(self):
		return 'pysics version alpha-1.0.4'

class init:
	def __init__(self, sound=False):
		pygame.init()
		if sound:
			pygame.mixer.init()

class Camera:
	def __init__(self, position = None):
		pass


