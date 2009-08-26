#!/usr/bin/env python

#Version 1.03

import tx_rx_path
import packetizer
from gnuradio import gr

class txrx_controller():

	def __init__(self):
		self.event_list = ['NT', 'IN', 'PR', 'TC', 'ER']
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
		self.pkts = list()
		self.data = ''
		if data_source == 'Error':
			make_pkts(self, error_event=True)
			transmit_pkts(self)
			return True
		elif data_source.count('/') > 0:
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
			if self.txrx_path.msg_queue_out.empty_p() is False:
				#Tested: w/ USRP
				msgq_in(self)
				while len(self.data_temp) < self.pkt_count:
					self.data_temp.append('')
				self.data_temp.append(self.payload)
			elif len(self.data_temp) == self.total_pkts:
				#Completed Frame, minimum rcvd last packet 1st time
				if len(self.data) == 0:
					#Tested
					for i in range(len(self.data_temp)):
						self.data.append(self.data_temp.pop(0))
				#Completed 2nd + Frame, retrieving event
				else:
					#Untested: w/ USRP
					temp_event = self.data_temp[0]
					if temp_event == '':
						self.data_temp = list()
				#2nd + rcvd Packet Resend
				if temp_event == self.event_list[2]:
					#Untested: w/ USRP
					insert_missing_pkts(self)
					if frame_check(self) is True:
						self.data.pop(0)
						print ''.join(self.data)
				#2nd + rcvd Incomplete Transmission
				elif temp_event == self.event_list[1]:
					#Untested: w/ USRP
					self.bad_pkt_indices = self.data_temp[1].split(':')
					handshaking_transmit(2)
					self.data_temp = list()
					cleanup(self)
				#Any, rcvd Transmission Complete
				elif self.data[0] == self.event_list[3] or temp_event == self.event_list[3]:
					#Untested: w/ USRP
					cleanup(self)
					self.pkts = list()
					print True
				#1st, rcvd Incomplete Transmission
				elif self.data[0] == self.event_list[1]:
					#Untested: w/ USRP
					self.bad_pkt_indices = self.data[1].split(':')
					handshaking_transmit(2)
					self.data_temp = list()
					cleanup(self)
				#1st, rcvd New Transmission or don't know Event
				elif self.data[0] == self.event_list[0] or self.data[0] == '':
					#Tested
					if frame_check(self) is True:
						self.data.pop(0)
						print ''.join(self.data)
				#Any, rcvd Error event
				elif self.data[0] == self.event_list[4] or temp_event == self.event_list[4]:
					cleanup(self)
					print "Error"

	def set_freq(self, new_freq, tx_rx=''):
		#Tested: w/ USRP
		if tx_rx == 'tx':
			self.txrx_path.usrp_simple_sink_x_0.set_frequency(new_freq, verbose=True)
		elif tx_rx == 'rx':
			self.txrx_path.usrp_simple_source_x_0.set_frequency(new_freq, verbose=True)

	def time_out_pad(self):
		#Tested
		while len(self.data_temp) < self.total_pkts:
			self.data_temp.append('')

	def stop_trans(self):
		#Tested: Does not free up resource
		#Acts like a pause
		#Need to either kill process altogether, or determine how this actually works
		self.txrx_path.stop()
		self.txrx_path.wait()

	def start_trans(self):
		#Tested: need to confirm restart, no verbose at restart
		#Acts like a resume
		self.txrx_path.start()			

########################################################################################
#				RECEIVER TOOLS					       #
########################################################################################

def frame_check(self):
	#Tested: w/ USRP
	if self.data.count('') == 0:
		handshaking_transmit(self, 3)
		cleanup(self)
		return True
	else:
		bad_pkt_indexes(self)
		handshaking_transmit(self, 1)
		self.data_temp = list()
		cleanup(self)
		return False

def insert_missing_pkts(self):
	#Tested: theoretical
	#Untested: w/ USRP
	for i in range(1, len(self.data_temp)):
		slice_total_count_pkt_count_payload(self.data_temp.pop(1))
		self.data.pop(self.pkt_count)
		self.data.insert(self.pkt_count, self.payload)			

def msgq_in(self):
	#Tested: w/ USRP
	temp = ''
	temp = self.txrx_path.msg_queue_out.delete_head_nowait().to_string()
	slice_total_count_pkt_count_payload(temp)

def handshaking_transmit(self, event_index):
	#Untested: w/ USRP
	handshaking_make_pkts(event_index)
	transmit_pkts(self)

def handshaking_make_pkts(self, event_index):
	#Tested: theoretical
	#Untested: /w USRP
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
	#Untested: /w USRP
	self.bad_pkt_indices = list()
	index = 0
	n_index = 0
	while len(self.bad_pkt_indices) < self.data.count(''):
		index = self.data.index('', n_index)
		self.bad_pkt_indices.append(str(index))
		n_index = index + 1

def slice_total_count_pkt_count_payload(self, temp):
	#Tested: w/ USRP
	self.total_pkts = int(temp[:temp.index(":")])
	temp = temp[temp.index(":") + 1:]
	self.pkt_count = int(temp[:temp.index(":")])
	self.payload = temp[temp.index(":") + 1:]

########################################################################################
#				TRANSMITTER TOOLS				       #
########################################################################################

def make_pkts(self, error_event=False):
	#Tested: w/ USRP
	if error_event is False:
		total_pkts = len(self.data)/self.payload_length + 2
		if len(self.data)/self.payload_length == 0:
			total_pkts -= 1
		self.pkts.append(packetizer.make_packet(self.event_list[0], '0', total_pkts))
		for i in range(1, total_pkts):
			payload = self.data[:self.payload_length]
			self.data = self.data[self.payload_length:]
			self.pkts.append(packetizer.make_packet(payload, i, total_pkts))
		for i in range(len(self.pkts)):
			self.pkts_temp.append(self.pkts[i])
	else:
		self.pkts.append(packetizer.make_packet(self.event_list[4], '0', 1))
		self.pkts_temp.append(self.pkts[0])

########################################################################################
#				COMMON TOOLS					       #
########################################################################################
def transmit_pkts(self):
	#Tested: w/ USRP
	for i in range(len(self.pkts_temp)):
		msg = gr.message_from_string(self.pkts_temp.pop(0))
		self.txrx_path.msg_queue_in.insert_tail(msg)
	return True

def cleanup(self):
	#No Testing needed
	self.bad_pkt_indices = list()
	self.pkts_temp = list()
	self.pkt_count = None
	self.total_pkts = None
	self.payload = ''
