import math,sys,os
import pygame	

path = os.path.dirname(os.path.realpath(__file__))
class texture:
	def __init__(self, imagepath = path + '/DefaultTexture.png'):
		self.text = pygame.image.load(imagepath)

	@property
	def image(self):
		return self.text

	def rotate(self):
		pass

	def scale(self,w,h):
		self.text = pygame.transform.scale(self.text,(w,h))


	def __repr__(self):
		return self.text
