#!/usr/bin/env python

"""
self.py is the Model in the MVC architecture. It stores the application
specific (in this case a ground station) data and logic. The data stored includes
GPS data, modulation scheme, image, and other telemetry data. This provides 
various functions to request data from the UAV.
"""
import os
import abstractmodel
import sys
import threading
import Queue
sys.path.append("GPS") #includes GPS/ directory to use GPS_packet.py
from GPS_packet import GPS_packet
from dummyTransmitter import dummyTransmitter


class ground_controls(abstractmodel.AbstractModel, threading.Thread):

	def __init__(self):
		abstractmodel.AbstractModel.__init__(self)
		threading.Thread.__init__(self)
		self.pendingRequest = threading.Event()
		self.cmd_qLock = threading.Lock()
		self.gps = GPS_packet("GPSD,P=0 0,A=0,V=0,E=0")
		self.temperature = '0'
		self.batt = '0'
		self.freq = '0'
		self.modulation = 'BPSK'
		self.timeout = '10' #(in seconds)
		self.sigPower = '0'
		self.cmd_list = []
		self.MAX_COMMANDS=3
		self.imageFileName = ''
		self.tsvr = dummyTransmitter()
	
	
	"""GUI responder methods: These are the only methods that should be
	called by the GUI"""	
	def addToQueue(self, cmd):
		self.cmd_qLock.acquire()
		if len(self.cmd_list) > 2:
			self.cmd_qLock.release()
			raise QueueLimitException()
		self.cmd_list.append(cmd)
		self.cmd_qLock.release()
		self.update()
		self.pendingRequest.set()

	def getNextCommand(self):
		cmd = ''
		self.cmd_qLock.acquire()
		if len(self.cmd_list) > 0:
			cmd = self.cmd_list[0]
			self.cmd_list[0]+=' (Pending)'
		self.cmd_qLock.release()
		self.update()
		if len(self.cmd_list) > 0:
			self.pendingRequest.set()
		return cmd
	
	def removeCompletedCommand(self):
		"""Remove the first item in command queue to convey that it
			has been completed"""
		self.cmd_qLock.acquire()
		if len(self.cmd_list) > 0:
			self.cmd_list.pop(0)
		if len (self.cmd_list) == 0:
			self.pendingRequest.clear()
		self.cmd_qLock.release()
		self.update()

	def run(self):
		"""This method is called when the thread is started. It executes
		commands in the command queue when there are items in it. If there
		are no items in the queue, this thread sleeps, until notified of a
		change in the queue."""
		while True:
			self.pendingRequest.wait()	#sleep until a command is requested

			cmd = self.getNextCommand()

			#figure out which command has been requested
			if cmd.startswith('GPS'):
				self.getGPS()
			elif cmd.startswith('Image'):
				self.getImage()
			elif cmd.startswith('FFT'): pass
			elif cmd.startswith('Batt'): pass
			elif cmd.startswith('Temp'): pass
			elif cmd.startswith('Freq'):
				freq = cmd.split(' ')[1] #string after the space is the freq.
				self.changeFrequency(freq)
			else: pass
			
			self.removeCompletedCommand()
			
			#receive the data



	"""Worker methods: These methods send and recieve data from the
	transeiver. They are I/O bound, which is why it is necessary to run them
	in a separate thread to keep the application responsive."""

	def getImage(self):
		self.tsvr.send(data = 'Image')
		filename = self.tsvr.receive()
		self.update()
	

	def getGPS(self):
		self.tsvr.send(data = 'GPS')
		#recieve returns the name of the file it recieved
		fname = self.tsvr.receive()
		f = open(fname)
		self.gps = GPS_packet(f.readline())
		self.update()

	def getBatt(self):
		self.tsvr.send(data = 'sensors')
		fname =self.tsvr.receive()
		f = open(fname)
		self.batt = f.readline()
		self.update()

	def changeModScheme(self, mod):
		self.modulation = mod
		self.update()

	def changeFrequency(self, newFreq):
		'''will need to send command to UAV, wait for confirmation,
		then save the new frequency in the model.'''
		self.freq = newFreq
		self.update()

class QueueLimitException(Exception):pass
