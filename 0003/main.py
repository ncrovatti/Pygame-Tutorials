"""

MIT/X11 License

Copyright (c) 2009 Nicolas Crovatti.

Permission is hereby granted, free of charge, to any person obtaining a 
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation 
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and / or sell copies of the Software, and to permit persons to whom the Software 
is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in 
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR 
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL 
THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR 
OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR 
OTHER DEALINGS IN THE SOFTWARE.



Additionnal Copyrights:

Clouds Brushes 	: http://javierzhx.deviantart.com/
Fighter 				: http://prinzeugn.deviantart.com

"""

import os 
import pygame
from pygame.locals import *
from random import randint
from gameobjects.vector2 import Vector2

pygame.init()

RESOLUTION 		= Vector2(800, 600)
W, H 					=	RESOLUTION

screen 				= pygame.display.set_mode(RESOLUTION)
background 		= pygame.Surface(RESOLUTION)
default_font 	= pygame.font.get_default_font()
font 					= pygame.font.SysFont(default_font, 20, False)	

background.fill((255,255,255))
screen.blit(background, (0, 0))

class AnimatedSprite(pygame.sprite.Sprite):
		def __init__(self, images, fps = 10):
			pygame.sprite.Sprite.__init__(self)
			
			# Animation 
			self._start 			= pygame.time.get_ticks()
			self._delay 			= 1000 / fps
			self._last_update = 0
			self._frame 			= 0
			self._images 			= images
			
			self.image 				= self._images[self._frame]
			
			# Movement
			self.location 		= Vector2(0,0)
			self.destination 	= Vector2(0,0)
			self.heading			= None
			self.speed				= 0.
			
			
			
		def process(self, t):
			if self.speed > 0. and self.location != self.destination:
					destination 						= self.destination - self.location
					distance 								= destination.get_length()
					self.heading 						= destination.get_normalized()
					most_accurate_distance 	= min(distance, t * self.speed)
					self.location 					+= most_accurate_distance * self.heading
					
		def update(self, t):
			
			# Note that this doesn't work if it's been more that self._delay
			# time between calls to update(); we only update the image once
			# then, but it really should be updated twice.
			if t - self._last_update > self._delay:
				self._frame += 1
				if self._frame >= len(self._images):
					self._frame = 0
					
				self.image = self._images[self._frame]
				self._last_update = t
            
		def render(self, screen):
			screen.blit(self.image, self.location)

# Fire And forget 
class Bullet(AnimatedSprite):
	def __init__(self, world, x_dest , y_dest, fps = 60):
		self.images = load_sliced_sprites(12, 	9, 		'bullet-1-12x9.png')
		AnimatedSprite.__init__(self, self.images, 60)
		self.speed 		= 2000.
		self.x 				= x_dest
		self.y 				= y_dest
		self.id 			= None
		self.world		= world
		
	def fire(self):
		self.world.add_entity(self)
		self.destination = Vector2(*(W, self.y))
		
	def update(self, interval):
		if self.location >= self.destination:
			# Helping the garbage collector
			self.world.remove_entity(self)
		


class Fighter(AnimatedSprite):
		def __init__(self, images, world, fps = 60):
				AnimatedSprite.__init__(self, images, fps)
				self.speed 					= 600.	
				self.default_speed	= self.speed
				self.location 			= Vector2(*(100, RESOLUTION[1]/2))
				self.destination 		= self.location
				self.stoping				= False
				self.world					= world
				self.slowing_factor = 10.
				
				# Forward movement image - default
				self.image 					= self._images[1]
				
				self.last_shot			= 0
				self.fire_delay			= 0.008
				
		def event_handler(self, event):
			if event.type == KEYUP:
				self.stop(event.key)	
			
			if event.type == KEYDOWN:
				if event.key == K_UP or \
						event.key == K_DOWN or \
						event.key == K_LEFT or \
						event.key == K_RIGHT:
					self.move(event.key)	
				
		

		def update(self, t):
			# Slowing effect
			if self.stoping is True:
				self.speed -= self.speed/self.slowing_factor

			if self.stoping is False:
				self.speed = self.default_speed
		
		def fire(self):
			now = pygame.time.get_ticks() 
			if (now - self.last_shot) / 1000.0 < self.fire_delay:
				return
			
			x, y 						= self.location
			w, h 						= self.image.get_size()
			weapon 					= Bullet(self.world, x, y, 100)
			weapon.location = Vector2(*(x+w/2, y+h/2))
			weapon.fire()
			self.last_shot = pygame.time.get_ticks()
		
		def move(self, key):
			# Overriden to make use differently of the image's slices
			self.stoping = False
			W,H = RESOLUTION - self.image.get_size()
			x,y = self.location
			
			if key == K_UP:
				self.image = self._images[0]
				self.destination = Vector2(*(x,0))
				
			elif key == K_DOWN:
				self.image = self._images[2]
				self.destination = Vector2(*(x,H))
				
			elif key == K_LEFT: 
				self.destination = Vector2(*(0,y))
					
			elif key == K_RIGHT:
				self.destination = Vector2(*(W,y))		 
			
		def stop(self, key):
			W,H 				= RESOLUTION - self.image.get_size()
			x, y 				= self.destination
			xa,ya 			= self.location
			w,h 				=	self.image.get_size()
			self.image 	= self._images[1]	
			
			
			# Stopping Y Axis Movements
			if key == K_UP:
				self.stoping = True
				self.destination = Vector2(*(x, max(ya-h*self.slowing_factor, 0)))
				
			if key == K_DOWN: 
				self.stoping = True
				self.destination = Vector2(*(x, min(ya+h*self.slowing_factor, H)))
			
			# Stopping X Axis Movements	
			if key == K_LEFT: 
				self.stoping = True
				self.destination = Vector2(*(max(xa-w*self.slowing_factor, 0), y))
				
			if key == K_RIGHT:
				self.stoping = True
				self.destination = Vector2(*(min(xa+w*self.slowing_factor, W), y))
				

