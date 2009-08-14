import os 
import pygame
from pygame.locals import *
from gameobjects.vector2 import Vector2
from random import randint
from time import sleep

RESOLUTION = (300, 300)

pygame.init()
screen 				= pygame.display.set_mode(RESOLUTION)
background 		= pygame.Surface(RESOLUTION)
default_font 	= pygame.font.get_default_font()
font 					= pygame.font.SysFont(default_font, 20, False)	

background.fill((255,255,255))
screen.blit(background, (0, 0))
		

class AnimatedSprite(pygame.sprite.Sprite):
		def __init__(self, images, fps = 10):
			pygame.sprite.Sprite.__init__(self)
			self._images 			= images

			# Track the time we started, and the time between updates.
			# Then we can figure out when we have to switch the image.
			self._start 			= pygame.time.get_ticks()
			self._delay 			= 1000 / fps
			self._last_update = 0
			self._frame 			= 0
			self.image 				= self._images[self._frame]
			# Defining a default location on screen for our sprite
			w, h 							= RESOLUTION
			self.location 		= (randint(0,w),randint(0,h))
			
		def update(self, t):
			# Note that this doesn't work if it's been more that self._delay
			# time between calls to update(); we only update the image once
			# then, but it really should be updated twice.
			if t - self._last_update > self._delay:
				self._frame += 1
				# Animation Finished, choosing a new location
				if self._frame >= len(self._images):
					self._frame = 0
					w, h 							= RESOLUTION
					x, y							= self.image.get_size()
					self.location 		= (randint(0+x,w-x),randint(0+y,h-y))
										
				self.image = self._images[self._frame]
				self._last_update = t
            
		def render(self, screen):
			self.update(pygame.time.get_ticks())
			screen.blit(self.image, self.location)

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
		explosion_images 	= load_sliced_sprites(20, 20, 'explosion-sprite.png')
		clock 						= pygame.time.Clock()
		
		sprites						= []
		sprites.append(AnimatedSprite(explosion_images, 15))
	 	
		while True:
				for event in pygame.event.get():
						if event.type == QUIT:
								return
						
						if event.type == MOUSEBUTTONDOWN:
								explosion = AnimatedSprite(explosion_images, 15)
								explosion.location = event.pos
								sprites.append(explosion)
				
				screen.blit(background, (0, 0))
				time_passed = clock.tick(30)

				for sprite in sprites:
					sprite.render(screen)
					
				instructions = font.render("Click to add explosions", True, (0,0,0))
				screen.blit(instructions, (0, 0))
				pygame.display.update()


if __name__ == "__main__":
				run()
