import math,sys,os
import pygame
from pygame import gfxdraw
from pysics.position import Position
from pysics.background import background
from pysics.Vector import vector
from pysics.texture import texture

class screen:
	def __init__(self,w = 640, h = 480, origin=vector(0,0), fps=False):
		self.origin = Position(origin)
		self.screen = pygame.display.set_mode((w,h))
		self.width = w
		self.height = h
		self.background = background(self.screen)
		self.states = []
		pygame.display.set_icon(texture().image)

	def set_icon(self,texture = texture()):
		pygame.display.set_icon(texture.image)

	def translate(self, neworigin = vector(0,0)):
		self.origin = self.origin.position = neworigin

	def update(self):
		pygame.display.flip()
		for Event in pygame.event.get():
			if Event.type == pygame.QUIT:
				quit()
				sys.exit()

	def push(self):
		self.states.append(self.origin)

	def pop(self):
		self.origin = self.states.pop()

	def DrawPolygon(self, position = None, texture = None, points = None, color = None, stroke = None):
		pointslist = []
		for i in range(0,len(points)):
			pointslist.append((points[i].x + self.origin.x + position.x, points[i].y + self.origin.y - position.y))
		
		if color == None:
			gfxdraw.textured_polygon(self.screen, pointslist, texture.image, position.x + self.origin.x, position.y - self.origin.y)
		if texture == None:
			pygame.draw.polygon(self.screen,color,pointslist,stroke)