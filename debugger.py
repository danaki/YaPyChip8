#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Framework for a minimal shell.
Based on: http://inspirated.com/2009/08/01/writing-a-minimal-shell-in-python
"""

import exceptions
import shlex
import signal
import sys
import re
import inspect
import pygame

from chip8.cpu import CPU
from chip8.video import Video

class SIGINTException(Exception):
	pass

class ExitException(Exception):
	pass

class CommandException(Exception):
	pass

class BadArgumentsException(CommandException):
	def __init__(self, message=None):
		self.message = message

	def __str__(self):
		result = "Bad arguments, see 'help' for usage"
		if not self.message is None:
			result += ": " + self.message

		return result

class BadArgumentCountException(BadArgumentsException):
	def __init__(self):
		super(NoArgumentsRequredException, self).__init__("wrong number of arguments")

class NoArgumentsRequredException(BadArgumentsException):
	def __init__(self):
		super(NoArgumentsRequredException, self).__init__("this command require no arguments")

class Debugger:
	def __init__(self, rom_file):
		signal.signal(signal.SIGINT, self.sigint_handler)

		self.commands = {
			"[di]sassemble": ("Disassemble: disassemble addr[, count=16]", self.cmd_disassemble),
			"[r]egisters": ("Examine registers", self.cmd_registers),
			"[s]tep": ("One CPU step: step [count=1]", self.cmd_step),
			"[v]ideo": ("Examine video memory contents", self.cmd_video),
			"[du]mp": ("Dump memory: dump addr[, count=16]", self.cmd_dump),
			"[h]elp": ("This help", self.cmd_help),
			"[q]uit": ("Quit", self.cmd_quit),
		}

		self.video = Video()
		screen = pygame.display.set_mode(self.video.get_mode())
		#pygame.mouse.set_visible(0)
		pygame.display.update()

		surface = pygame.Surface(screen.get_size())
		surface = surface.convert()
		screen.blit(surface, (0, 0))
		self.video.set_surface(surface)

		pygame.display.flip()

		self.cpu = CPU(self.video)
		fd = open(rom_file, "rb")
		self.cpu.load(fd.read())

	def run(self):
		last_command = None
		while True:
			try:
				prompt = "(debugger) "
				raw = raw_input(prompt)
				if (raw == '') and (not last_command is None):
					callback, callback_args = last_command
					callback(*callback_args)
				else:
					args = shlex.split(raw)

					callback = None
					for k, v in self.commands.items():
						m = re.search("^(.*)\[(.*)\](.*)$", k)
						short = m.group(2)
						long = m.group(1) + m.group(2) + m.group(3)

						if args[0] in [short, long]:
							callback = v[1]
							# we assume that command arguments are always numeric either in hex 0x... or decimal format
							callback_args = []
							for arg in args[1:]:
								try:
									arg = int(arg, 0)
								except (ValueError, TypeError):
									pass

								callback_args.append(arg)

							last_command = callback, callback_args
							callback(*callback_args)
							break
					else:
						raise CommandException("Unknown command %s" % args[0])

			except IndexError:
				continue

			except CommandException as e:
				print e

			except (EOFError, ExitException):
				return 0

			except SIGINTException:
				print >> sys.stderr, \
					"<SIGINT received, bye-bye>"
				return 1

	def sigint_handler(self, signum, frame):
		"""Handler for the SIGINT signal."""
		raise SIGINTException

	def print_addr(self, addr):
		instruction = self.cpu.get_instruction(addr)
		decoded = self.cpu.decode_instruction(instruction)

		print "0x%04X 0x%04X" % (addr, instruction),

		if decoded is None:
			print "*** Unknown instruction"
		else:
			(handler, args) = decoded
			syntax = re.split('\n', inspect.getdoc(handler))[0]
			fmt = syntax\
				.replace('Vx', 'V%d')\
				.replace('Vy', 'V%d')\
				.replace('addr', '0x%04X')\
				.replace('nibble', '%d')\
				.replace('byte', '0x%02X')\

			print fmt % tuple(args),
			if addr == self.cpu.IP:
				print " <<<",

			print

	def cmd_disassemble(self, *args):
		if (len(args) < 1) or (len(args) > 2):
			raise BadArgumentCountException

		addr = args[0]
		count = args[1] if len(args) == 2 else 16

		while (count > 0) and (addr < len(self.cpu.ram) - 2):
			self.print_addr(addr)

			count -= 1
			addr += 2

	def cmd_registers(self, *args):
		if len(args) > 0:
			raise BadArgumentsException

		for i in range(0, len(self.cpu.V)):
			print "V%d: 0x%02x" % (i, self.cpu.V[i])

		print "I: 0x%04X" % self.cpu.I
		print "DT: 0x%02X" % self.cpu.DT
		print "ST: 0x%02X" % self.cpu.ST
		print "(IP): 0x%04X" % self.cpu.IP
		print "(SP): 0x%02X" % self.cpu.SP

	def cmd_dump(self, *args):
		if (len(args) < 1) or (len(args) > 2):
			raise BadArgumentCountException

		addr = args[0]
		count = args[1] if len(args) == 2 else 16

		i = 0
		while (i < count) and (addr < len(self.cpu.ram) - 2):
			if ((i % 16) == 0) and (i > 0):
				print

			print "%02X" % self.cpu.ram[addr],

			i += 1
			addr += 2

		print

	def cmd_video(self, *args):
		if len(args) > 0:
			raise BadArgumentCountException

		for y in xrange(0, 32):
			for x in xrange(0, 64):
				print 'x' if self.video.get_pixel(x, y) else '.',

			print

		print

	def cmd_step(self, *args):
		if len(args) > 1:
			raise BadArgumentCountException

		if len(args) == 0:
			count = 1
		else:
			count = args[0]

		while count > 0:
			self.print_addr(self.cpu.IP)
			self.cpu.tick()
			count -= 1

	def cmd_help(self, *args):
		if len(args) > 0:
			raise NoArgumentsRequredException

		for k, v in self.commands.items():
			print k,
			print " " * (12 - len(k)),
			print v[0]

	def cmd_quit(self, *args):
		raise ExitException

if __name__ == "__main__":
	if len(sys.argv) != 2:
		print "Usage: debugger.py [rom_file]"
	else:
		sys.exit(Debugger(sys.argv[1]).run())
