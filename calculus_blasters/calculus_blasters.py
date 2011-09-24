'''
Created on Jun 23, 2010

@author: folz
'''

from engine import *
from engine.misc import *

import entities
import expr

class CalculusBlasters:
	TITLE = "Calculus Blasters"

	def __init__( self ):
		pygame.init()

		# set the dimensions of the display window
		self.SIZE = self.WIDTH, self.HEIGHT = 800, 600

		# set the FPS
		self.FPS = 30

		# the actual FPS value refers to the delay, so let's update it properly
		# 1000ms/self.FPS = delay (but we're still calling it FPS)
		self.FPS = 1000 / self.FPS

		# create the window and display it
		self.window = gamewindow.GameWindow( self.SIZE )
		self.window.set_title( CalculusBlasters.TITLE )
		self.window.set_flags( pygame.HWSURFACE | pygame.DOUBLEBUF )# | pygame.FULLSCREEN )
		self.window.display()

		self.clock = pygame.time.Clock()

		self.keys = {
			pygame.K_ESCAPE : False,
			pygame.K_LEFT : False,
			pygame.K_RIGHT : False,
			pygame.K_z : False,
			pygame.K_x : False
		}

		self.world = world.World( ( 800, 600 ) )
		self.world.set_background( "blasters-gui.png" )
		self.world.debug = True

		# create the viewport that will view the world
		self.viewport = viewport.Viewport( self.window, self.world )

		self.question_text, self.answer_text, self.null = expr.generate()
		self.question = entity.SentenceEntity( ( 177, 450 ), self.question_text, size=20 )
		self.answer = entity.SentenceEntity( ( 178, 522 ), self.answer_text, size=20 )
		self.world.add_entity( self.question )
		self.world.add_entity( self.answer )

		self.delta = 0.0
		self.fps_count = 0.0

		self.running = True
		while self.running:
			self.game_loop()

	def regenerate_problem( self ):
		try:
			self.question.remove()
			self.answer.remove()
		except:
			pass
		self.question_text, self.answer_text, null = expr.generate()
		self.question = entity.SentenceEntity( ( 177, 450 ), self.question_text, size=20 )
		self.answer = entity.SentenceEntity( ( 178, 522 ), self.answer_text, size=20 )
		self.world.add_entity( self.question )
		self.world.add_entity( self.answer )

	def handle_events( self ):
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				self.running = False

			elif event.type in ( pygame.KEYDOWN, pygame.KEYUP ):
				print( event )
				self._handle_keys( event )

	def _handle_keys( self, keyEvent ):
		key = keyEvent.key

		if key == pygame.K_ESCAPE:
			pygame.event.post( pygame.event.Event( pygame.QUIT ) )

		print ( keyEvent )

		if keyEvent.type == pygame.KEYDOWN:
			if key == pygame.K_BACKSPACE:
				self.answer.backspace()
			elif key == pygame.K_RETURN:
				print( expr.check( self.answer_text, self.answer.text ) )
			else:
				self.answer.type( keyEvent.unicode )

	def do_logic( self ):
		if self.keys[pygame.K_ESCAPE]:
			pygame.event.post( pygame.event.Event( pygame.QUIT ) )

	def game_loop( self ):
		# Timing controls

		self.delta = self.clock.tick()
		self.fps_count += self.delta

		self.window.set_title( "{0} (FPS: {1})".format( CalculusBlasters.TITLE, 1000 / self.fps_count ) )

		self.handle_events()
		self.do_logic()

		self.viewport.update( self.delta )

		if self.fps_count > self.FPS:
			self.fps_count -= self.FPS
			self.viewport.render( self.delta )

		pygame.display.flip()

if __name__ == "__main__":
	CalculusBlasters()

