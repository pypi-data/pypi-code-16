import math,sys,os
from pysics.position import Position
from pysics.Vector import vector
from pysics.physics import engine

class Object:
	def __init__(self, name = None, ObjectID = None, position = vector(0,0), description = None, physics = True, texture = None, vertices = None, color = None, stroke = None):
		self.name = name
		self.id = ObjectID
		self.position = Position(position)
		self.description = description
		self.physics = physics
		self.vertices = vertices
		self.texture = texture
		if self.physics:
			self.physicsengine = engine(self)
		else:
			self.physicsengine = engine(self, Rigid = True)
		self.color = color
		self.stroke = stroke

	def __repr__(self):
		return self.description

	def draw(self,screen):
		if self.physics:
			self.physicsengine.applyphysics()
		if self.color == None:
			screen.DrawPolygon(position = self.position, texture = self.texture, points = self.vertices)
		else:
			screen.DrawPolygon(position = self.position, color = self.color, points = self.vertices, stroke = self.stroke)

class Liquid:
	def __init__(self, name = None, ObjectID = None, position = vector(0,0), description = None, physics = False, texture = None, vertices = None):
		self.name = name
		self.id = ObjectID
		self.position = Position(position)
		self.description = description
		self.physics = physics
		self.vertices = vertices
		self.texture = texture

	def __repr__(self):
		return self.description

	def draw(self,screen):
		screen.DrawPolygon(self.position)

