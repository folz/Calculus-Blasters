'''
Created on Jun 24, 2010

@author: folz
'''

import math, pygame, sys, random
from pygame.locals import *
from engine import *

def frac( delta ):
	return delta / 1000

def ppv( delta ):
	return entity.Entity.PIXELSPERVECTOR / delta

class AsteroidEntity( entity.Entity ):
	def __init__( self ):
		return

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
		if self.team == "red":
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
				break

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

