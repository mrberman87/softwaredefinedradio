#!/usr/bin/env python

"""
ground_controls.py is the Model in the MVC architecture. It stores the application
specific (in this case a ground station) data and logic. The data stored includes
GPS data, modulation scheme, image, and other telemetry data. This provides 
various functions to request data from the UAV.
"""
import os
import abstractmodel
import sys
import Queue
sys.path.append("GPS") #includes GPS/ directory to use GPS_packet.py
from GPS_packet import GPS_packet
from dummyTransmitter import dummyTransmitter


class ground_controls(abstractmodel.AbstractModel):
	def __init__(self):
		abstractmodel.AbstractModel.__init__(self)
		self.gps = GPS_packet("GPSD,P=0 0,A=0,V=0,E=0")
		self.temperature = '0'
		self.batt = '0'
		self.freq = '0'
		self.modulation = ''
		self.timeout = '10' #(in seconds)
		self.sigPower = '0'
		self.cmd_list = []
		self.imageClickedTimes = 0 #test var to test relaying information to view
		self.imageFileName = ''
		self.tsvr = dummyTransmitter()
	
	
	"""GUI responder methods: These are the only methods that should be
	called by the GUI"""	
	def addToQueue(self, cmd):
		self.cmd_list.append(cmd)
		self.update()
		self.process_commands()


	"""Worker methods: These methods send and recieve data from the
	transeiver."""
	def process_commands(self):
		while(len(self.cmd_list) > 0):
			cmd = self.cmd_list.pop()
			if cmd == 'GPS':
				self.getGPS()
			elif cmd == 'Image':
				self.getImage()
			elif cmd == 'FFT': pass
			else: pass
			
			#receive the data

	def getImage(self):
		self.tsvr.send(data = 'Image')
		filename = self.tsvr.receive()
		self.update()
	
	def changeModScheme(self, mod):
		self.modulation = mod
		self.update()
	
	def getGPS(self):
		self.tsvr.send(data = 'GPS')
		#recieve returns the name of the file it recieved
		fname = self.tsvr.receive()
		f = open(fname)
		self.gps = GPS_packet(f.readline())
		self.update()