class Parallax(AnimatedSprite):
		def __init__(self, images, fps = 30):
				AnimatedSprite.__init__(self, images, fps)
				
		def render(self, screen):
			# Overridding the default render method
			w,h = self.image.get_size()
			x,y = self.location
			W,H = RESOLUTION
			
			# Reseting original image location 
			if abs(x) == w:
					self.location = Vector2(*(0, y))
					x = 0
					
			# Blitting the image loop 
			if x - w < W:
				location = Vector2(x+w+1, y)
				screen.blit(self.image, location)
			
			screen.blit(self.image, self.location)		

class World(object):
		
		def __init__(self):
			self.entities = {}
			self.entity_id = 0
			
		def add_entity(self, entity):
				self.entities[self.entity_id] = entity
				entity.id = self.entity_id
				self.entity_id += 1
				
		def remove_entity(self, entity):
				del self.entities[entity.id]
				entity = None
				
		def process(self, time_passed):					
			time_passed_seconds = time_passed / 1000.0				
			for id in self.entities.keys():
				entity = self.get(id)
				entity.process(time_passed_seconds)
						
		def render(self, surface):
			for id in self.entities.keys():
				entity = self.get(id)
				entity.render(surface)
					
		def update(self, time_passed):
			for id in self.entities.keys():
				entity = self.get(id)
				entity.update(time_passed)
				
		def get(self, entity_id):
			if entity_id in self.entities:
					return self.entities[entity_id]
			else:
					return None
								
def load_sliced_sprites(w, h, filename):
    '''
    Specs :
    	Master can be any height.
    	Sprites frames width must be the same width
    	Master width must be len(frames)*frame.width
    '''
    images = []
    master_image = pygame.image.load(os.path.join('', filename)).convert_alpha()

    master_width, master_height = master_image.get_size()
    for i in xrange(int(master_width/w)):
    	images.append(master_image.subsurface((i*w,0,w,h)))
    return images



def run():
		pygame.key.set_repeat(3)
		clock 						= pygame.time.Clock()		
		world							= World()
		
		parallax_1 				= load_sliced_sprites(800, 	800, 	'clouds-1-800x800.png')
		parallax_2 				= load_sliced_sprites(800, 	800, 	'clouds-2-800x800.png')
		fighter		 				= load_sliced_sprites(64, 	51, 	'fighter-1-192x51.png')
		keys_images 			= load_sliced_sprites(32, 	32, 	'keys-160x32.png')
		# up, right, down, left
						
		prlx1							= Parallax(parallax_1, 60)
		prlx1.speed 			= 10.
		prlx1.location 		= (0, 0)
		prlx1.destination = Vector2(*(-parallax_1[0].get_rect().w, 0))
		
		
	 	prlx2 						= Parallax(parallax_2, 60)
		prlx2.speed 			= 40.
		prlx2.location 		= (0, 0)
		prlx2.destination = Vector2(*(-parallax_2[0].get_rect().w, 0))
		
		fghtr 						= Fighter(fighter, world, 60)

		key 							= Fighter(keys_images, world, 60)
		key.speed 				= 0.
		key.location 			= (RESOLUTION[0]/2, RESOLUTION[1]/2)
		key.image					= keys_images[0]
		key.destination 	= key.location
		

		world.add_entity(prlx2)
		world.add_entity(prlx1)
		world.add_entity(fghtr)
		world.add_entity(key)
		
		while True:
				"""
					for event in pygame.event.get():
	 						
	 	 		"""
 	 			event = pygame.event.poll()			
				if event.type == QUIT:
					return
				
				fghtr.event_handler(event)
								
				time_passed = clock.tick(60)
				time_passed_seconds = time_passed / 1000.0
				
				keys = pygame.key.get_pressed()
				if keys[K_LCTRL]:
					fghtr.fire()
				
				print world.entity_id
				background.fill((20,20,100))
				screen.blit(background, (0, 0))
				
				world.process(time_passed)
				world.update(pygame.time.get_ticks())
				world.render(screen)
				
				pygame.display.flip()


if __name__ == "__main__":
				run()
   
