#!/usr/bin/env python

import os, time

class uav_controller:
	def __init__(self):
		#set priority
		os.system("renice 0 %d" % os.getpid())
		self.log("Starting Up: pid = %d" % os.getpid())
		self.init_vars()
		
		#This is the main controller section of code
		while True:
			

if __name__ == '__main__':
	uav_controller()
		


