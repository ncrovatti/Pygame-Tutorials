"""

MIT/X11 License

Copyright (c) 2009 Nicolas Crovatti.

Permission is hereby granted, free of charge, to any person obtaining a 
copy of this software and associated documentation files (the "Software"), 
to deal in the Software without restriction, including without limitation 
the rights to use, copy, modify, merge, publish, distribute, sublicense, 
and/or sell copies of the Software, and to permit persons to whom the Software 
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

Mounts & Clouds Brushes 	: http://javierzhx.deviantart.com/
Trees Brushes 						: http://deathoflight.deviantart.com/
Grass Brushes 						: http://archeleron.deviantart.com/
"""

import os 
import pygame
from pygame.locals import *
from random import randint
from gameobjects.vector2 import Vector2


RESOLUTION = (500, 400)

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
			
			# Animation 
			self._start 			= pygame.time.get_ticks()
			self._delay 			= 1000 / fps
			self._last_update = 0
			self._frame 			= 0
			self._images 			= images
			
			self.image 				= self._images[self._frame]
			
			# Movement
			self.location 		= (0,0)
			self.destination 	= (0,0)
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
					self.location = Vector2(0, y)
					x = 0
					
			# Blitting the image loop 
			if x - w < W:
				location = Vector2(x+w, y)
				screen.blit(self.image, location)
			
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
		clock 						= pygame.time.Clock()
		backgrounds				= []
		
		parallax_1 	= load_sliced_sprites(800, 200, 'parallax-1-800x200.png')
		parallax_2 	= load_sliced_sprites(800, 120, 'parallax-2-800x120.png')
		parallax_3 	= load_sliced_sprites(800, 200, 'parallax-3-800x200.png')
		parallax_4 	= load_sliced_sprites(800, 200, 'parallax-4-800x200.png')
		parallax_5 	= load_sliced_sprites(1600, 400, 'parallax-5-1600x400.png')
		
		prlx1	= Parallax(parallax_1, 60)
		prlx1.speed = 10.
		prlx1.location = (0, 0)
		prlx1.destination = Vector2(*(-parallax_1[0].get_rect().w, 0))
		backgrounds.append(prlx1)
		
	 	prlx2 = Parallax(parallax_2, 60)
		prlx2.speed = 40.
		prlx2.location = (0, 110)
		prlx2.destination = Vector2(*(-parallax_2[0].get_rect().w, 110))
		backgrounds.append(prlx2)
		
	 	prlx3 = Parallax(parallax_3, 60)
	 	prlx3.speed = 80.
	 	prlx3.location = (0, 60)
	 	prlx3.destination = Vector2(*(-parallax_3[0].get_rect().w, 60))
		backgrounds.append(prlx3)
		
		
	 	prlx4 = Parallax(parallax_4, 60)
	 	prlx4.speed = 120.
	 	prlx4.location = (0, 90)
	 	prlx4.destination = Vector2(*(-parallax_4[0].get_rect().w, 90))
		backgrounds.append(prlx4)
		
		prlx5 = Parallax(parallax_5, 60)
	 	prlx5.speed = 900.
	 	prlx5.location = (0, 0)
	 	prlx5.destination = Vector2(*(-parallax_5[0].get_rect().w, 0))
		backgrounds.append(prlx5)
		
		while True:
				for event in pygame.event.get():
						if event.type == QUIT:
								return
								
				screen.blit(background, (0, 0))
				time_passed = clock.tick(60)
				
				time_passed_seconds = time_passed / 1000.0
				
				for parallax in backgrounds:	
					parallax.process(time_passed_seconds)
					parallax.render(screen)
					
				pygame.display.update()


if __name__ == "__main__":
				run()
