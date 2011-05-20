'''
Created on Jun 24, 2010

@author: folz
'''

import math, pygame, sys
from pygame.locals import *
from engine import *

class BulletEntity( entity.CollidableEntity ):
	'''
	A Bullet is something you shoot. It is handled by a BulletManager
	'''

	MAX_SPEED_X = 5
	MAX_SPEED_Y = 5

	def __init__( self, location, velocity, facing ):
		'''
		Constructor
		'''
		entity.Entity.__init__( self, "bullet.png", location, velocity )
		if facing == "left":
			self.image = pygame.transform.flip( self.image, True, False )
		self.used = False
		self.sent = False
		self.rect = pygame.Rect( self.location.x, self.location.y, self.get_width(), self.get_height() )

	def setBulletManagerCallback( self, bulletmanager ):
		self.bulletmanager = bulletmanager

	def networkBullet( self ):
		p2 = self.world.get_entity_by_name( "player2" )
		self.bounding_poly = geometry.Rect( self.location.x, self.location.y, self.get_width(), self.get_height() )
		mtd = p2.bounding_poly.collide( self.bounding_poly )
		if mtd != False:
			p2.take_hit()
			self.used = True

	def move( self, delta ):
		if( self.velocity.x == 0 ):
			return

		self.networkBullet()

		if self.used:
			self.bulletmanager.removeBullet( self )
			del self
			return

		if self.velocity.x > self.MAX_SPEED_X:
			self.velocity.x = self.MAX_SPEED_X
		if self.velocity.x < -self.MAX_SPEED_X:
			self.velocity.x = -self.MAX_SPEED_X
		if self.velocity.y > self.MAX_SPEED_Y:
			self.velocity.y = self.MAX_SPEED_Y
		if self.velocity.y < -self.MAX_SPEED_Y:
			self.velocity.y = -self.MAX_SPEED_Y

		self.location.x += self.velocity.x * ( entity.Entity.PIXELSPERVECTOR / delta )
		self.location.y += self.velocity.y * ( entity.Entity.PIXELSPERVECTOR / delta )

		self.rect = pygame.Rect( self.location.x, self.location.y, self.get_width(), self.get_height() )

		if self.location.x < 0 or self.location.x > self.world.get_width() or self.location.y < 0 or self.location.y > self.world.get_height():
			self.bulletmanager.bullets.remove( self )

	def check_collisions( self ):
		if not self.used:
			self.bounding_poly = geometry.Rect( self.location.x, self.location.y, self.get_width(), self.get_height() )
			for terrain in self.world.get_terrain():
				mtd = self.bounding_poly.collide( terrain )
				if mtd != False:
					self.used = True
		else:
			self.bulletmanager.removeBullet( self )
			del self

class FlagEntity( entity.Entity ):

	def __init__( self, team, location=geometry.Vector( 0, 0 ), velocity=geometry.Vector( 0, 0 ) ):
		'''
		Constructor
		'''
		self.start = geometry.Vector( location[0], location[1] )
		entity.Entity.__init__( self, "flag_%s.png" % team, location, velocity )
		self.facing = "right"
		self.wasFacing = self.facing
		self.team = team
		self.captured = False
		self.capturer = None
		self.scale = 1
		self.score = 0

	def set_facing( self, newFacing ):
		self.wasFacing = self.facing
		self.facing = newFacing

	def was_captured_by( self, entity ):
		self.captured = True
		self.capturer = entity
		self.capturer.flag1 = self

	def release( self ):
		if self.capturer is not None:
			self.capturer.flag1 = None
			self.capturer.hasFlag = False
		self.facing = "right"
		self.captured = False
		self.capturer = None
		self.location = self.start.copy()

	def move( self, delta ):
		if self.captured and self.capturer != None:
			pass
		self.checkCollisions()

	def updateScore( self, score ):
		self.score = score

	def checkCollisions( self ):
		self.bounding_poly = geometry.Rect( self.location.x, self.location.y, self.get_width(), self.get_height() )
		if not self.captured:
			for player in self.world.get_entities_by_attribute( "player" ):
				if player.team != self.team:
					mtd = self.bounding_poly.collide( player.bounding_poly )
					if mtd != False:
						self.was_captured_by( player )
						player.hasFlag = True
						print( "captured" )
				else:
					mtd = self.bounding_poly.collide( player.bounding_poly )
					if mtd != False and player.hasFlag and self.captured == False:
						player.flag1.release()
						self.score += 1
						print( "SCORED" )


		else:
			if self.capturer.facing == "left":
				self.location.x = self.capturer.location.x + self.capturer.get_width() / 2
				self.location.y = self.capturer.location.y
			elif self.capturer.facing == "right":
				self.location.x = self.capturer.location.x - self.capturer.get_width() / 2
				self.location.y = self.capturer.location.y

		self.rect = pygame.Rect( self.bounding_poly.realPoints[0][0], self.bounding_poly.realPoints[0][1], self.bounding_poly.width, self.bounding_poly.height )

	def draw( self ):
		if self.facing == "right" and self.scale == -1:
			self.image = pygame.transform.flip( self.image, True, False )
			self.scale = 1
		elif self.facing == "left" and self.scale == 1:
			self.image = pygame.transform.flip( self.image, True, False )
			self.scale = -1

		entity.Entity.draw( self )
		self.wasFacing = self.facing

