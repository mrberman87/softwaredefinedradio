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
import usb, time
sys.path.append("GPS") #includes GPS/ directory to use GPS_packet.py
from GPS_packet import GPS_packet
sys.path.append("../Data_Path")
from txrx_controller import txrx_controller


class ground_controls(abstractmodel.AbstractModel, threading.Thread):

	def __init__(self):
		abstractmodel.AbstractModel.__init__(self)
		threading.Thread.__init__(self)
		self.pendingRequest = threading.Event()
		self.cmd_qLock = threading.Lock()
		self.gps = GPS_packet("GPSD,P=0 0,A=0,V=0,E=0")
		self.go_home() #initialize the "GO HOME" type variables
		#setting up the usb controller
		self.dev = usb.core.find(idVendor=65534, idProduct=2)
		self.dev.set_configuration()
		self.temperature = '0'
		self.batt = '0'
		self.sigPower = '0'
		self.cmd_list = []
		self.MAX_COMMANDS=3
		self.fname = ''
		self.working_dir = os.path.expanduser('~') + '/softwaredefinedradio/src/ground_components'
		self.image = '/image.jpg'
		self.fft = '/fft.jpg'
		self.imageFileName = self.working_dir + self.image
		self.fftFileName = self.working_dir + self.fft
		self.gpsFileName = self.working_dir + '/gps.dat'
		self.teleFileName = self.working_dir + '/tele.dat'
		self.path = ''
		self.new_freq = 0
		self.new_modulation = ''
		self.new_timeout = 0
		#this sets up the transceiver
		self.tsvr = ''
		self.set_params()
	
	def __del__(self):
		self.dev.reset()
	
	
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
			
			if not cmd.startswith('All'):
				#figure out which command has been requested
				if cmd.startswith('GPS'):
					data = 'GPS'
					self.path = self.gpsFileName
				elif cmd.startswith('Image'):
					data = 'Image'
					self.path = self.image
				elif cmd.startswith('FFT'):
					data = 'FFT'
					self.path = self.fft
				elif cmd.startswith('Telemetry'):
					data = 'Telemetry'
					self.path = self.teleFileName
				elif cmd.startswith('Settings'):
					data = 'Settings'
					tmp  = cmd.split(' ')
					self.new_freq = int(tmp[1])
					self.new_modulation = tmp[2]
					self.new_timeout = int(tmp[3])
					self.new_handshake = int(tmp[4])
			
				rtn = self.send_data(data)
			else:
				rtn_gps = self.send_data('GPS')
				rtn_image = self.send_data('Image')
				rtn_fft = self.send_data('FFT')
				rtn_tele = self.send_data('Telemetry')
				rtn = rtn_gps and rtn_image and rtn_fft and rtn_tele
			
			#FIXME let the user know that something wasnt properly communicated between the ground and UAV
			#if not rtn:
				#...
			
			#handle getting everything properly
			self.removeCompletedCommand()
				


	"""Worker methods: These methods send and recieve data from the
	transeiver. They are I/O bound, which is why it is necessary to run them
	in a separate thread to keep the application responsive."""
	
	def send_data(self, data):
		print "Checking Data " + data
		self.fname = data + '.dat'

		if data == 'Settings':
			#print things into a file to be sent up and change data to the file path
			fd = open(self.fname)
			fd.write("settings\n")
			if self.new_freq != self.freq: fd.write("Freq: " + self.new_freq + '\n')
			if self.new_timeout != self.timeout: fd.write("Timeout: " + self.new_timeout + '\n')
			if self.new_handshake != self.handshake: fd.write("Hand_Max: " + self.new_handshake + '\n')
			if self.new_modulation != self.modulation: fd.write("Version: " + self.new_modulation + '\n')
			fd.close()
		
		tmp = self.tsvr.transmit(data)
		print tmp
		if tmp is True or tmp == 'Transmission Complete':
			self.go_home = 0
			#decode the data sent back down
			if data == 'Settings':
				if self.new_modulation == self.modulation:
					self.freq = self.new_freq
					self.modulation = self.new_modulation
					self.timeout = self.new_timeout
					self.handshake = self.new_handshake
					self.set_params()
				else:
					if self.new_freq != self.freq:
						self.freq = self.new_freq
						self.tsvr.set_frequency(self.freq)
					elif self.new_timeout != self.timeout:
						self.timeout = self.new_timeout
						self.tsvr.set_frame_time_out(self.timeout)
					elif self.new_handshake != self.handshake:
						self.handshake = self.new_handshake
						self.tsvr.set_hand_shaking_maximum(self.handshake)
				return True
		else:
			#self.go_home = self.go_home + 1
			self.report_error(tx_rx = 'Receiving', msg = tmp)
			return False
		
		if self.go_home >= 3:
			#Going Home
			rtn = True
			#tmp = self.tsvr.transmit("Going Home")
			#if not (tmp is True or tmp == 'Transmission Complete'):
			#	rtn = False
			#	#let user know of forcefull "GO HOME" state
			#	...
			self.go_home()
			#FIXME tell the user that this has occured somehow... possbily a popup
			#...
			return rtn
		
		print "\n\nHERE IS THE PATH...\n\n"
		print self.path
		self.tsvr.set_rx_path(self.path)
		print self.tsvr.rx_filename
		tmp = self.tsvr.receive()
		if tmp is True or tmp == 'Transmission Complete':
			self.go_home = 0
			#decode the data sent back down
			if data == 'GPS':
				f = open(self.gpsFileName)
				self.gps = GPS_packet(f.readline())
				f.close()
			elif data == 'Telemetry':
				f = open(self.teleFileName)
				self.temperature = int(f.readline().strip('\n').strip())
				self.batt = int(f.readline().strip('\n').strip())
				f.close()
		else:
			#self.go_home = self.go_home + 1
			self.report_error(tx_rx = 'Transmitting', msg = tmp)
	
	#this sets parameters for the txrx_controller
	#calling this will also initialze the controller
	def set_params(self):
		del self.tsvr
		self.dev.reset()
		time.sleep(2)
		self.tsvr = txrx_controller(fc=int(self.freq), centoff=11e3, foffset_tx=0, foffset_rx=50e3, hand_shaking_max = int(self.handshake),
			frame_time_out = int(self.timeout), work_directory=self.working_dir, version = self.modulation)
		time.sleep(2)
	
	def report_error(self, tx_rx, msg):
		rtn = "There was an error while " + tx_rx + " a transmission.\nThe error was as follows: \"" + msg + "\""
		#FIXME show this error message to the user in some fassion... possibly a popup message, or in the queue
		print rtn
		self.removeCompletedCommand()
	
	def go_home(self):
		self.go_home = 0
		self.freq = '440000000'
		self.modulation = 'BPSK'
		self.timeout = '45' #(in seconds)
		self.handshake = '5'

class QueueLimitException(Exception):pass
