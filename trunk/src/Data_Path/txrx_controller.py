#!/usr/bin/env python

#Version 1.05

import tx_rx_path
import packetizer
from gnuradio import gr
import time

class txrx_controller():

	def __init__(self):
		self.event_list = ['NT', 'IN', 'PR', 'TC', 'ER']
		self.initial_rcv = True
		self.bad_pkt_indices = list()
		self.hand_shaking_count = 0
		self.data = list()
		self.data_temp = list()
		self.data_split_for_pkts = list()
		self.pkt_num = list()
		self.pkts_temp = list()
		self.payload_length = 128
		self.pkt_count = None
		self.total_pkts = None
		self.payload = ''
		self.txrx_path = tx_rx_path.tx_rx_path()
		self.txrx_path.start()

########################################################################################
#					TRANSMITTER				       #
########################################################################################
	def transmit(self, data_source):
		self.cleanup()
		if data_source == 'Error':
			self.make_pkts(error_event=True)
			return True
		elif data_source.count('/') > 0:
			fo = file(data_source, 'r')
			self.data = fo.read()
			fo.close()
		else:
			self.data = data_source	
		self.make_pkts()
		temp = self.receive()
		return temp

########################################################################################
#					RECEIVER				       #
########################################################################################
	def receive(self):
		time_0 = time.time()
		self.data = list()
		self.data_temp = list()
		self.hand_shaking_count = 0
		temp_event = ''
		while True:
			if self.txrx_path.msg_queue_out.empty_p() is False:
				time_0 = time.time()
				self.msgq_in()
				if self.initial_rcv:
					while len(self.data_temp) < self.pkt_count:
						self.data_temp.append('')
				else:
					time_1 = time.time()
					self.pkt_num.append(str(self.pkt_count) + ':' + self.payload)
				self.data_temp.append(self.payload)
				self.pkt_count = None
				self.payload = ''
			elif len(self.data_temp) == self.total_pkts:
				self.hand_shaking_count += 1
				self.total_pkts = None
				if self.initial_rcv:
					for i in range(len(self.data_temp)):
						self.data.append(self.data_temp.pop(0))
					self.initial_rcv = False
					time_1 = time.time()
				else:
					self.pkt_num.pop(0)
					if self.data_temp[0] in self.event_list:
						temp_event = self.data_temp.pop(0)
					else:
						temp_event = ''
						self.data_temp = list()
						self.pkt_num = list()
				if temp_event == self.event_list[2]:
					temp_event = ''
					self.insert_missing_pkts()
					if self.frame_check():
						return "Handshaking Complete."
				elif temp_event == self.event_list[1]:
					temp_event = ''
					self.pkts_num = list()
					self.bad_pkt_incices = (''.join(self.data_temp)).split(':')
					self.handshaking_transmit(2)
					self.data_temp = list()
				elif self.data[0] == self.event_list[3] or temp_event == self.event_list[3]:
					self.cleanup()
					return True
				elif self.data[0] == self.event_list[1]:
					self.bad_pkt_indices = (''.join(self.data[1:])).split(':')
					self.handshaking_transmit(2)
					self.data_temp = list()
				elif self.data[0] == self.event_list[0] or self.data[0] == '':
					if self.frame_check():
						return "Handshaking complete."
				elif self.data[0] == self.event_list[4] or temp_event == self.event_list[4]:
					self.cleanup()
					return "Error"
			#Need testing to make sure this handshaking timeout padding works correctly.
			elif int(time.time() - time_1) >= 5 and self.initial_rcv is False:
				self.data_temp = list()
				if self.total_pkts != None:
					while len(self.data_temp) < self.total_pkts:
						self.data_temp.append('')
			elif int(time.time() - time_0) >= 35:
				temp_event = ''
				self.cleanup()
				return "Timeout"
			elif self.hand_shaking_count == 5:
				temp_event = ''
				self.cleanup()
				return "Handshaking maximum reached."
				
	def set_freq(self, new_freq, tx_rx=''):
		if tx_rx == 'tx':
			self.txrx_path.usrp_simple_sink_x_0.set_frequency(new_freq, verbose=True)
		elif tx_rx == 'rx':
			self.txrx_path.usrp_simple_source_x_0.set_frequency(new_freq, verbose=True)

	#def time_out_pad(self):
		#while len(self.data_temp) < self.total_pkts:
			#self.data_temp.append('')

	#def stop_trans(self):
		#self.txrx_path.stop()
		#self.txrx_path.wait()

	#def start_trans(self):
		#self.txrx_path.start()			

