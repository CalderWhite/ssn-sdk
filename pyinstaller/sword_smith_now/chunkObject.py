import pygame
pygame.init()
class rect(object):
	def __init__(self,rectt,color,width=0):
		"""Simple rectangle, nothing special. Since it works with the pygame "api" you should look at their docs if you want to know more. http://www.pygame.org/docs/ref/draw.html#pygame.draw.rect"""
		self.x = rectt[0]
		self.y = rectt[1]
		self.width = rectt[2]
		self.height = rectt[3]
		self.rectt = list(rectt)
		self.color = color
		self.border_width = width
		pass
	def get_rect(self):
		return self.rectt
	def draw(self,display,offset):
		pygame.draw.rect(display,self.color,[offset[0],offset[1],self.width,self.height],self.border_width)
		pass