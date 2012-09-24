from pygame import Color, Rect
import pygame

class Video():
	def __init__(self):
		self.surface = None
		self.width = 64
		self.height = 32
		self.ram = [[False for col in range(self.width)] \
			for row in range(self.height)]
		self.pixel_size = 4
		self.dirty_rect = None

	def set_surface(self, surface):
		self.surface = surface

	def get_mode(self):
		return self.width * self.pixel_size, self.height * self.pixel_size

	def clear(self):
		for y in range(self.height):
			for x in range(self.width):
				self.ram[y][x] = False

	def set_pixel(self, x, y, is_white):
		self.ram[y][x] = is_white

		rx = x * self.pixel_size
		ry = y * self.pixel_size

		pygame.draw.rect(self.surface, Color(0xFFFFFF) if is_white else Color(0x0),
            Rect(rx, ry, self.pixel_size, self.pixel_size))
		self.dirty_rect = Rect(rx, ry, self.pixel_size, self.pixel_size)

	def get_pixel(self, x, y):
		return self.ram[y][x]
