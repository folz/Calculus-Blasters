'''
Created on Jun 28, 2010

@author: folz
'''

import pygame, math
from pygame.locals import *
from engine import *
from engine.misc import *
from entities import *

class BulletManager:

	def __init__( self, entity ):
		self.entity = entity
		self.lastshot = pygame.time.get_ticks()
		self.bullets = []

	def shoot( self, delta ):
		for b in self.bullets:
			b.move( delta )
			b.draw()

	def addBullet( self, location, velocity, facing="right" ):
		nowshot = pygame.time.get_ticks()
		if ( nowshot - self.lastshot ) > 150:
			self.lastshot = nowshot
			b = BulletEntity( location, velocity, facing )
			self.bullets.append( b )
			b.set_world_callback( self.entity.world )
			b.setBulletManagerCallback( self )

	def removeBullet( self, bullet ):
		if bullet in self.bullets:
			self.bullets.remove( bullet )
			del bullet

class NetworkBulletManager:

	def __init__( self, world ):
		self.world = world
		self.bullets = []

	def fromNetwork( self, bullets ):
		if len( bullets ) == 0: return
		for b in self.bullets:
			self.removeBullet( b )
		for b in bullets:
			self.addBullet( geometry.Vector( b[0], b[1] ) )

	def draw( self ):
		for b in self.bullets:
			b.draw()

	def addBullet( self, location ):
		b = BulletEntity( location, ( 0, 0 ), "right" )
		self.bullets.append( b )
		b.set_world_callback( self.world )
		b.setBulletManagerCallback( self )
		b.draw()

	def removeBullet( self, bullet ):
		if bullet in self.bullets:
			self.bullets.remove( bullet )
			del bullet
