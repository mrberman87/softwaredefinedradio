#!/usr/bin/env python

import time
import os
import sys
import signal
import UAV
import Transceiver

fromUAV,toTransceiver = os.pipe()
fromTransceiver,toUAV = os.pipe()

class controller():
	def __init__(self):
		self.fft_fn = '/fft.png'
		self.mod_scheme = 'bpsk'
		self.fft= False
		self.pid = os.fork()
		print 'pid : ', self.pid
		self.forkit()

	def forkit(self):
		self.pid = os.fork()
		self.run()

	def run(self):
		if self.pid == 0:
			try:
				t = Transceiver.Transceiver(self, self.pid, self.fft_fn, self.mod_scheme, self.fft, toUAV, fromUAV)
				while True:
					pass
			except:
				print 'Unable to open USRP, closing process : ', str(self.pid)
				os.write(toUAV, 'closing')
				sys.exit(0)
		
		else:
			try:
				u = UAV.UAV(self, toTransceiver, fromTransceiver)
				while True:
					pass	
			except:
				os.write(toTransceiver, 'close:')
				time.sleep(1)
				os.kill(self.pid, signal.SIGTERM)
				sys.exit(0)

if __name__ == '__main__':
	controller()