class PlayerEntity( entity.CollidableEntity ):
	'''
	classdocs
	'''

	MAXXSPEED = 4
	MAXUPSPEED = 4
	MAXDOWNSPEED = 4

	def __init__( self, team, location=geometry.Vector( 0, 0 ), image="rocketplok.gif", velocity=geometry.Vector( 0, 0 ) ):
		'''
		Constructor
		'''
		entity.Entity.__init__( self, image, location, velocity )
		self.moving = False
		self.startLocation = location
		self.wasFacing = "right"
		self.facing = "right"
		self.jumping = True
		self.shooting = False
		self.gun = None
		self.team = team
		self.hasFlag = False
		self.flag1 = None
		self.hit = False
		self.health = 10
		self.death_cooldown = 200
		self.scale = 1

	def reset( self ):
		self.moving = False
		self.wasFacing = "right"
		self.facing = "right"
		self.jumping = True
		self.shooting = False
		self.hit = False
		self.health = 10
		self.location = geometry.Vector( self.startLocation[0], self.startLocation[1] )
		self.death_cooldown = 0
		self.rect = pygame.Rect( self.bounding_poly.realPoints[0][0], self.bounding_poly.realPoints[0][1], self.bounding_poly.width, self.bounding_poly.height )

	def set_facing( self, newFace ):
		self.wasFacing = self.facing
		self.facing = newFace

	def was_hit( self ):
		if self.hasFlag:
			self.hasFlag = False
			self.flag1.release()
		self.health -= 1
		if self.health == 0:
			self.reset()

	def take_hit( self ):
		if self.hasFlag:
			self.hasFlag = False
			self.flag1.release()
		self.hit = True

	def move_left( self ):
		self.moving = True
		self.facing = "left"

	def move_right( self ):
		self.moving = True
		self.facing = "right"

	def try_to_fly( self ):
		self.velocity += geometry.Vector( 0, -1.5 )

	def add_gun( self, gun ):
		self.gun = gun

	def shoot( self ):
		if not self.death_cooldown == 200: return
		offset = 0
		if self.facing == "left":
			xvel = -20 + self.velocity.x * .2
			offset = -self.get_width() - 1
		elif self.facing == "right":
			xvel = 20 + self.velocity.x * .2
			offset = self.get_width() + 1
		self.gun.addBullet( ( self.location.x + offset, self.location.y + self.get_height() / 2 ), ( xvel, 0 ), self.facing ) # TODO get velocity based on user mouse position

	def move( self, delta ):
		if not self.death_cooldown == 200:
			self.death_cooldown += 1
			return

		# If the entity has a non-zero velocity but we're not moving, slow it down 
		if ( abs( self.velocity.x ) > .001 and not self.moving ):
			self.velocity.x *= .5

		self.velocity += self.world.gravity

		if self.velocity.x > self.MAXXSPEED:
			self.velocity.x = self.MAXXSPEED
		if self.velocity.x < -self.MAXXSPEED:
			self.velocity.x = -self.MAXXSPEED
		if self.velocity.y > self.MAXUPSPEED:
			self.velocity.y = self.MAXUPSPEED
		if self.velocity.y < -self.MAXDOWNSPEED:
			self.velocity.y = -self.MAXDOWNSPEED

		self.location.x += self.velocity.x * ( PlayerEntity.PIXELSPERVECTOR / delta )
		self.location.y += self.velocity.y * ( PlayerEntity.PIXELSPERVECTOR / delta )

		print( "Velocity: {0}".format( self.velocity ) )

		self.gun.shoot( delta )



	def check_collisions( self ):
		if not self.death_cooldown == 200:
			return
		self.bounding_poly = geometry.Rect( self.location.x, self.location.y, self.get_width(), self.get_height() )
		for terrain in self.world.get_terrain():
			mtd = self.bounding_poly.collide( terrain )

			if mtd != False: # if we're colliding with the terrain
				self.location += mtd # adjust our position so that we're not colliding anymore

				if self.bounding_poly.isAbove == True: # if we're above whatever we're colliding with
					self.velocity.y = 0
				elif self.bounding_poly.isAbove == False: # if we're below whatever we're colliding with
					self.velocity.y = 0
				elif self.bounding_poly.isAbove == None: # this shouldn't happen, but sometimes it comes back neither true nor false
					pass

				elif self.bounding_poly.isLeft == True: # if we're to the left of whatever we're colliding with
					self.velocity.x = 0
				elif self.bounding_poly.isLeft == False: #if we're to the right of whatever we're colliding with
					self.velocity.x = 0
				elif self.bounding_poly.isLeft == None: # this shouldn't happen, but sometimes it comes back neither true nor false
					pass
			else: # we're not colliding with anything
				pass#self.jumping = True

		self.rect = pygame.Rect( self.bounding_poly.realPoints[0][0], self.bounding_poly.realPoints[0][1], self.bounding_poly.width, self.bounding_poly.height )
		self.wasVelocity = self.velocity

	def draw( self ):
		if self.facing == "right" and self.scale == -1:
			self.image = pygame.transform.flip( self.image, True, False )
			self.scale = 1
		elif self.facing == "left" and self.scale == 1:
			self.image = pygame.transform.flip( self.image, True, False )
			self.scale = -1

		entity.Entity.draw( self )
		self.wasFacing = self.facing

