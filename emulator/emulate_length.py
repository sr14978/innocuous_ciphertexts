
"""This is a progam for creating an invertable encoding that produces ciphertexts that look like they come from a given distrobution"""

import numpy as np
from collections import deque
import random

import common as com

def init_emulator(bins):
	"""Returns (encode, decode) functions that emulate the length distrobution defined by `bins`."""
	cumlative_splits = com._create_cumlative_splits(bins)

	def encode(messages):

		# put in to a continous stream
		data_stream = ""
		for text in messages:
			data_stream += "%08X"%(len(text))
			data_stream += text

		# slice up following the distrobution
		distributed_texts = []
		while len(data_stream) > 0:
			length = sample(cumlative_splits)
			if len(data_stream) > length:
				out = data_stream[:length]
				distributed_texts.append("%04x"%(length))
				distributed_texts.append(out)
				data_stream = data_stream[length:]
			else:
				distributed_texts.append("%04x"%(len(data_stream)))
				distributed_texts.append(data_stream)
				data_stream = ""

		return distributed_texts

	def decode(urls):

		# join back in to continous stream
		data_stream = "".join(urls)

		original_messages = []
		while len(data_stream) > 0:
			length = int(data_stream[:4], 16)
			data_stream = data_stream[4:]
			message = data_stream[:length]
			data_stream = data_stream[length:]
			original_messages.append(message)

		return original_messages

	return encode, decode

def sample(dist):
	max = dist[-1][1]
	return com._lies_at_index_range(dist, random.randrange(max))