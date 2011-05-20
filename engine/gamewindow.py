'''
gamewindow.py

@author: folz
'''

import pygame

class GameWindow:
	'''
	A GameWindow is the actual window where Worlds are drawn.
	Sometimes it's fullscreen.
	'''
	def __init__( self, size=( 800, 600 ), title="PyGame", flags=pygame.SWSURFACE, screen=None ):
		self.width, self.height = self.size = size
		self.title = title
		self.flags = flags
		self.screen = screen
		self.visible = False

	### -------- get/set methods -------- ###

	def get_width( self ):
		return self.width

	def set_width( self, width ):
		if width == self.width:
			return
		self.width = width
		self.size = ( self.width, self.height )
		self.recreate()

	def get_height( self ):
		return self.height

	def set_height( self, height ):
		if height == self.height:
			return
		self.height = height
		self.size = ( self.width, self.height )
		self.recreate()

	def get_size( self ):
		return self.size

	def set_size( self, size ):
		if size == self.size:
			return
		self.size = size
		self.width, self.height = self.size
		self.recreate()

	def get_flags( self ):
		return self.flags

	def set_flags( self, flags ):
		if flags == self.flags:
			return
		self.flags = flags
		self.recreate()

	def get_title( self ):
		return self.screen.get_caption()

	def set_title( self, title ):
		if title == self.title:
			return
		if not self.visible:
			self.title = title
		else:
			pygame.display.set_caption( title )

	### -------- methods that actually do things -------- ###

	def set_world_callback( self, callback ):
		self.callback = callback

	def recreate( self ):
		if self.visible:
			pygame.display.quit()
			self.visible = False
			self.display()
		else:
			pass

	def display( self ):
		if not self.visible:
			pygame.display.init()
			pygame.display.set_caption( self.title )
			self.screen = pygame.display.set_mode( self.size, self.flags )
			self.visible = True
		else:
			pass
