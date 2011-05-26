'''
Created on Jun 24, 2010

@author: folz
'''

import math, pygame, sys
from pygame.locals import *
from engine import *

def frac( delta ):
	return delta / 1000

def ppv( delta ):
	return entity.Entity.PIXELSPERVECTOR / delta

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
			self.bulletmanager.remove_bullet( self )
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

	def check_collisions( self, delta ):
		if not self.used:
			self.bounding_poly = geometry.Rect( self.location.x, self.location.y, self.get_width(), self.get_height() )
			for terrain in self.world.get_terrain():
				mtd = self.bounding_poly.collide( terrain )
				if mtd != False:
					self.used = True
		else:
			self.bulletmanager.remove_bullet( self )
			del self

class FlagEntity( entity.CollidableEntity ):

	def __init__( self, team, location=geometry.Vector( 0, 0 ), velocity=geometry.Vector( 0, 0 ) ):
		'''
		Constructor
		'''
		self.start = geometry.Vector( location[0], location[1] )
		entity.Entity.__init__( self, "flag_%s.png" % team, location, velocity )
		self.facing = "right"
		self.was_facing = self.facing
		self.team = team
		self.captured = False
		self.capturer = None
		self.scale = 1
		self.score = 0

	def set_facing( self, newFacing ):
		self.was_facing = self.facing
		self.facing = newFacing

	def was_captured_by( self, entity ):
		self.captured = True
		self.capturer = entity
		self.capturer.flag1 = self

	def release( self ):
		if self.capturer is not None:
			self.capturer.flag1 = None
			self.capturer.has_flag = False
		self.facing = "right"
		self.captured = False
		self.capturer = None
		self.location = self.start.copy()

	def move( self, delta ):
		if self.captured and self.capturer != None:
			pass

	def update_score( self, score ):
		self.score = score

	def check_collisions( self, delta ):
		self.bounding_poly = geometry.Rect( self.location.x, self.location.y, self.get_width(), self.get_height() )
		if not self.captured:
			for player in self.world.get_entities_by_attribute( "player" ):
				if player.team != self.team:
					mtd = self.bounding_poly.collide( player.bounding_poly )
					if mtd != False:
						self.was_captured_by( player )
						player.has_flag = True
						print( "captured" )
				else:
					mtd = self.bounding_poly.collide( player.bounding_poly )
					if mtd != False and player.has_flag and self.captured == False:
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

		self.rect = pygame.Rect( self.bounding_poly.real_points[0][0], self.bounding_poly.real_points[0][1], self.bounding_poly.width, self.bounding_poly.height )

	def draw( self ):
		if self.facing == "right" and self.scale == -1:
			self.image = pygame.transform.flip( self.image, True, False )
			self.scale = 1
		elif self.facing == "left" and self.scale == 1:
			self.image = pygame.transform.flip( self.image, True, False )
			self.scale = -1

		entity.Entity.draw( self )
		self.was_facing = self.facing

