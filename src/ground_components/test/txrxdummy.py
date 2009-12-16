#!/usr/bin/env python

#Version 2.02

import time, os
from gnuradio import gr

class txrx_controller():

	def __init__(self, hand_shaking_max=5, frame_time_out=45, pay_load_length=128, \
			work_directory = os.path.expanduser('~') + '/Desktop', version='bpsk'):
		self.event_list = ['N', 'I', 'P', 'C', 'E', 'RTS', 'CTS']
		self.hand_shaking_maximum = hand_shaking_max
		self.working_directory = work_directory
		self.payload_length = pay_load_length
		self.frame_timeout = frame_time_out
		self.new_transmission_data = list()
		self.data_split_for_pkts = list()
		self.pkts_for_resend = list()
		self.hand_shaking_count = 0
		self.init_rcv = True
		self.total_pkts = None
		self.pkt_num = None
		self.payload = ''
		self.event = ''
		
########################################################################################
#					TRANSMITTER				       #
########################################################################################
	def transmit(self, data_source):
		try:
			fo = open(self.working_directory + data_source, 'r')
			temp_data = fo.read()
			fo.close()
		except:
			return False

		temp = self.receive()
		return temp

########################################################################################
#					RECEIVER				       #
########################################################################################
	def receive(self):
		while True:
			if True:
				return "my fake data string"
			if True:
				return 'Handshaking Maximum Reached'
			if True:
				return 'Timeout'



########################################################################################
#				USER TOOLS					       #
########################################################################################
	def set_payload_length(self, new_length):
		try:
			pass
		except:
			return False
	
	def set_hand_shaking_maximum(self, new_max):
		try:
			pass
		except:
			return False

	def set_frame_time_out(self, new_timeout):
		try:
			pass
		except:
			return False

	def set_frequency(self, new_freq, tx_rx):
		if tx_rx == 'tx':
			try:
				pass
			except:
				return False
		elif tx_rx == 'rx':
			try:
				pass
			except:
				return False

	def set_rx_path(self, new_path):
		if os.path.exists(new_path):
			self.work_directory = new_path
			return True
		return False

