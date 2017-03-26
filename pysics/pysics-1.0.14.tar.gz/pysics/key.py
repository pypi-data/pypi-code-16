import math,sys,os
import pygame

class key:
	def __init__(self):
		self.pressed = []

	def get_pressed(self):
		self.pressed = pygame.key.get_pressed()
		return self.pressed

	def is_pressed(self,key):
		self.pressed = pygame.key.get_pressed()
		self.temp = False
		exec('if self.pressed[pygame.K_' + key + ']: self.temp = True')
		if self.temp:
			return True # return true when selected key is pressed
		else:
			return False # else return false

	def get_last_pressed(self):
		return self.pressed

	def __repr__(self):
		return pygame.key.get_pressed()


