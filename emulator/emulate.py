
import argparse
import pickle
import random

modes = {
	'PATTERN_DISTROBUTION':'pattern',
	'CHARACTER_DISTROBUTION':'char',
	'SLASHES_FREQUENCY':'slash',
	'INTER_SLASH_DIST':'dist',
	'FIRST_LETTER':'first',
	'RANDOM_LETTER':'rand',
	'URL_LENGTH':'length'
}

def get_emulations(messages=None, number=1000, mode=modes['CHARACTER_DISTROBUTION'], reference_file=None):
	"""Produce example encodings"""

	def randchar():
		return chr(random.randrange(33, 127))

	if mode == modes['URL_LENGTH']:
		message_length = 238
		encode,_ = init_emulator(mode=mode)


		if messages == None:
			messages = ["".join([randchar() for _ in range(message_length)]) for _ in range(number)]
		return encode(messages)

	elif mode == modes['PATTERN_DISTROBUTION']:
		message_length = 238
		encode,_ = init_emulator(mode=modes['PATTERN_DISTROBUTION'], message_length=message_length)

		if messages == None:
			messages = ["".join([randchar() for _ in range(message_length)]) for _ in range(number)]
		return [encode(m) for m in messages]

	elif mode == modes['CHARACTER_DISTROBUTION']:
		message_length = 238
		encode,_ = init_emulator(mode=modes['PATTERN_DISTROBUTION'], message_length=message_length)

		if messages == None:
			messages = ["".join([randchar() for _ in range(message_length)]) for _ in range(number)]
		return [encode(m) for m in messages]


def init_emulator(mode=modes['CHARACTER_DISTROBUTION'], reference_file=None, message_length=256, key_enc=None, key_mac=None):
	"""construct encode and decode fuctions that emulate the `bins` distrobution"""
	if reference_file == None:
		import os.path as path
		dir_path = path.abspath(path.join(__file__ ,"../.."))
		reference_file = dir_path + "/1000/adversary/reference_" + mode + "_bins"

	if mode == modes['PATTERN_DISTROBUTION']:
		with open(reference_file, "rb") as f:
			bins = pickle.load(f)

		import emulate_pattern
		return emulate_pattern.init_emulator(bins, message_length=message_length)

	elif mode == modes['CHARACTER_DISTROBUTION'] or mode == modes['INTER_SLASH_DIST'] or mode == modes['FIRST_LETTER'] or mode == modes['RANDOM_LETTER']:

		with open(reference_file, "rb") as f:
			bins = pickle.load(f)

		import emulate_char
		# base = number of distrobution divisions
		base = 10
		return emulate_char.init_emulator(bins, base, message_length)

	elif mode == modes['URL_LENGTH']:

		with open(reference_file, "rb") as f:
			bins = pickle.load(f)

		import emulate_length
		return emulate_length.init_emulator(bins)

	elif mode == 'proxy':

		with open(dir_path + "/1000/adversary/reference_char_bins", "rb") as f:
			bins = pickle.load(f)

		import emulate_char, emulate_length, conf
		# base = number of distrobution divisions
		base = 15
		encode,decode = emulate_char.init_emulator(bins, base, message_length)

		with open(dir_path + "/1000/adversary/reference_length_bins", "rb") as f:
			bins = pickle.load(f)

		to_length_dist, from_length_dist = emulate_length.init_emulator(bins)

		if key_enc == None or key_mac == None:
			raise Exception("No key")

		from fte.encrypter import Encrypter
		import padder
		encrypter = Encrypter(K1=key_enc, K2=key_mac)

		return Encoder(encrypter, to_length_dist, encode), Decoder(encrypter, from_length_dist, decode)

	else:
		raise Exception("mode not supported")


class Encoder:
	def __init__(self, encrypter, to_length_dist, encode):
		self._encrypter = encrypter
		self._to_length_dist = to_length_dist
		self._encode = encode

	def encode(self, data):
		return "GET /" + self._encode(data) + " HTTP/1.1\r\n\r\n"

	def encrypt(self, data):
		return self._encrypter.encrypt(data)

	def to_length_dist(self, input):
		return self._to_length_dist(input)

class Decoder:
	def __init__(self, encrypter, from_length_dist, decode):
		self._encrypter = encrypter
		self._from_length_dist = from_length_dist
		self._decode = decode

	def decode(self, buffer):
		index = buffer.find("HTTP/1.1\r\n\r\n")
		if index == -1:
			return None, buffer
		else:
			packet = buffer[:index+12]
			buffer = buffer[index+12:]
			msg = self._decode(packet[5:-13])
			return msg, buffer

	def decrypt(self, data):
		return self._encrypter.decrypt(data)

	def from_length_dist(self, input):
		return self._from_length_dist(input)
