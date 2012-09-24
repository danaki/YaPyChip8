from pygame.locals import *

class Keyboard():
	keymap = {
		K_1: 0x1,
		K_2: 0x2,
		K_3: 0x3,
		K_4: 0xC,
		K_q: 0x4,
		K_w: 0x5,
		K_e: 0x6,
		K_r: 0xD,
		K_a: 0x7,
		K_s: 0x8,
		K_d: 0x9,
		K_f: 0xE,
		K_z: 0xA,
		K_x: 0x0,
		K_c: 0xB,
		K_v: 0xF
	}
	
	def translate(self, real_key):
		if real_key in self.keymap:
			return self.keymap[real_key]
		
		return None