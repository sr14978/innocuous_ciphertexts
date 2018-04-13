#!/usr/bin/python2

description = """
Program produce ciphertexts that emulate the given reference distrobution
"""

import argparse
import pickle

import random

from bins import modes
from bins import default_mode

"""Produce example encodings"""
def get_emulations(messages=None, message_length=64*8, number=100, mode=modes['CHARACTER_DISTROBUTION'], reference_file=None):
	if messages == None:
		messages = [random.getrandbits(message_length) for _ in range(number)]
		
	encode, _ = init_emulator(mode=mode, message_length=message_length, reference_file=reference_file)
	
	return [encode(m) for m in messages]

"""construct encode and decode fuctions that emulate the `bins` distrobution"""
def init_emulator(mode=modes['CHARACTER_DISTROBUTION'], message_length=64*8, reference_file=None):
	
	if reference_file == None:
		reference_file = "100/reference_" + mode + "_bins"
		
	with open(reference_file, "rb") as f:
		bins = pickle.load(f)
	
	if mode == modes['CHARACTER_DISTROBUTION']:

		# base = number of distrobution divisions 
		base = 10
		import emulate_char
		return emulate_char.init_emulator(bins, base, message_length)
			
	else:
		print "mode not supported"


if __name__ == "__main__":

	parser = argparse.ArgumentParser(description=description)
	parser.add_argument('-o', '--out', default="100/emulated/char/1")
	parser.add_argument('-m', '--mode',
		choices=modes.values(), default=modes['CHARACTER_DISTROBUTION'])
	parser.add_argument('-nu', '--nouse', action='store_true')
	args = vars(parser.parse_args())
	
	if args["nouse"]:
		init_emulator(mode=args["mode"])
	else:
		urls = get_emulations(mode=args["mode"])
		with open(args["out"], "wb") as f:
			pickle.dump(urls, f)
	
	
	
