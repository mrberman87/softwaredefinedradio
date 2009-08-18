#!/usr/bin/env python

import tx_rx_path
import packetizer
from gnuradio import gr

class txrx_controller():

	def __init__(self):
		self.event_list = ['EW', 'IN', 'PR', 'TC']
		self.bad_pkt_indices = list()
		self.data = list()
		self.data_temp = list()
		self.pkts = list()
		self.pkts_temp = list()
		self.payload_length = 1024
		self.pkt_count = None
		self.total_pkts = None
		self.payload = ''
		self.txrx_path = tx_rx_path.tx_rx_path()
		self.txrx_path.start()

########################################################################################
#					TRANSMITTER				       #
########################################################################################
	def transmit(self, data_source):
		#Tested
		#Untested: receiving packets to verify they are correct
		home_path = '/home/charles/softwaredefinedradio/src/'
		self.data = ''
		if data_source.count('/') > 0:
			fo = file(home_path + data_source, 'r')
			data = fo.read()
			fo.close()
			self.data = data
		else:
			self.data = data_source	
		make_pkts(self)
		transmit_pkts(self)
		return True


########################################################################################
#					RECEIVER				       #
########################################################################################
	def receive(self):
		#Tested: w/ USRP, need to confirm logic
		self.data = list()
		self.data_temp = list()
		temp_event = ''
		while True:
			#Untested: msgq retrieval
			if self.txrx_path.msg_queue_out.empty_p() is False:
				msgq_in(self)
				while len(self.data_temp) < self.pkt_count:
					self.data_temp.append('')
				self.data_temp.append(self.payload)
			elif len(self.data_temp) == self.total_pkts:
				#Tested: copy procedure
				if len(self.data) == 0:
					for i in range(len(self.data_temp)):
						self.data.append(self.data_temp.pop(0))
				else:
					temp_event = self.data_temp[0]
				if temp_event == '':
					self.data_temp = list()
					break
				if temp_event == event_list[2]:
					insert_missing_pkts(self)
					if frame_check(self) is True:
						self.data.pop(0)
						return ''.join(self.data)
				elif temp_event == event_list[1]:
					self.bad_pkt_indices = self.data_temp[1].split(':')
					handshaking_transmit(2)
					self.data_temp = list()	
				elif (self.data[0] == event_list[3] and temp_event == '') or temp_event == event_list[3]:
					cleanup(self)
					return True
				elif self.data[0] == event_list[1]:
					self.bad_pkt_indices = self.data[1].split(':')
					handshaking_transmit(2)
					self.data_temp = list()
				elif self.data[0] == event_list[0] or self.data[0] == '':
					if frame_check(self) is True:
						self.data.pop(0)
						return ''.join(self.data)				

########################################################################################
#				RECEIVER TOOLS					       #
########################################################################################

def frame_check(self):
	if self.data.count('') == 0:
		handshaking_transmit(self, 3)
		cleanup(self)
		return True
	else:
		bad_pkt_indexes(self)
		handshaking_transmit(self, 1)
		self.data_temp = list()
		return False

def insert_missing_pkts(self):
	#Tested
	for i in range(1, len(self.data_temp)):
		slice_total_count_pkt_count_payload(self.data_temp.pop(1))
		self.data.pop(self.pkt_count)
		self.data.insert(self.pkt_count, self.payload)			

def msgq_in(self):
	#Untested: msgq retrieval
	temp = ''
	temp = self.txrx_path.msg_queue_out.delete_head_nowait().to_string()
	slice_total_count_pkt_count_payload(temp)

def handshaking_transmit(self, event_index):
	handshaking_make_pkts(event_index)
	transmit_pkts(self)

def handshaking_make_pkts(self, event_index):
	#Tested
	if event_index == 1: #Transmitting Incomplete Transmission w/ 2nd packet having missing pkt numbers
		self.pkts_temp.append(packetizer.make_packet(self.event_list[event_index], 0, 2))
		self.pkts_temp.append(packetizer.make_packet(':'.join(self.bad_pkt_indices), 1, 2))
	elif event_index == 2: #Transmitting Packet Resend, w/ missing pkts from rcved inc. trans. pkt list
		total_pkts = len(self.bad_pkt_indices) + 1
		self.pkts_temp.append(packetizer.make_packet(self.event_list[event_index], 0, total_pkts))
		for i in range(len(self.bad_pkt_indices)):
			self.pkts_temp.append(self.pkts[int(self.bad_pkt_indices[i])])
	elif event_index == 3: #Transmitting Transmission Complete
		self.pkts_temp.append(packetizer.make_packet(self.event_list[event_index], 0, 1))
	

def bad_pkt_indexes(self):
	#Tested
	self.bad_pkt_indices = list()
	index = 0
	n_index = 0
	while len(self.bad_pkt_indices) < self.data.count(''):
		index = self.data.index('', n_index)
		self.bad_pkt_indices.append(str(index))
		n_index = index + 1

def slice_total_count_pkt_count_payload(self, temp):
	#Tested
	self.total_pkts = int(temp[:temp.index(":")])
	temp = temp[temp.index(":") + 1:]
	self.pkt_count = int(temp[:temp.index(":")])
	self.payload = temp[temp.index(":") + 1:]

########################################################################################
#				TRANSMITTER TOOLS				       #
########################################################################################

def make_pkts(self):
	#Tested
	total_pkts = len(self.data)/self.payload_length + 2
	if len(self.data)%2 == 0:
		total_pkts -= 1
	self.pkts.append(packetizer.make_packet(self.event_list[0], '0', total_pkts))
	for i in range(1, total_pkts):
		payload = self.data[:self.payload_length]
		self.data = self.data[self.payload_length:]
		self.pkts.append(packetizer.make_packet(payload, i, total_pkts))
	for i in range(len(self.pkts)):
		self.pkts_temp.append(self.pkts[i])

########################################################################################
#				COMMON OPERATIONS				       #
########################################################################################
def transmit_pkts(self):
	#Tested: Loop length correct
	#Untested: msgq insert
	for i in range(len(self.pkts_temp)):
		msg = gr.message_from_string(self.pkts_temp.pop(0))
		self.txrx_path.msg_queue_in.insert_tail(msg)

def cleanup(self):
	#No Testing needed
	self.bad_pkt_indices = list()
	self.pkts = list()
	self.pkts_temp = list()
	self.pkt_count = None
	self.total_pkts = None
	self.payload = ''