########################################################################################
#				RECEIVER TOOLS					       #
########################################################################################
	def frame_check(self):
		if self.data.count('') == 0:
			fo = open('/home/student/Desktop/p', 'w')
			fo.write(''.join(self.data[1:]))
			fo.close()
			self.handshaking_transmit(3)
			self.cleanup()
			return True
		else:
			self.bad_pkt_indexes()
			self.handshaking_transmit(1)
			self.data_temp = list()
			return False

	def insert_missing_pkts(self):
		self.pkt_count = None
		self.payload = ''
		for i in self.pkt_num:
			self.pkt_count = int(i[:i.index(':')])
			self.payload = i[i.index(':') + 1:]
			self.data.pop(self.pkt_count)
			self.data.insert(self.pkt_count, self.payload)
		self.pkt_num = list()
		self.pkt_count = None
		self.payload = ''

	def msgq_in(self):
		temp = ''
		temp = self.txrx_path.msg_queue_out.delete_head_nowait().to_string()
		self.slice_total_count_pkt_count_payload(temp)

	def handshaking_transmit(self, event_index):
		total_pkts = None
		payload = ''
		if event_index == 1:
			bad_packet_indices = ''
			bad_packet_indices = ':'.join(self.bad_pkt_indices)
			total_pkts = len(bad_packet_indices)/self.payload_length + 2
			if len(bad_packet_indices)%self.payload_length == 0:
				total_pkts -= 1
			self.transmit_pkts(packetizer.make_packet(self.event_list[event_index], 0, total_pkts))
			for i in range(1, total_pkts):
				payload = bad_packet_indices[:self.payload_length]
				bad_packet_indices = bad_packet_indices[self.payload_length:]
				self.transmit_pkts(packetizer.make_packet(payload, i, total_pkts))
				payload = ''
			self.transmit_pkts('1010101010101010')
			self.bad_pkt_indices = list()
		elif event_index == 2:
			total_pkts = None
			total_pkts = len(self.bad_pkt_indices) + 1
			self.transmit_pkts(packetizer.make_packet(self.event_list[event_index], 0, total_pkts))
			for i in self.bad_pkt_indices:
				self.transmit_pkts(packetizer.make_packet(self.data_split_for_pkts[int(i)], int(i), total_pkts))
			self.transmit_pkts('1010101010101010')
			self.bad_pkt_indices = list()
		elif event_index == 3:
			self.transmit_pkts(packetizer.make_packet(self.event_list[event_index], 0, 1))
			self.transmit_pkts('1010101010101010')
	
	def bad_pkt_indexes(self):
		self.bad_pkt_indices = list()
		index = 0
		n_index = 0
		while len(self.bad_pkt_indices) < self.data.count(''):
			index = self.data.index('', n_index)
			self.bad_pkt_indices.append(str(index))
			n_index = index + 1

	def slice_total_count_pkt_count_payload(self, temp):
		self.total_pkts = int(temp[:temp.index(":")])
		temp = temp[temp.index(":") + 1:]
		self.pkt_count = int(temp[:temp.index(":")])
		self.payload = temp[temp.index(":") + 1:]

########################################################################################
#				TRANSMITTER TOOLS				       #
########################################################################################
	def make_pkts(self, error_event=False):
		total_pkts = None
		if error_event is False:
			self.data_split_for_pkts.append('NT')
			total_pkts = len(self.data)/self.payload_length + 2
			if len(self.data)%self.payload_length == 0:
				total_pkts -= 1
			self.transmit_pkts(packetizer.make_packet(self.event_list[0], 0, total_pkts))
			for i in range(1, total_pkts):
				payload = self.data[:self.payload_length]
				self.data_split_for_pkts.append(payload)
				self.data = self.data[self.payload_length:]
				self.transmit_pkts(packetizer.make_packet(payload, i, total_pkts))
			self.transmit_pkts('1010101010101010')
		else:
			self.transmit_pkts(packetizer.make_packet(self.event_list[4], 0, 1))
			self.transmit_pkts('1010101010101010')

########################################################################################
#				COMMON TOOLS					       #
########################################################################################
	def transmit_pkts(self, msg):
		msg_0 = gr.message_from_string(msg)
		self.txrx_path.msg_queue_in.insert_tail(msg_0)

	def cleanup(self):
		self.initial_rcv = True
		self.bad_pkt_indices = list()
		self.hand_shaking_count = 0
		self.data = list()
		self.data_temp = list()
		self.data_split_for_pkts = list()
		self.pkt_num = list()
		self.payload_length = 128
		self.pkt_count = None
		self.total_pkts = None
		self.payload = ''