class PlayerEntity( entity.CollidableEntity ):
	'''
	classdocs
	'''

	SPEED = 4.9

	def __init__( self, team, location=geometry.Vector( 0, 0 ), image="rocketplok.gif", velocity=geometry.Vector( 0, 0 ) ):
		'''
		Constructor
		'''
		entity.Entity.__init__( self, image, location, velocity )
		self.moving = False
		self.flying = False
		self.shooting = False
		self.startLocation = location
		self.was_facing = "right"
		self.facing = "right"
		self.gun = None
		self.team = team
		self.has_flag = False
		self.flag1 = None
		self.hit = False
		self.health = 10
		self.death_cooldown = 200
		self.scale = 1

	def reset( self ):
		self.moving = False
		self.flying = True
		self.shooting = False
		self.was_facing = "right"
		self.facing = "right"
		self.hit = False
		self.health = 10
		self.location = geometry.Vector( self.startLocation[0], self.startLocation[1] )
		self.death_cooldown = 0
		self.rect = pygame.Rect( self.bounding_poly.real_points[0][0], self.bounding_poly.real_points[0][1], self.bounding_poly.width, self.bounding_poly.height )

	def set_facing( self, newFace ):
		self.was_facing = self.facing
		self.facing = newFace

	def was_hit( self ):
		if self.has_flag:
			self.has_flag = False
			self.flag1.release()
		self.health -= 1
		if self.health == 0:
			self.reset()

	def take_hit( self ):
		if self.has_flag:
			self.has_flag = False
			self.flag1.release()
		self.hit = True

	def move_left( self ):
		self.moving = True
		self.facing = "left"

	def move_right( self ):
		self.moving = True
		self.facing = "right"

	def stop_moving( self ):
		self.moving = False

	def jump( self ):
		self.flying = True

	def stop_jumping( self ):
		self.flying = False

	def add_gun( self, gun ):
		self.gun = gun

	def debug( self, prnt ):
		return
		if self.team == "blue":
			print( prnt )

	def shoot( self ):
		if not self.death_cooldown == 200:
			return

		offset = 0
		if self.facing == "left":
			xvel = -BulletEntity.MAX_SPEED_X + self.velocity.x * .2
			offset = -self.get_width() - 1
		elif self.facing == "right":
			xvel = BulletEntity.MAX_SPEED_X + self.velocity.x * .2
			offset = self.get_width() + 1
		self.gun.add_bullet( ( self.location.x + offset, self.location.y + self.get_height() / 2 ), ( xvel, 0 ), self.facing ) # TODO get velocity based on user mouse position

	def move( self, delta ):
		if not self.death_cooldown == 200:
			self.death_cooldown += 1
			return

		# If we're moving left or right, find out which direction and how far
		if self.moving:
			self.velocity += geometry.Vector(
											- self.SPEED if self.facing == "left" else self.SPEED,
											0 ) * frac( delta )

		# If we're trying to fly
		if self.flying:
			self.velocity += geometry.Vector( 0, -3 * self.SPEED ) * frac( delta )

		self.velocity += self.world.gravity * frac( delta )

		if self.velocity.x > self.SPEED:
			self.velocity.x = self.SPEED
		if self.velocity.x < -self.SPEED:
			self.velocity.x = -self.SPEED
		if self.velocity.y > self.SPEED:
			self.velocity.y = self.SPEED
		if self.velocity.y < -self.SPEED:
			self.velocity.y = -self.SPEED

		self.debug( "\n" + str( self.velocity ) )

		self.location.x += self.velocity.x * ppv( delta )
		self.location.y += self.velocity.y * ppv( delta )

		#self.gun.shoot( delta )

	def check_collisions( self, delta ):
		if not self.death_cooldown == 200:
			return

		self.bounding_poly = geometry.Rect( self.location.x, self.location.y, self.get_width(), self.get_height() )

		standing_on_something = False

		for terrain in self.world.get_terrain():
			if terrain.is_on_screen():
				mtd = self.bounding_poly.collide( terrain )
			else:
				continue

			if mtd != False: # If we're colliding with this terrain
				self.location += mtd # adjust our position so that we're not colliding anymore

				if self.bounding_poly.isAbove == True: # if we're above whatever we're colliding with
					standing_on_something = True
					self.velocity.y = 0
				elif self.bounding_poly.isAbove == False: # if we're below whatever we're colliding with
					self.velocity.y = 0

				elif self.bounding_poly.isLeft == True: # if we're to the left of whatever we're colliding with
					self.velocity.x = 0
				elif self.bounding_poly.isLeft == False: #if we're to the right of whatever we're colliding with
					self.velocity.x = 0

		if standing_on_something and not self.moving:
			# If the entity has a non-zero velocity but we're not moving, slow it down
			if self.velocity.x < 0:
				if self.velocity.x > PlayerEntity.SPEED * frac( delta ):
					self.velocity += geometry.Vector( self.SPEED, 0 ) * frac( delta )
				else:
					self.velocity.x = 0
			elif self.velocity.x > 0:
				if self.velocity.x < -PlayerEntity.SPEED * frac( delta ):
					self.velocity += geometry.Vector( -self.SPEED, 0 ) * frac( delta )
				else:
					self.velocity.x = 0


		self.debug( "Velocity: {0}; MTD: {1}".format( self.velocity, mtd ) )

		self.rect = pygame.Rect( self.bounding_poly.real_points[0][0], self.bounding_poly.real_points[0][1], self.bounding_poly.width, self.bounding_poly.height )
		self.wasVelocity = self.velocity

	def draw( self ):
		if self.facing == "right" and self.scale == -1:
			self.image = pygame.transform.flip( self.image, True, False )
			self.scale = 1
		elif self.facing == "left" and self.scale == 1:
			self.image = pygame.transform.flip( self.image, True, False )
			self.scale = -1

		entity.Entity.draw( self )
		self.was_facing = self.facing

class AIEntity(CollidableEntity):
	STEP = 5

	def __init__(self, team, **kwargs):
		self.direction = True
		location = geometry.Vector(
			random.randint(0, self.world.get_width()),
			random.randint(0, self.world.get_height())
		)
		PlayerEntity.__init__(self, team, location=location, kwargs)

	def move(self, delta):
		step = STEP * ppv(delta)
		if self.location.x == 0:
			self.direction = True # go right
		elif self.location.x == self.world.get_width():
			self.direction = False # go left
		self.location.x += step * (1 if self.direction else -1)
		self.location.y += step

