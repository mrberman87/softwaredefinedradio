#!/usr/bin/env python

import os, time
from controls import *

class uav_controller:
	def __init__(self):
		#set priority
		os.system("renice 0 %d" % os.getpid())
		self.log("Starting Up: pid = %d" % os.getpid())
		self.init_vars()
		
		#This is the main controller section of code
		while True:
			#check for received packets
			#start receiver process
			self.rx_pid = controls.run_rx()
			
			#execute the command
			controls.exec_command()
			
			#transmit data
			self.tx_pid = controls.run_tx()

if __name__ == '__main__':
	uav_controller()
		


