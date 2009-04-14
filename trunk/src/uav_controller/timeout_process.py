#!/usr/bin/env python

import os, time
from optparse import OptionParser

class timeout:
	def __init__(self):
		time.sleep(self.optparse())
	
	def optparse(self):
		parser = OptionParser("Useage: %prog -t arg1")
		parser.add_option("-t", "--time", action="store", type="int", dest="time")
		(options, args) = parser.parse_args()
		return int(options.time)

if __name__ == "__main__":
	timeout()
