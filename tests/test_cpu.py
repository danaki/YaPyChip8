import unittest
from chip8.cpu import CPU

class CPUTest(unittest.TestCase):
	def setUp(self):
		self.cpu = CPU()
		
	def test_int2hex(self):
		self.assertEquals('0000', self.cpu.int2hex(0))
		self.assertEquals('0001', self.cpu.int2hex(1))
		self.assertEquals('00FF', self.cpu.int2hex(255))
		self.assertEquals('0100', self.cpu.int2hex(256))
		self.assertEquals('0FFF', self.cpu.int2hex(0x0FFF))
		self.assertEquals('FFFF', self.cpu.int2hex(0xFFFF))
		self.assertEquals('A123', self.cpu.int2hex(0xA123))
		
	def test_decode_instruction(self):
		self.assertEquals((self.cpu.CLS, []), self.cpu.decode_instruction(0x00E0)) # CLS
		self.assertEquals((self.cpu.JP_addr, [564]), self.cpu.decode_instruction(0x1234)) # JP 0x234
		self.assertEquals((self.cpu.LD_Vx_Vy, [1, 2]), self.cpu.decode_instruction(0x8120)) # LD V1, V2
		self.assertEquals((self.cpu.RND_Vx_byte, [5, 255]), self.cpu.decode_instruction(0xC5FF)) # RND V5, FF
		self.assertEquals((self.cpu.DRW_Vx_Vy_nibble, [4, 5, 7]), self.cpu.decode_instruction(0xD457)) # DRW V4, V5, 7
		self.assertEquals((self.cpu.LD_I_Vx, [10]), self.cpu.decode_instruction(0xFA55)) # LD [I], V10

	def load_example_program(self):
		program = '00E081201000' # CLS; LD V1, V2; JP 0000
		data = bytearray(program.decode('hex'))
		self.cpu.load(data)

	def test_get_instruction(self):
		self.load_example_program()
		self.assertEquals(0x00E0, self.cpu.get_instruction(0))
		self.assertEquals(0x8120, self.cpu.get_instruction(2))
		self.assertEquals(0x1000, self.cpu.get_instruction(4))

	def test_load_and_decode_instruction(self):
		self.load_example_program()
