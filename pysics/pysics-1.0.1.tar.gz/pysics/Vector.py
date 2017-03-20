import math,sys,os

class vector:
	def __init__(self,x,y):
		self.x = x
		self.y = y

	def __add__(self, other):
		return self.__class__(self.x + other.x, self.y + other.y)

	def __sub__(self, other):
		return self.__class__(self.x - other.x, self.y - other.y)

	def __mul__(self):
		return self.__class__(self.x * other.x, self.y * other.y)

	def __len__(self):
		return (self.x**2 + self.y**2)**0.5

	def angle(self,atype = 'RADIAN'):
		if atype == 'RADIAN':
			return math.atan(self.x/self.y)
		else:
			return math.degrees(math.atan(self.x/self.y))

	def __repr__(self):
		return '[x: ' + str(self.x) + 'y: ' + str(self.y) + ']'

	def __str__(self):
		return '[x: ' + str(self.x) + 'y: ' + str(self.y) + ']'