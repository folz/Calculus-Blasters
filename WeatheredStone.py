'''
Created on Jun 23, 2010

@author: folz
'''

import pygame, math
from pygame.locals import *
from engine import *
from engine.misc import *

import multiplayer
import managers
import entities

class WeatheredStone:
	def __init__( self, id, svrip ):
		self.id = id
		self.svrip = svrip
		self.client = multiplayer.Client( self.svrip, self.useData )

		# set the dimensions of the display window
		self.SIZE = self.WIDTH, self.HEIGHT = 800, 600

		# create the window and display it
		self.window = gamewindow.GameWindow( self.SIZE )
		self.window.set_title( "Calculus Blasters" )
		self.window.set_flags( pygame.HWSURFACE | pygame.DOUBLEBUF )# | pygame.FULLSCREEN )
		self.window.display( )

		pygame.init( )
		self.helveticaFnt = pygame.font.SysFont( "Arial", 16, True, False )

		self.clock = pygame.time.Clock( )
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
			self.player2 = entities.PlayerEntity( "red", ( 100, 100 ), "green-soldier.png" )
		elif self.id == 2:
			self.player1 = entities.PlayerEntity( "red", ( 100, 100 ) )
			self.player2 = entities.PlayerEntity( "blue", ( 1940, 1940 ), "green-soldier.png" )

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

		self.polygons = ( )

		self.viewport.follow( self.player1 )

		self.running = True
		self.scrollX = 4
		self.scrollY = 4

		self.delta = 0.0

		self.makeTerrain( )
		
		while self.running:
			self.game_loop( )

	def useData( self, data ):
		if data is None:
			return
		if data.pId != id:
			#print(data)
			self.player2.location = geometry.Vector( data.px, data.py )
			self.player2.set_facing( data.pf )
			if self.id == 2:
				self.flag1.set_facing( data.ff )
				self.flag2.updateScore( data.s )
				if data.fc:
					self.flag1.was_captured_by( self.player2 )
				else:
					self.flag1.release( )
			else:
				self.flag2.set_facing( data.ff )
				self.flag1.updateScore( data.s )
				if data.fc:
					self.flag2.was_captured_by( self.player2 )
				else:
					self.flag2.release( )
			#networkBullets.fromNetwork(data.bullets)
			for b in data.bullets:
				self.player2.gun.addBullet( ( b[0], b[1] ), ( b[2], b[3] ) )
			if data.hit:
				self.player1.was_hit( )

	def createBlock( self, x, y, w, h ):
		p = geometry.Terrain( [( x, y ), ( x + w, y ), ( x + w, y + h ), ( x, y + h )], self.world )
		self.world.add_terrain( p )

	def makeTerrain( self ):
		leftWall = geometry.Slope( [( 0, 0 ), ( 0, 2000 )] )
		self.world.add_terrain( leftWall )
		rightWall = geometry.Slope( [( 2000, 0 ), ( 2000, 2000 )] )
		self.world.add_terrain( rightWall )
		topWall = geometry.Slope( [( 0, 0 ), ( 2000, 0 )] )
		self.world.add_terrain( topWall )
		
		#bottomwall
		self.createBlock( 0, 2000, 2000, 50 )

		#top level
		p = geometry.Terrain( [( 1350, 350 ), ( 1500, 350 ), ( 1500, 250 )], self.world )
		self.world.add_terrain( p )
		p = geometry.Terrain( [( 700, 200 ), ( 1050, 350 ), ( 1050, 400 ), ( 700, 250 )], self.world )
		self.world.add_terrain( p )

		self.createBlock( 1700, 1900, 100, 100 )
		self.createBlock( 1900, 1800, 100, 100 )
		self.createBlock( 1500, 1800, 500, 20 )
		self.createBlock( 0, 200, 300, 60 )
		self.createBlock( 200, 0, 50, 80 )
		self.createBlock( 300, 150, 50, 50 )
		self.createBlock( 300, 200, 400, 50 )
		self.createBlock( 1050, 350, 850, 50 )
		self.createBlock( 1500, 250, 100, 100 )
		self.createBlock( 1800, 200, 150, 50 )
		self.createBlock( 1200, 125, 150, 50 )

		#second
		self.createBlock( 800, 500, 1300, 50 )
		self.createBlock( 800, 450, 75, 75 )
		self.createBlock( 0, 500, 600, 50 )
		self.createBlock( 700, 650, 100, 50 )

		self.createBlock( 0, 800, 1600, 60 )
		self.createBlock( 1700, 800, 400, 60 )
		self.createBlock( 400, 740, 50, 60 )
		self.createBlock( 600, 600, 100, 50 )
		self.createBlock( 1800, 750, 50, 50 )
		self.createBlock( 200, 700, 100, 50 )
		self.createBlock( 400, 750, 50, 50 )
		self.createBlock( 1800, 700, 100, 50 )
		self.createBlock( 1200, 700, 75, 40 )
		self.createBlock( 1000, 750, 50, 50 )
		self.createBlock( 850, 740, 100, 40 )
		self.createBlock( 150, 375, 200, 50 )

		self.createBlock( 0, 920, 250, 50 )
		self.createBlock( 300, 920, 400, 50 )
		self.createBlock( 780, 920, 1000, 50 )
		self.createBlock( 500, 890, 20, 30 )

		self.createBlock( 50, 1050, 1950, 30 )
		self.createBlock( 300, 1030, 20, 20 )
		self.createBlock( 600, 1020, 30, 30 )
		self.createBlock( 1200, 1030, 20, 50 )

		self.createBlock( 0, 1150, 500, 20 )
		self.createBlock( 550, 1150, 1500, 20 )
		self.createBlock( 300, 1130, 30, 20 )
		self.createBlock( 800, 1120, 50, 30 )
		self.createBlock( 1400, 1120, 20, 30 )

		self.createBlock( 0, 1300, 1950, 20 )
		self.createBlock( 200, 1220, 100, 20 )
		self.createBlock( 100, 1270, 30, 30 )
		self.createBlock( 500, 1220, 250, 20 )
		self.createBlock( 800, 1260, 40, 40 )
		self.createBlock( 1200, 1270, 30, 30 )
		self.createBlock( 1600, 1220, 60, 10 )

		self.createBlock( 0, 1500, 750, 20 )
		self.createBlock( 800, 1500, 1200, 20 )
		self.createBlock( 200, 1400, 120, 15 )
		self.createBlock( 470, 1420, 100, 15 )
		self.createBlock( 750, 1410, 86, 15 )
		self.createBlock( 1200, 1400, 130, 15 )
		self.createBlock( 1600, 1400, 80, 15 )
		self.createBlock( 100, 1450, 50, 50 )
		self.createBlock( 350, 1460, 40, 40 )
		self.createBlock( 940, 1480, 20, 20 )
		self.createBlock( 1300, 1450, 50, 50 )
		self.createBlock( 1700, 1470, 30, 30 )
		self.createBlock( 1800, 1400, 200, 20 )

		self.createBlock( 0, 1750, 300, 20 )
		self.createBlock( 350, 1750, 1000, 20 )
		self.createBlock( 1400, 1750, 600, 20 )
		self.createBlock( 200, 1730, 20, 20 )
		self.createBlock( 600, 1680, 150, 20 )
		self.createBlock( 1200, 1700, 50, 50 )
		self.createBlock( 1600, 1650, 100, 20 )
		self.createBlock( 1800, 1720, 30, 30 )
		self.createBlock( 750, 1600, 200, 20 )

		self.createBlock( 0, 1850, 600, 20 )
		self.createBlock( 300, 1840, 20, 20 )

	def handle_keys( self, keyEvent ):
		key = keyEvent.key

		if keyEvent.type == pygame.KEYDOWN:
			self.keys[key] = True

		if keyEvent.type == pygame.KEYUP:
			self.keys[key] = False

	def handle_events( self ):
		for event in pygame.event.get( ):
			if event.type == pygame.QUIT:
				self.client.kill( )
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
			self.player1.startJumping( )

		if self.keys[pygame.K_x]:
			self.player1.shoot( )
			self.keys[pygame.K_x] = False

		self.player1.move( self.delta )

	def game_loop( self ):
		self.delta = self.clock.tick( 30 ) #FPS
		self.handle_events( )
		self.do_logic( )
		self.send_data( )
		self.viewport.render( self.delta )
		self.networkBullets.draw( )
		self.window.screen.blit( self.helveticaFnt.render( "Blue Team Score: " + str( self.flag2.score ), True, ( 0, 0, 255 ), ( 0, 0, 0 ) ), ( 0, 0 ) )
		self.window.screen.blit( self.helveticaFnt.render( "Red Team Score: " + str( self.flag1.score ), True, ( 255, 0, 0 ), ( 0, 0, 0 ) ), ( 0, 18 ) )
		pygame.display.flip( )

if __name__ == "__main__":
	id = int ( input ( "id? " ) )
	#svrip = input ( "server ip? " )
	WeatheredStone = WeatheredStone( id, "192.168.56.1" )

