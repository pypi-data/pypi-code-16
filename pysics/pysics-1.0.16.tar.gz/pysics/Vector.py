import math
import sys
import os


class vector:
    self.anglemode = "rad"

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, other):
        return self.__class__(self.x + other.x, self.y + other.y)

    def __iadd__(self, other):
        self.x += other.x
        self.y += other.y
        return self

    def __sub__(self, other):
        return self.__class__(self.x - other.x, self.y - other.y)

    def __isub__(self, other):
        self.x -= other.x
        self.y -= other.y
        return self

    def __mul__(self, val):
        return self.__class__(self.x * val, self.y * val)

    def __imul__(self, other):
        self.x *= other.x
        self.y *= other.y
        return self

    def __truediv__(self, val):
        return self.__class__(self.x / val, self.y / val)

    def __idiv__(self, other):
        self.x /= other.x
        self.y /= other.y
        return self

    def dist(self, other):
        return ((self.x - other.x)**2 + (self.y - other.y)**2)**0.5

    @property
    def heading(self):
        if self.anglemode == 'rad':
            return math.atan(self.x / self.y)
        elif self.anglemode = 'deg':
            return math.degrees(math.atan(self.x / self.y))

    def dot(self, other):
        return (self.x * other.x) + (self.y * other.y)

    @property
    def magnitude(self):
        return (self.x**2 + self.y**2)**0.5

    def setmag(self, val):
        m = self.magnitude
        self.x = (self.x / m) * val
        self.y = (self.y / m) * val

    def normalize(self):
        m = self.magnitude
        self.x = self.x / m
        self.y = self.y / m

    def copy(self):
        return vector(self.x, self.y)

    def __repr__(self):
        return '[x: ' + str(self.x) + '   y: ' + str(self.y) + ']'

    def __str__(self):
        return '[x: ' + str(self.x) + '   y: ' + str(self.y) + ']'

    def anglemodedeg(self):
        self.anglemode = 'deg'

    def anglemoderad(self):
        self.anglemode = 'rad'
