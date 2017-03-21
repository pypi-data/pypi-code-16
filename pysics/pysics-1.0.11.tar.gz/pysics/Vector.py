import math,sys,os

class vector:
	def __init__(self,x,y):
		self.x = x
		self.y = y

	def __add__(self, other):
		return self.__class__(self.x + other.x, self.y + other.y)

	def __iadd__(self,other):
		self.x += other.x
		self.y += other.y

	def __sub__(self, other):
		return self.__class__(self.x - other.x, self.y - other.y)

	def __iadd__(self,other):
		self.x -= other.x
		self.y -= other.y

	def __mul__(self, val):
		return self.__class__(self.x * val, self.y * val)

	def __imul__(self,other):
		self.x *= other.x
		self.y *= other.y

	def __div__(self, val):
		return self.__class__(self.x / val, self.y / val)

	def __idiv__(self,other):
		self.x /= other.x
		self.y /= other.y

	def dist(self,other):
		return ((self.x - other.x)**2 + (self.y - other.y)**2)**0.5

	def heading(self,atype = 'RADIAN'):
		if atype == 'RADIAN':
			return math.atan(self.x/self.y)
		else:
			return math.degrees(math.atan(self.x/self.y))

	def dot(self,other):
		return (self.x*other.x)+(self.y*other.y)

	@property
	def magnitude(self):
		return (self.x**2 + self.y**2)**0.5

	def setmag(self,val):
		self.x = (self.x / self.magnitude)*val
		self.y = (self.y / self.magnitude)*val

	def normalize(self):
		self.x = self.x / self.magnitude
		self.y = self.y / self.magnitude

	def copy(self):
		return vector(self.x,self.y)

	def __repr__(self):
		return '[x: ' + str(self.x) + '   y: ' + str(self.y) + ']'

	def __str__(self):
		return '[x: ' + str(self.x) + '   y: ' + str(self.y) + ']'