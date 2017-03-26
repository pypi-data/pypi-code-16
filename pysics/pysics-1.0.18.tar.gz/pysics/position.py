import math,sys,os
from pysics.Vector import vector

class Position:
	def __init__(self, pos = vector(0,0), size = None, acceleration = vector(0,0), speed = vector(0,0)):
	
		self.position = pos
		self.size = size
		self.acceleration = acceleration
		self.speed = speed

	def add(self, addedposvector):
		self.position.x += addedposvector.x
		self.position.y += addedposvector.y

	@property
	def x(self):
		return self.position.x

	@property
	def sx(self):
		return self.speed.x

	@property
	def sy(self):
		return self.speed.y

	@property
	def ax(self):
		return self.acceleration.x

	@property
	def ay(self):
		return self.acceleration.y

	@property
	def y(self):
		return self.position.y

	@property
	def w(self):
		return self.position.w

	@property
	def h(self):
		return self.position.h

	
	def __repr__(self):
		return str(self.position)
