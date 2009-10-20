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
		self.go_home() #initialize the "GO HOME" type variables
		self.temperature = '0'
		self.batt = '0'
		self.sigPower = '0'
		self.cmd_list = []
		self.MAX_COMMANDS=3
		self.imageFileName = ''
		self.tsvr = dummyTransmitter()
		self.fname = ''
		self.new_freq = 0
		self.new_modulation = ''
		self.new_timeout = 0
	
	
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
			if cmd.startswith('GPS'): self.send_data('GPS')
			elif cmd.startswith('Image'):self.send_data('Image')
			elif cmd.startswith('FFT'): self.send_data('FFT')
			elif cmd.startswith('Batt'): self.send_data('Telemetry')
			elif cmd.startswith('Settings'):
				tmp  = cmd.split(' ')
				self.new_freq = int(tmp[1])
				self.new_modulation = tmp[2]
				self.new_timeout = int(tmp[3])
				#self.new_handshake = int(tmp[4])
			else: pass
			
			self.removeCompletedCommand()
			self.update()
			#receive the data



	"""Worker methods: These methods send and recieve data from the
	transeiver. They are I/O bound, which is why it is necessary to run them
	in a separate thread to keep the application responsive."""
	
	def send_data(self, data):
		rx = True

		if data == 'GPS': self.fname = 'gps.dat'
		elif data == 'Image': self.fname = 'picture.jpg'
		elif data == 'FFT': self.fname = 'fft.jpeg'
		elif data == 'Telemetry': self.fname = 'tele.dat'
		elif data == 'Settings': self.fname = 'settings.dat'

		if data == 'Settings':
			#print things into a file to be sent up and change data to the file path
			rx = False
			fd = open(self.fname)
			fd.write("settings\n")
			if self.new_freq != self.freq: fd.write("Freq: " + self.new_freq + '\n')
			if self.new_timeout != self.timeout: fd.write("Timeout: " + self.new_timeout + '\n')
			#if self.new_handshake != self.handshake: fd.write("Hand_Max: " + self.new_handshake + '\n')
			if self.new_modulation != self.modulation: fd.write("Version: " + self.new_modulation + '\n')
			fd.close()
		
		tmp = self.tsvr.transmit(data)
		if tmp is True or tmp == 'Transmission Complete':
			self.go_home = 0
			#decode the data sent back down
			if data == 'GPS':
				f = open(self.fname)
				self.gps = GPS_packet(f.readline())
				f.close()
			elif data == 'Telemetry':
				f = open(self.fname)
				self.temprature = int(f.readline().strip('\n').strip())
				self.batt = int(f.readline().strip('\n').strip())
				f.close()
			elif data == 'Settings':
				self.freq = self.new_freq
				self.modulation = self.new_modulation
				self.timeout = self.new_timeout
				#self.handshake = self.new_handshake
		elif tmp == 'Handshaking Maximum Reached':
			self.go_home = self.go_home + 1
			
		elif tmp == 'Timeout':
			self.go_home = self.go_home + 1
			
		elif tmp == 'Error':
			self.go_home = self.go_home + 1
			
		
		if self.go_home >= 3:
			#Going Home
			rx = False
			self.go_home()
		
		if rx:
			tmp = self.tsvr.receive()
			if tmp is True or tmp == 'Transmission Complete':
				self.go_home = 0
			elif tmp == 'Handshaking Maximum Reached':
				
			elif tmp == 'Timeout':
				
			elif tmp == 'Error':
				

	def go_home(self):
		self.go_home = 0
		self.freq = '0'
		self.modulation = 'BPSK'
		self.timeout = '10' #(in seconds)
		#self.handshake = 5

class QueueLimitException(Exception):pass
