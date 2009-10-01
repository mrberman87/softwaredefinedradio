#!/usr/bin/python

"""This will be used to simulate transmitting and recieving data with USRP"""

import time

class dummyTransmitter():
	def __init__(self):
		self.mod = ''
		self.freq = ''
		self.filename = ''
		self.img_count = 0
		
	def send(self, filename):
		"""open the specified filename and send the data inside"""
		"""will pause for a period to send data"""
		time.sleep(1)
		return True
	def send(self, data):
		"""simulate sending string data"""
		if data == 'GPS':
			self.filename = 'GPS.txt'
		elif data == 'Image':
			self.img_count = self.img_count + 1
			#alternate images in order to test functionality in GUI
			if self.img_count%2 == 0:
				self.filename = '1.jpg'
			else:
				self.filename = '2.jpg' 
		time.sleep(1)
		return
		
	def receive(self):
		"""simulate waiting for and recieving a file, then return
		the filename"""
		time.sleep(3)
	
		return self.filename
