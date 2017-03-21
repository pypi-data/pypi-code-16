import math,sys,os
from pysics.Vector import vector

class sprite:
	def __init__(self, name = None, SpriteID = None, position = vector(0,0), description = None, physics = False):
		self.name = name
		self.id = SpriteID
		self.position = Position(position)
		self.description = description
		self.physics = physics

	def __repr__(self):
		return self.description

	def draw(self):
		pass
