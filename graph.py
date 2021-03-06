#!/usr/bin/python2

"""
This program can display the relation of normal, fake and emulated distrobutions to a reference distrobution.
```bash
./graph.py --mode <binning_method>
eg ./graph.py --mode char
```
"""

import numpy as np
import math
import calculate as calc
import bins
import functools as ft
import os
import argparse
import matplotlib.pyplot as plt

def display(size=1000, mode=bins.default_mode):

	base_path = os.path.dirname(os.path.abspath(__file__))

	fake_path = base_path + "/" + str(size) + "/fakes/"
	normal_path = base_path + "/" + str(size) + "/normals/"
	emulated_path = base_path + "/" + str(size) + "/emulated/" + mode + "/"


	fake_paths = [fake_path + p for p in os.listdir(fake_path) if p != "results"]
	normal_paths = [normal_path + p for p in os.listdir(normal_path) if p != "results"]
	emulated_paths = [emulated_path + p for p in os.listdir(emulated_path) if p != "results"]

	test = ft.partial(
		calc.test_file,
		reference_file= str(size) + "/censor/reference_" + mode + "_bins",
		mode=mode
	)

	fakes = [test(p) for p in fake_paths]
	normals = [test(p) for p in normal_paths]
	emulateds = [test(p) for p in emulated_paths]

	# fake = np.mean(fakes)
	# normal = np.mean(normals)
	# emulated = np.mean(emulateds)

	# print "fake", fake, fakes
	# print "normal", normal, normals
	# print "emualted", emulated, emulateds

	plt.plot(fakes, 'ro', normals, 'go', emulateds, 'bx')
	plt.xlabel("Sample Index")
	plt.ylabel("Statistic Value")
	plt.show()

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
	parser.add_argument('-s', '--size', default="1000")
	parser.add_argument('-m', '--mode',
		choices=bins.modes.values(), default=bins.default_mode)
	args = vars(parser.parse_args())
	display(args["size"], args["mode"])
