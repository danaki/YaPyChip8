import re
import math
import random

class CPU():
	PROGRAM_BASE = 0x200
	FONTSET_BASE = 0x050

	fontset = (
		0xF0, 0x90, 0x90, 0x90, 0xF0, # 0
		0x20, 0x60, 0x20, 0x20, 0x70, # 1
		0xF0, 0x10, 0xF0, 0x80, 0xF0, # 2
		0xF0, 0x10, 0xF0, 0x10, 0xF0, # 3
		0x90, 0x90, 0xF0, 0x10, 0x10, # 4
		0xF0, 0x80, 0xF0, 0x10, 0xF0, # 5
		0xF0, 0x80, 0xF0, 0x90, 0xF0, # 6
		0xF0, 0x10, 0x20, 0x40, 0x40, # 7
		0xF0, 0x90, 0xF0, 0x90, 0xF0, # 8
		0xF0, 0x90, 0xF0, 0x10, 0xF0, # 9
		0xF0, 0x90, 0xF0, 0x90, 0x90, # A
		0xE0, 0x90, 0xE0, 0x90, 0xE0, # B
		0xF0, 0x80, 0x80, 0x80, 0xF0, # C
		0xE0, 0x90, 0x90, 0x90, 0xE0, # D
		0xF0, 0x80, 0xF0, 0x80, 0xF0, # E
		0xF0, 0x80, 0xF0, 0x80, 0x80  # F
	)

	def __init__(self, video):
		self.video = video

		self.opcodes = {
			'0nnn': self.SYS_addr,
			'00E0': self.CLS,
			'00EE': self.RET,
			'1nnn': self.JP_addr,
			'2nnn': self.CALL_addr,
			'3xkk': self.SE_Vx_byte,
			'4xkk': self.SNE_Vx_byte,
			'5xy0': self.SE_Vx_Vy,
			'6xkk': self.LD_Vx_byte,
			'7xkk': self.ADD_Vx_byte,
			'8xy0': self.LD_Vx_Vy,
			'8xy1': self.OR_Vx_Vy,
			'8xy2': self.AND_Vx_Vy,
			'8xy3': self.XOR_Vx_Vy,
			'8xy4': self.ADD_Vx_Vy,
			'8xy5': self.SUB_Vx_Vy,
			'8xy6': self.SHR_Vx_Vy,
			'8xy7': self.SUBN_Vx_Vy,
			'8xyE': self.SHL_Vx_Vy,
			'9xy0': self.SNE_Vx_Vy,
			'Annn': self.LD_I_addr,
			'Bnnn': self.JP_V0_addr,
			'Cxkk': self.RND_Vx_byte,
			'Dxyn': self.DRW_Vx_Vy_nibble,
			'Ex9E': self.SKP_Vx,
			'ExA1': self.SKNP_Vx,
			'Fx07': self.LD_Vx_DT,
			'Fx0A': self.LD_Vx_K,
			'Fx15': self.LD_DT_Vx,
			'Fx18': self.LD_ST_Vx,
			'Fx1E': self.ADD_I_Vx,
			'Fx29': self.LD_F_Vx,
			'Fx33': self.LD_B_Vx,
			'Fx55': self.LD_I_Vx,
			'Fx65': self.LD_Vx_I
		}

		self.V = [0] * 16
		self.VF = self.V[0xF]

		self.I = 0
		self.DT = 0
		self.ST = 0

		self.IP = 0
		self.SP = 0

		self.ram = [0] * (0xFFF + 1) # last memory address + 1

		# load ROM
		for i in range(len(self.fontset)):
			self.ram[self.FONTSET_BASE + i] = self.fontset[i]

		self.stack = [0] * 16
		self.pressed_keys = [0] * 16

		self.wait_for_keypress = False
		self.wait_for_keypress_register = None

	def load(self, data):
		for i in range(len(data)):
			self.ram[self.PROGRAM_BASE + i] = ord(data[i])

		# Most Chip-8 programs start at location 0x200 (512)
		self.IP = 0x200

	def tick(self):
		if self.wait_for_keypress:
			# we are running LD Vx, K
			self.LD_Vx_K_continue()
		else:
			instruction = self.get_instruction(self.IP)

			decoded = self.decode_instruction(instruction)
			if decoded is None:
				raise Exception("Unknown instruction at address %04x" % self.IP)

			#print decoded
			(handler, args) = decoded
			# at the moment of command execution, IP contains the address of the next instruction to be executed.
			self.IP += 2

			handler(*args)

	def timer(self):
		if self.DT > 0:
			self.DT -= 1

		if self.ST > 0:
			self.ST -= 1

	def key_down(self, key):
		self.pressed_keys[key] = True

	def key_up(self, key):
		self.pressed_keys[key] = False

	def get_instruction(self, addr):
		# guess it's little endian
		return (self.ram[addr] << 8) + self.ram[addr + 1]

	def int2hex(self, i):
		return ("%04x" % i).upper()

	def decode_instruction(self, word):
		hex = self.int2hex(word)
		keys = self.opcodes.keys()
		keys = sorted(keys, key=lambda key: key.count('x') + key.count('y') + key.count('k') + key.count('n'))

		for code in keys:
			handler = self.opcodes[code]
			# make regex
			regex = code.replace('x', '(.)').replace('y', '(.)').replace('kk', '(..)').replace('nnn', '(...)').replace('n', '(.)')

			m = re.match(regex, hex)
			if m:
				args = []
				for arg in m.groups():
					args.append(int(arg, 16))

				return (handler, args)

		return None

	def SYS_addr(self, addr):
		"""
		SYS addr

		Jump to a machine code routine at nnn.
		"""
		pass

	def CLS(self):
		"""
		CLS

		Clear the display.
		"""
		self.video.clear()

	def RET(self):
		"""
		RET

		Return from a subroutine.
		"""
		self.SP -= 1
		self.IP = self.stack[self.SP]

	def JP_addr(self, addr):
		"""
		JP addr

		Jump to location nnn.
		"""
		self.IP = addr

	def CALL_addr(self, addr):
		"""
		CALL addr

		Call subroutine at nnn.
		"""
		self.stack[self.SP] = self.IP
		self.SP += 1
		self.IP = addr

	def SE_Vx_byte(self, x, byte):
		"""
		SE Vx, byte

		Skip next instruction if Vx = kk.
		"""
		if self.V[x] == byte:
			self.IP += 2

	def SNE_Vx_byte(self, x, byte):
		"""
		SNE Vx, byte

		Skip next instruction if Vx != kk.
		"""
		if self.V[x] != byte:
			self.IP += 2

	def SE_Vx_Vy(self, x, y):
		"""
		SE Vx, Vy

		Skip next instruction if Vx = Vy.
		"""
		if self.V[x] == self.V[y]:
			self.IP += 2

	def LD_Vx_byte(self, x, byte):
		"""
		LD Vx, byte

		Set Vx = kk.
		"""
		self.V[x] = byte

	def ADD_Vx_byte(self, x, byte):
		"""
		ADD Vx, byte

		Set Vx = Vx + kk.
		"""
		self.V[x] += byte
		self.V[x] &= 255

	def LD_Vx_Vy(self, x, y):
		"""
		LD Vx, Vy

		Set Vx = Vy.
		"""
		self.V[x] = self.V[y]

	def OR_Vx_Vy(self, x, y):
		"""
		OR Vx, Vy

		Set Vx = Vx OR Vy.
		"""
		self.V[x] |= self.V[y]

	def AND_Vx_Vy(self, x, y):
		"""
		AND Vx, Vy

		Set Vx = Vx AND Vy.
		"""
		self.V[x] &= self.V[y]

	def XOR_Vx_Vy(self, x, y):
		"""
		XOR Vx, Vy

		Set Vx = Vx XOR Vy.
		"""
		self.V[x] ^= self.V[y]

	def ADD_Vx_Vy(self, x, y):
		"""
		ADD Vx, Vy

		Set Vx = Vx + Vy, set VF = carry.
		"""
		self.V[x] += self.V[y]
		if self.V[x] > 255:
			self.VF = 1
			self.V[x] &= 255
		else:
			self.VF = 0

	def SUB_Vx_Vy(self, x, y):
		"""
		SUB Vx, Vy

		Set Vx = Vx - Vy, set VF = NOT borrow.
		"""
		self.VF = 1 if self.V[x] > self.V[y] else 0
		self.V[x] -= self.V[y]
		if self.V[x] < 0:
			self.V[x] = self.V[x] + 256

	def SHR_Vx_Vy(self, x, y):
		"""
		SHR Vx

		Set Vx = Vx SHR 1.
		"""
		self.VF = self.V[x] & 1
		self.V[x] >>= 1

	def SUBN_Vx_Vy(self, x, y):
		"""
		SUBN Vx, Vy

		Set Vx = Vy - Vx, set VF = NOT borrow.
		"""
		self.VF = 1 if self.V[y] > self.V[x] else 0
		self.V[x] = self.V[y] - self.V[x]
		if self.V[x] < 0:
			self.V[x] = self.V[x] + 256

	def SHL_Vx_Vy(self, x):
		"""
		SHL Vx

		Set Vx = Vx SHL 1.
		"""
		self.V[x] <<= 1
		if self.V[x] > 127:
			self.VF = 1

		self.V[x] &= 255

	def SNE_Vx_Vy(self, x, y):
		"""
		SNE Vx, Vy

		Skip next instruction if Vx != Vy.
		"""
		if self.V[x] != self.V[y]:
			self.IP += 2

	def LD_I_addr(self, addr):
		"""
		LD I, addr

		Set I = nnn.
		"""
		self.I = addr

	def JP_V0_addr(self, addr):
		"""
		JP V0, addr

		Jump to location nnn + V0.
		"""
		self.IP = addr + self.V[0]

	def RND_Vx_byte(self, x, byte):
		"""
		RND Vx, byte

		Set Vx = random byte AND kk.
		"""
		self.V[x] = random.randint(0, 255) & byte

	def DRW_Vx_Vy_nibble(self, x, y, n):
		"""
		DRW Vx, Vy, nibble

		Display n-byte sprite starting at memory location I at (Vx, Vy), set VF = collision.
		"""
		for i in range(n):
			byte = self.ram[self.I + i]
			yy = self.V[y] + i
			for j in range(8):
				xx = self.V[x] + j

				is_white = True if (byte >> (7 - j)) & 1 else False
				if (xx >= 0) and (xx < self.video.width) \
					and (yy >= 0) and (yy < self.video.height):
					if is_white and self.video.get_pixel(xx, yy):
						self.VF = 1
						is_white = False
					elif not is_white and self.video.get_pixel(xx, yy):
						is_white = True

					self.video.set_pixel(xx, yy, is_white)

	def SKP_Vx(self, x):
		"""
		SKP Vx

		Skip next instruction if key with the value of Vx is pressed.
		"""
		if self.pressed_keys[self.V[x]]:
			self.IP += 2

	def SKNP_Vx(self, x):
		"""
		SKNP Vx

		Skip next instruction if key with the value of Vx is not pressed.
		"""
		if not self.pressed_keys[self.V[x]]:
			self.IP += 2

	def LD_Vx_DT(self, x):
		"""
		LD Vx, DT

		Set Vx = delay timer value.
		"""
		self.V[x] = self.DT

	def LD_Vx_K(self, x):
		"""
		LD Vx, K

		Wait for a key press, store the value of the key in Vx.
		"""
		self.wait_for_keypress = True
		self.wait_for_keypress_register = x

	def LD_Vx_K_continue(self):
		"""
		Run on exit from LD_Vx_K
		"""
		for k, v in enumerate(self.pressed_keys):
			if v:
				self.V[self.wait_for_keypress_register] = k
				self.wait_for_keypress = False

	def LD_DT_Vx(self, x):
		"""
		LD DT, Vx

		Set delay timer = Vx.
		"""
		self.DT = self.V[x]

	def LD_ST_Vx(self, x):
		"""
		LD ST, Vx

		Set sound timer = Vx.
		"""
		self.ST = self.V[x]

	def ADD_I_Vx(self, x):
		"""
		ADD I, Vx

		Set I = I + Vx.
		"""
		self.I += self.V[x]

	def LD_F_Vx(self, x):
		"""
		LD F, Vx

		Set I = location of sprite for digit Vx.
		"""
		self.I = self.FONTSET_BASE + self.V[x] * 5

	def LD_B_Vx(self, x):
		"""
		LD B, Vx

		Store BCD representation of Vx in memory locations I, I+1, and I+2.
		"""
		value = self.V[x]
		for i in range(2, -1, -1):
			self.ram[self.I + 1] = value % 10
			value /= 10

	def LD_I_Vx(self, x):
		"""
		LD [I], Vx

		Store registers V0 through Vx in memory starting at location I.
		"""
		for i in range(0, x + 1):
			self.ram[self.I + i] = self.V[i]

	def LD_Vx_I(self, x):
		"""
		LD Vx, [I]

		Read registers V0 through Vx from memory starting at location
		"""
		for i in range(0, x + 1):
			self.V[i] = self.ram[self.I + i]