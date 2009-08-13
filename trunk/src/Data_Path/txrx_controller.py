#!/usr/bin/env python

import tx_rx_path
import packetizer
from gnuradio import gr

class txrx_controller():

	def __init__(self):
		self.event = ''
		self.event_list = ['EW', 'IN', 'PR', 'TC']
		self.tx = True
		self.bad_packet_indexes = list()
		self.data = ''
		self.pkts = list()
		self.pkts_copy = list()
		self.payload_length = 1024
		self.pkt_count = 0
		self.total_pkts = None
		self.payload = ''
		self.transmission_framer = ''
		tb = tx_rx_path.tx_rx_path()
		tb.Start()
			
	def receive(self):
		self.tx = False
		self.data = list()
		while self.tx is False:
			if tb.msg_queue_out.empty_p() is False:
				temp = ''
				temp = tb.msg_queue_out.delete_head_nowait().to_string()
				strip_pkt_count(temp)
				if self.pkt_count == 0:
					strip_total_pkt_count()
					self.data.append(self.payload)
				else:
					while len(self.data) < self.pkt_count:
						self.data.append('')
					self.data.append(self.payload)
			elif len(self.data) == self.total_pkts:			
				#Finish this
			#Need to add individual Event logic still
		cleanup()
		self.tx = True
	
	def transmit(self, data, payload_length=1024):
		if self.tx is True:
			cleanup()
			self.payload_length = payload_length
			self.data = data
			self.total_payloads = len(data)/self.payload_length + 2
			frame_pkt(0)
			make_pkts()
			transmit_pkts()
			return True
		else:
			return False

	def make_pkts(self):
		data_pkts = len(self.data)/self.payload_length + 2
		self.pkts.append(packetizer.make_packet(self.transmission_framer, 0))
		for i in range(1, data_pkts):
			payload = self.data[:self.payload_length]
			self.data = self.data[self.payload_length:]
			self.pkts.append(packetizer.make_packet(payload, i))
		self.pkts_copy = self.pkts

	def handshaking_transmit(self, event_index):
		self.total_payloads = 2
		frame_pkt(event_index)
		handshaking_make_pkts()
		transmit_pkts()

	def handshaking_make_pkts():	
		self.pckts_copy.append(packetizer.make_packet(self.transmission_framer, 0))
		bad_pkts()

	def bad_pkts(self):
		for i in self.bad_packet_indexes:
			self.pkts_copy.append(self.pkts[int(i)])

	def bad_pkt_indexes(self):
		index = 0
		while len(self.bad_packet_indexes) < self.data.count(''):
			index = self.data.index('', index + 1)
			self.bad_packet_indexes.append(str(index))				

	def transmit_pkts(self):
		while len(self.pkts_copy) != 0:
			tb.msg_queue_in.insert_tail(gr.message_from_string(self.pkts_copy.pop(0)))

	def strip_pkt_count(self, temp):
		self.pkt_count = int(temp[:temp.index(":")])
		self.payload = temp[temp.index(":") + 1:]

	def strip_total_pkt_count(self):
		self.total_pkts = int(self.payload[self.payload.index(":") + 1:])
		self.payload = self.payload[:self.payload.index(":")]

	def cleanup(self):
		self.event = ''
		self.bad_packet_indexes = list()
		self.data = ''
		self.pkts_copy = list()
		self.payload_count_list = list()
		self.payload_count = 0
		self.total_payloads = 0
		self.payload = ''
		self.transmission_framer = ''
	
	def frame_pkt(self, event_index):
		self.transmission_framer = self.event_list[event_index] + ":" + self.total_payloads
