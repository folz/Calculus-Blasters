'''
Created on Jun 23, 2010

@author: folz
'''

from engine import *
from engine.misc import *

import multiplayer
import managers
import entities

class CalculusBlasters:
	def __init__( self, id, svrip ):
		pygame.init()

		self.id = id
		self.svrip = svrip
		self.client = multiplayer.Client( self.svrip, self.use_data )
		self.player2 = None

		# set the dimensions of the display window
		self.SIZE = self.WIDTH, self.HEIGHT = 800, 600

		# set the FPS
		self.FPS = 30

		# the actual FPS value refers to the delay, so let's update it properly
		# 1000ms/self.FPS = delay (but we're still calling it FPS)
		self.FPS = 1000 / self.FPS

		# create the window and display it
		self.window = gamewindow.GameWindow( self.SIZE )
		self.window.set_title( "Calculus Blasters" )
		self.window.set_flags( pygame.HWSURFACE | pygame.DOUBLEBUF )# | pygame.FULLSCREEN )
		self.window.display()

		self.helveticaFnt = pygame.font.SysFont( "Arial", 16, True, False )

		self.clock = pygame.time.Clock()

		self.keys = {
			pygame.K_ESCAPE : False,
			pygame.K_LEFT : False,
			pygame.K_RIGHT : False,
			pygame.K_z : False,
			pygame.K_x : False
		}

		self.world = world.World( ( 2000, 2000 ) )
		self.world.set_background( "giantbg.png" )
		self.world.set_gravity( geometry.Vector( 0, 1 ) )
		self.world.debug = True

		self.networkBullets = managers.NetworkBulletManager( self.world )

		# create the viewport that will view the world
		self.viewport = viewport.Viewport( self.window, self.world )

		# create a player1 character
		if self.id == 1:
			self.player1 = entities.PlayerEntity( "blue", ( 1940, 1940 ) )
			self.player2 = entities.PlayerEntity( "red", ( 100, 100 ), "rocketplok.gif" )
		elif self.id == 2:
			self.player1 = entities.PlayerEntity( "red", ( 100, 100 ) )
			self.player2 = entities.PlayerEntity( "blue", ( 1940, 1940 ), "rocketplok.gif" )

		self.world.add_entity( self.player1, attrs="player" )
		self.world.set_entity_name( self.player1, "player1" )
		self.player1.addGun( managers.BulletManager( self.player1 ) )

		self.world.add_entity( self.player2, attrs="player" )
		self.world.set_entity_name( self.player2, "player2" )
		self.player2.addGun( managers.BulletManager( self.player2 ) )

		self.flag1 = entities.FlagEntity( "red", ( 50, 175 ) )
		self.flag2 = entities.FlagEntity( "blue", ( 1950, 1975 ) )
		self.world.add_entity( self.flag1 )
		self.world.add_entity( self.flag2 )

		self.polygons = ()

		self.viewport.follow( self.player1 )

		self.running = True

		self.delta = 0.0
		self.delta_count = 0.0

		self.make_terrain()

		while self.running:
			self.game_loop()

	def use_data( self, data ):
		if self.player2 is None:
			return
		if data is None:
			return
		if data.pId != self.id:
			print( data )
			self.player2.location = geometry.Vector( data.px, data.py )
			self.player2.set_facing( data.pf )
			if self.id == 2:
				self.flag1.set_facing( data.ff )
				self.flag2.updateScore( data.s )
				if data.fc:
					self.flag1.was_captured_by( self.player2 )
				else:
					self.flag1.release()
			else:
				self.flag2.set_facing( data.ff )
				self.flag1.updateScore( data.s )
				if data.fc:
					self.flag2.was_captured_by( self.player2 )
				else:
					self.flag2.release()
			#networkBullets.fromNetwork(data.bullets)
			for b in data.bullets:
				self.player2.gun.addBullet( ( b[0], b[1] ), ( b[2], b[3] ) )
			if data.hit:
				self.player1.was_hit()

	def create_block( self, x, y, w, h ):
		p = geometry.Terrain( [( x, y ), ( x + w, y ), ( x + w, y + h ), ( x, y + h )], self.world )
		self.world.add_terrain( p )

	def make_terrain( self ):

		# create a boundary around the world
		leftWall = geometry.Slope( [( 0, 0 ), ( 0, self.world.get_height() )] )
		self.world.add_terrain( leftWall )

		rightWall = geometry.Slope( [( self.world.get_width(), 0 ), ( self.world.get_width(), self.world.get_height() )] )
		self.world.add_terrain( rightWall )

		topWall = geometry.Slope( [( 0, 0 ), ( self.world.get_width(), 0 )] )
		self.world.add_terrain( topWall )

		bottomWall = geometry.Slope( [( 0, self.world.get_height() ), ( self.world.get_width(), self.world.get_height() )] )
		self.world.add_terrain( bottomWall )

	def handle_keys( self, keyEvent ):
		key = keyEvent.key

		if keyEvent.type == pygame.KEYDOWN:
			self.keys[key] = True

		if keyEvent.type == pygame.KEYUP:
			self.keys[key] = False

	def handle_events( self ):
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				self.client.kill()
				self.running = False

			elif event.type in ( pygame.KEYDOWN, pygame.KEYUP ):
				self.handle_keys( event )

	def send_data( self ):
		bullets = self.player1.gun.bullets
		bs = []
		for b in bullets:
			if not b.sent:
				bs.append( ( b.location.x, b.location.y, b.velocity.x, b.velocity.y ) )
				b.sent = True

		if self.id == 1:
			flagFace = self.flag1.facing
			score = self.flag2.score
			cap = self.flag1.captured
		else:
			flagFace = self.flag2.facing
			score = self.flag1.score
			cap = self.flag2.captured
		data = multiplayer.Data( self.player1.location.x, self.player1.location.y,
								bs, id, self.player2.hit, self.player1.facing,
								flagFace, score, cap )
		self.client.send_data( data )
		self.player2.hit = False

	def do_logic( self ):
		self.player1.moving = False

		if self.keys[pygame.K_ESCAPE]:
			pygame.event.post( pygame.event.Event( pygame.QUIT ) )

		if self.keys[pygame.K_LEFT]:
			self.player1.moving = True
			self.player1.facing = "left"
			if self.player1.wasFacing == "right":
				self.player1.velocity.x = 0
			self.player1.velocity.x += -.6

		if self.keys[pygame.K_RIGHT]:
			self.player1.moving = True
			self.player1.facing = "right"
			if self.player1.wasFacing == "left":
				self.player1.velocity.x = 0
			self.player1.velocity.x += .6

		if self.keys[pygame.K_z]:
			self.player1.start_jumping()

		if self.keys[pygame.K_x]:
			self.player1.shoot()
			self.keys[pygame.K_x] = False

	def game_loop( self ):
		# Timing controls
		self.delta = self.clock.tick()
		self.delta_count += self.delta

		self.handle_events()
		self.do_logic()
		self.send_data()

		self.viewport.update( self.delta )
		if self.delta_count > self.FPS:
			self.delta_count -= self.FPS
			self.viewport.render( self.delta )


		self.networkBullets.draw()
		self.window.screen.blit( self.helveticaFnt.render( "Blue Team Score: " + str( self.flag2.score ), True, ( 0, 0, 255 ), ( 0, 0, 0 ) ), ( 0, 0 ) )
		self.window.screen.blit( self.helveticaFnt.render( "Red Team Score: " + str( self.flag1.score ), True, ( 255, 0, 0 ), ( 0, 0, 0 ) ), ( 0, 18 ) )
		pygame.display.flip()

if __name__ == "__main__":
	id = int ( input ( "id? " ) )
	svrip = input ( "server ip? " )
	CalculusBlasters( id, svrip )

