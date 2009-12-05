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
		self.gpsFileName = '/GPS.txt'
		self.teleFileName = '/sensors.txt'
		self.path = ''
		self.new_freq = 0
		self.new_modulation = ''
		self.new_timeout = 0
		#this sets up the transceiver
		self.tsvr = ''
		self.set_params()
		os.system("touch Settings.dat")
		self.link_check = autoLinkCheck(self).start()
	
	def __del__(self):
		self.dev.reset()
	
	
	"""GUI responder methods: These are the only methods that should be
	called by the GUI"""	
	def addToQueue(self, cmd):
		if cmd == 'Clear':
			self.cmd_qLock.acquire()
			self.cmd_list = self.cmd_list[:1]
			self.cmd_qLock.release()
			self.update()
			return
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
			print cmd
			
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
				if tmp[1] != '#':
					self.new_freq = int(tmp[1])
				else:
					self.new_freq = ''
				self.new_modulation = tmp[2].lower()
				if tmp[3] != '#':
					self.new_timeout = int(tmp[3])
				else:
					self.new_timeout = ''
			elif cmd.startswith('Go Home'):
				self.go_home()
				self.set_params()
				self.removeCompletedCommand()
				self.removeCompletedCommand()
				self.removeCompletedCommand()
				continue
			elif cmd.startswith('Clear'):
				self.removeCompletedCommand()
				self.removeCompletedCommand()
				self.removeCompletedCommand()
			elif cmd.startswith('Keep'):
				data = 'ka'
			
			self.tsvr.set_rx_filename(self.path)
			rtn = self.send_data(data)
			
			#FIXME let the user know that something wasnt properly communicated between the ground and UAV
			#if not rtn:
			#...
			
			#handle getting everything properly
			self.removeCompletedCommand()
				


	"""Worker methods: These methods send and recieve data from the
	transeiver. They are I/O bound, which is why it is necessary to run them
	in a separate thread to keep the application responsive."""
	
	def send_data(self, data):
		self.fname = data
		
		if data == 'ka':
			return self.keep_alive()
		
		if data == 'Settings':
			#print things into a file to be sent up and change data to the file path
			self.fname = '/' + data + '.dat'
			fd = open(self.working_dir + self.fname, 'w')
			fd.write("Settings\n")
			if self.new_freq != int(float(self.freq)) and self.new_freq != '':
				fd.write("Freq: " + str(self.new_freq) + '\n')
			if self.new_timeout != int(self.timeout) and self.new_timeout != '':
				fd.write("Timeout: " + str(self.new_timeout) + '\n')
			if self.new_modulation.lower() != self.modulation.lower():
				fd.write("Version: " + self.new_modulation + '\n')
			fd.close()
		
		print "Path: ", self.tsvr.working_directory + self.fname
		tmp = self.tsvr.transmit(self.fname)
		print tmp
		if tmp == True or tmp == 'Transmission Complete':
			#decode the data sent back down
			if data == 'Settings':
				print "Checking Settings..."
				#temp = self.tsvr.transmit('Execute')
				#if temp == True:
				if self.new_modulation.lower() != self.modulation.lower():
					if str(self.new_freq) != '':
						self.freq = str(self.new_freq)
					if str(self.new_timeout) != '':
						self.timeout = str(self.new_timeout)				
					self.modulation = self.new_modulation
					self.set_params()
				else:
					if str(self.new_freq) != self.freq and str(self.new_freq) != '':
						self.freq = str(self.new_freq)
						self.tsvr.set_frequency(int(self.freq))
					if str(self.new_timeout) != self.timeout and str(self.new_timeout) != '':
						self.timeout = str(self.new_timeout)
						self.tsvr.set_frame_time_out(int(self.timeout))
				return True
		else:
			self.report_error(tx_rx = 'Receiving', msg = tmp)
			return False
		
		self.tsvr.set_rx_filename(self.path)
		if data == "Settings":
			return
		tmp = self.tsvr.receive()
		if tmp == True or tmp == 'Transmission Complete':
			#decode the data sent back down
			if data == 'GPS':
				f = open(self.working_dir + self.gpsFileName, 'r')
				self.gps = GPS_packet(f.readline())
				f.close()
			elif data == 'Telemetry':
				f = open(self.working_dir + self.teleFileName, 'r')
				self.temperature = f.readline().strip('\n').strip()
				self.batt = f.readline().strip('\n').strip()
				f.close()
		else:
			self.report_error(tx_rx = 'Transmitting', msg = tmp)
	
	#this sets parameters for the txrx_controller
	#calling this will also initialze the controller
	def set_params(self):
		del self.tsvr
		self.dev.reset()
		time.sleep(2)
		self.tsvr = txrx_controller(fc=int(self.freq), centoff=3.31e3, foffset_tx=0, foffset_rx=50e3,
			frame_time_out = int(self.timeout), work_directory=self.working_dir, version=self.modulation.lower())
		time.sleep(2)

	def report_error(self, tx_rx, msg):
		rtn = "There was an error while " + tx_rx + " a transmission.\nThe error was as follows: \"" + msg + "\""
		#FIXME show this error message to the user in some fassion... possibly a popup message, or in the queue
		print rtn
		self.removeCompletedCommand()
	
	def go_home(self):
		self.freq = '440000000'
		self.modulation = 'bpsk'
		self.timeout = '45' #(in seconds)
	
	def keep_alive(self):
		self.tsvr.set_frame_time_out(3)
		for i in range(int((int(self.timeout)*2)/3)):
			temp = self.tsvr.transmit('ka')
			if temp == 'ka':
				self.tsvr.set_frame_time_out(int(self.timeout))
				return 'Link Alive.'
		self.addToQueue('Go Home')

class QueueLimitException(Exception):pass

class autoLinkCheck(threading.Thread):
	def __init__(self, ground_controller):
		threading.Thread.__init__(self)
		self.grnd = ground_controller
		self.KA_timer = 10
	
	def run(self):
		while True:
			time.sleep(self.KA_timer)
			self.grnd.cmd_qLock.acquire()
			tmp = len(self.grnd.cmd_list)
			self.grnd.cmd_qLock.release()
			if not tmp > 0:
				self.grnd.addToQueue('Keep Alive')
				self.grnd.update()
				#self.KA_timer = int(self.grnd.timeout)*2 + 5
