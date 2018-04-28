
"""This is a progam for creating an invertable encoding that produces ciphertexts that look like they come from a given distrobution"""

import numpy as np
from collections import deque
import random

import common as com
import common_dict as comd

def init_emulator(bins, base=100, message_length=256, pattern_length=40):
	"""Returns (encode, decode) functions that emulate the character distrobution defined by `bins`."""
	message_max = (message_length+1)*8
	cumlative_splits = comd._create_cumlative_splits(bins)
	comd._set_dist(cumlative_splits)
	digit_splits = comd._create_digit_splits(bins, base, cumlative_splits)
	base_powers = com._calculate_powers_of_base(base, message_max)
	def encode(message):
		message = '\xFF'+message
		input_value = 0
		for char in message:
			input_value <<= 8
			input_value += ord(char)
		if input_value > (1<<message_max):
			raise Exception("Message too long")
		digits = deque()
		non_zero_digit_not_found = True
		for mod in base_powers:
			digit = input_value/mod
			if non_zero_digit_not_found:
				if digit == 0:
					continue
				else:
					non_zero_digit_not_found = False
			digits.appendleft(digit)
			input_value -= digit*mod
		bit_stream = []
		for digit in digits:
			low_split, high_split = digit_splits[digit]
			value = low_split + random.random()*(high_split-low_split)
			index = comd._lies_at_index_range(value)
			value = index
			# value = index + int(0.2e7)	# bin offset
			# value = (index + 30)	# bin offset
			bit_stream += to_pattern_bits(value)
		character_stream = []
		while len(bit_stream) > 0:
			character_stream.append(chr(evaluate(bit_stream[:8])))
			bit_stream = bit_stream[8:]
		return "".join(character_stream)

	def to_pattern_bits(value):
        	return [(value>>i)&1 for i in range(pattern_length)]

	def evaluate(bits):
        	sum = 0
	        for bit in reversed(bits):
        	        sum <<= 1
                	sum += bit
	        return sum

	def to_char_bits(value):
                return [(value>>i)&1 for i in range(8)]


	def decode(url):

		bit_stream = [b for c in url for b in to_char_bits(ord(c))]
		pattern_stream = []
		while len(bit_stream) > 0:
			pattern_stream.append(evaluate(bit_stream[:pattern_length]))
			bit_stream = bit_stream[pattern_length:]
		digits = deque()
		for pattern in pattern_stream:
			index = pattern
			# index = pattern - int(0.2e7)
			# index = pattern - 30
			value,_ = cumlative_splits[index]
			digit = com._lies_at_index_range(digit_splits, value)
			digits.append(digit)
		output_value = 0
		for digit,mod in zip(digits, base_powers[::-1]):
			output_value += digit*mod
		message = deque()
		while output_value != 0xFF:
			message.appendleft(chr(output_value & 0xFF))
			output_value >>= 8
		return "".join(message)

	return encode, decode
