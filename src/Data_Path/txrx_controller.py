#!/usr/bin/env python

import tx_rx_path
import packetizer
from gnuradio import gr

class txrx_controller():

	def __init__(self, data='', payload_length=1024):

		self.transmission_incomplete = packetizer.make_packet('TI', 0)
		self.transmission_complete = packetizer.make_packet('TC', 0)
		self.last_event = ''
		self.new_event = ''
		self.tx = True
		self.data = data
		self.pkts = []
		self.pkts_copy = []
		self.response = ''
		self.payload_length = payload_length
		self.payload_count_list = []
		self.payload_count = ''
		self.total_payloads = 0
		tb = tx_rx_path.tx_rx_path()
		tb.Start()
		main()

	def main(self):
		while True:
			if self.data != '' and self.tx is True:
				total_number_of_pkts = len(data)/self.payload_length + 1
				make_pkts(transmission_header = str(total_number_of_pkts))
				transmit_pkts()
				self.tx = False

			while self.tx is False:
				if tb.msg_queue_out.empty_p() is False:
					temp = ''
					temp = tb.msg_queue_out.delete_head().to_string()
					strip_payload_count(temp)
					
					#Finish This
			
	def make_pkts(self, transmission_header=''):
		self.pkts.append(packetizer.make_packet(transmission_header, 0))
		for i in range(1, len(self.data)/self.payload_length + 3):
			payload = self.data[:self.payload_length]
			self.data = self.data[self.payload_length:]
			self.pkts.append(packetizer.make_packet(payload, i))
		self.pkts_copy = self.pkts

	def transmit_pkts(self):
		while len(self.pkts_copy) != 0:
			tb.msg_queue_in.insert_tail(gr.message_from_string(self.pkts_copy.pop(0)))
		
	def bad_pkts(self):
		pass

	def insert_data(self, data=''):
		self.data = data

	def strip_payload_count(self, temp):
		loc = 1
		for ch in temp:
			if ch == ':':
				self.response = temp[loc:]
				self.payload_count = ''.join(self.payload_count_list)
				break
			else:
				self.payload_count_list.append(ch)
			loc += 1
