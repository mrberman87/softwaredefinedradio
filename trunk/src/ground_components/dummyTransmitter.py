#!/usr/bin/python

"""This will be used to simulate transmitting and recieving data with USRP"""

import time

class dummyTransmitter():
	def __init__(self):
		self.mod = ''
		self.freq = ''
		self.fileNum = 0
		self.fileNames = ['image.jpg', 'gps.txt', 'sensors.txt']
		self.data = ''
		
	def send(self, filename):
		"""open the specified filename and send the data inside"""
		"""will pause for a period to send data"""
		time.sleep(3)
		return True
	def send(self, data):
		"""simulate sending string data"""
		self.data = data
		time.sleep(1)
		return
		
	def receive(self):
		"""simulate waiting for and recieving a file, then return
		the filename"""
		time.sleep(10)
	
		return self.data + ".txt"
