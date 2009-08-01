#!/usr/bin/env python

import os, time
from payload_transmit_path import *

class uav_controller:
	def __init__(self):
		#set priority
		os.system("renice 0 %d" % os.getpid())
		self.log("Starting Up: pid = %d" % os.getpid())
		self.init_vars()
		
		#This is the main controller section of code
		while True:
			

	def init_vars(self):
		#initialize all class level variables
		

	def init_rx_msgq(self):
		

	def init_tx_msgq(self):
		


