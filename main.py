import sys
import pygame
from pygame.locals import *
from chip8.cpu import CPU
from chip8.video import Video
from chip8.keyboard import Keyboard

def main(rom_file):
	pygame.init()
	#screen = pygame.display.set_mode((64, 64))
	video = Video()
	screen = pygame.display.set_mode(video.get_mode())
	#pygame.mouse.set_visible(0)
	pygame.display.update()
	
	surface = pygame.Surface(screen.get_size())
	surface = surface.convert()
	screen.blit(surface, (0, 0))
	video.set_surface(surface)
	
	pygame.display.flip()

	keyboard = Keyboard()
	computer = CPU(video)
	fd = open(rom_file, "rb")
	computer.load(fd.read())
	
	CLOCK_HZ = 10000 # 4194304
	TIMER_HZ = 30
	CPU_CLOCK_EVENT = USEREVENT + 1
	TIMER_CLOCK_EVENT = CPU_CLOCK_EVENT + 1

	#pygame.time.set_timer(CPU_CLOCK_EVENT, 1000 / CLOCK_HZ)
	#pygame.time.set_timer(TIMER_CLOCK_EVENT, int(1000 / TIMER_HZ))
	pygame.time.set_timer(TIMER_CLOCK_EVENT, 100)
	
	i = 0
	while True:

		event = pygame.event.poll()
		
		if event.type == pygame.QUIT:
			sys.exit()
		#elif event.type == CPU_CLOCK_EVENT:
		#	computer.tick()
		elif event.type == TIMER_CLOCK_EVENT:
			computer.timer()
		elif event.type == pygame.KEYUP:
			key = keyboard.translate(event.key)
			if not key is None: 
				computer.key_up(key)
		elif event.type == pygame.KEYDOWN:
			key = keyboard.translate(event.key)
			if not key is None: 
				computer.key_down(key)
				
		i += 1
		#print "timer " + str(i)
		computer.timer()
		computer.tick()
		#pygame.time.wait(1000 / CLOCK_HZ)
		
		screen.blit(surface, (0, 0))
		if not video.dirty_rect is None: 
			pygame.display.update(video.dirty_rect)

		video.dirty_rect = None

if __name__ == '__main__':
	if len(sys.argv) != 2:
		print "Usage: main.py [rom_file]"
	else:
		main(sys.argv[1])
