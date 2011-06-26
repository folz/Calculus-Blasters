'''
Created on Jun 28, 2010

@author: folz
'''

import pygame, math
from pygame.locals import *
from engine import *
from engine.misc import *
from entities import *

class AsteroidManager:

	def __init__( self ):
		self.entity = entity
		self.lastshot = pygame.time.get_ticks()
		self.bullets = []

	def shoot( self, delta ):
		for b in self.bullets:
			b.move( delta )
			b.draw()

	def add_bullet( self, location, velocity, facing="right" ):
		nowshot = pygame.time.get_ticks()
		if ( nowshot - self.lastshot ) > 150:
			self.lastshot = nowshot
			b = BulletEntity( location, velocity, facing )
			self.bullets.append( b )
			b.set_world_callback( self.entity.world )
			b.setBulletManagerCallback( self )

	def remove_asteroid( self, asteroid ):
		if asteroid in self.bullets:
			self.bullets.remove( asteroid )
