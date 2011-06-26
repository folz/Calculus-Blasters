'''
Created on Jun 21, 2010

@author: folz
'''

import pygame
from pygame.locals import *
from engine import geometry
from engine import misc

class Entity( pygame.sprite.Sprite ):
	'''
	An entity represents any element that appears in a World
	'''

	PIXELSPERVECTOR = 1

	def __init__( self,
				location=geometry.Vector( 0, 0 ),
				velocity=geometry.Vector( 0, 0 ) ):

		pygame.sprite.Sprite.__init__( self )


		if isinstance( location, geometry.Vector ):
			self.location = location
		else:
			self.location = geometry.Vector( location[0], location[-1] )

		if isinstance( velocity, geometry.Vector ):
			self.velocity = velocity
		else:
			self.velocity = geometry.Vector( velocity[0], velocity[-1] )

	def __repr__( self ):
		return "Entity at (%d, %d) on %s with vector %s" % ( self.location.x, self.location.y, self.world, self.velocity )

	def set_world_callback( self, world ):
		self.world = world

	def real_move( self, delta ):
		self.move( delta )

	def move( self, delta ):
		'''
		This should be overwritten by subclasses
		'''
		pass

	def draw( self ):
		'''
		See ImageEntity below
		'''
		pass

class ImageEntity( Entity ):
	def __init__( self, image=None,
				location=geometry.Vector( 0, 0 ),
				velocity=geometry.Vector( 0, 0 ) ):
		Entity.__init__( self, location, velocity )

		if isinstance( image, pygame.Surface ):
			self.image = image
		else:
			self.image = misc.load_image( image )

		if image is not None:
			self.rect = self.image.get_rect()

	def get_width( self ):
		return self.image.get_width()

	def get_height( self ):
		return self.image.get_height()

	def get_size( self ):
		return self.get_width(), self.get_height()

	def is_on_screen( self ):
		return self.location.x + self.get_width() >= self.world.viewport.get_x_coord() \
			and self.location.x <= self.world.viewport.get_x_coord() + self.world.get_width() \
			and self.location.y + self.get_height() >= self.world.viewport.get_y_coord() \
			and self.location.y <= self.world.viewport.get_y_coord() + self.world.get_height()

	def draw( self ):
		self.world.blit( self.image, self.rect )

class SentenceEntity( Entity ):
	def __init__( self, location, text, font='Courier New', size=12, bold=False, italic=False ):
		Entity.__init__( self, location, ( 0, 0 ) )

		self.text = text
		self.__font__ = pygame.font.SysFont( font, size, bold, italic )

		self.update_size()

	def type( self, unicode ):
		self.text += unicode
		self.update_size()

	def backspace( self ):
		self.text = self.text[:-1]
		self.update_size()

	def update_size( self ):
		self.width, self.height = self.size = self.__font__.size( self.text )

	def is_on_screen( self ):
		return self.location.x + self.width >= self.world.viewport.get_x_coord() \
			and self.location.x <= self.world.viewport.get_x_coord() + self.world.get_width() \
			and self.location.y + self.height >= self.world.viewport.get_y_coord() \
			and self.location.y <= self.world.viewport.get_y_coord() + self.world.get_height()

	def draw( self ):
		self.world.blit( 
					self.__font__.render( self.text, True, ( 0, 0, 0 ) ),
					( self.location.x, self.location.y )
					)

class CollidableEntity( ImageEntity ):
	def __init__( self, image=None,
				location=geometry.Vector( 0, 0 ),
				velocity=geometry.Vector( 0, 0 ) ):
		Entity.__init__( self, image, location, velocity )

		self.bounding_poly = geometry.Rect( self.rect.x, self.rect.y, self.get_width(), self.get_height() )

	def real_move( self, delta ):
		ImageEntity.real_move( self, delta )

		self.check_collisions( delta )

	def get_bounding_poly( self ):
		return self.bounding_poly

	def set_bounding_poly( self, poly ):
		self.bounding_poly = poly

	def move( self, delta ):
		pass

	def check_collisions( self, delta ):
		'''
		This should be overridden by subclasses
		'''
		pass

