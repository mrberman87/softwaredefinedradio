#!/usr/bin/env python

import tx_rx_path
import packetizer
from gnuradio import gr

class txrx_controller():

	def __init__(self, data='', payload_length=1024):

		self.transmission_incomplete = packetizer.make_packet('TI', 0)
		self.transmission_complete = packetizer.make_packet('TC', 0)
		self.event = ''
		self.event_list = ['RY', 'PI', 'FF', 'BA', 'MP', 'IN', 'TC']
		self.return_list = ['Telemetry', 'Picture', 'FFT', 'Battery', \
			 'Temperature', 'Transmission Incomplete', 'Transmission Complete']
		self.tx = False
		self.bad_packet_indexes = []
		self.data = data
		self.pkts = []
		self.pkts_copy = []
		self.response = ''
		self.rx_packets = 0
		self.tx_packets = 0
		self.payload_length = payload_length
		self.payload_count_list = []
		self.payload_count = 0
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

			while self.tx is False:

				if tb.msg_queue_out.empty_p() is False:

					temp = ''
					temp = tb.msg_queue_out.delete_head().to_string()
					strip_payload_count(temp)
					self.event = self.response[:2]
					self.response = self.response[

					if self.event == event_list[0]:   #Telemetry
						#Tell Mikes Controller Telemetry Needed

					elif self.event == event_list[1]: #Picture
						#Tell Mikes Controller Picture Needed

					elif self.event == event_list[2]: #FFT
						#Tell Mikes Controller FFT Needed

					elif self.event == event_list[3]: #Battery
						#Tell Mikes Controller Battery Needed

					elif self.event == event_list[4]: #Temperature
						#Tell Mikes Controller Temperature Needed

					elif self.event == event_list[5]: #Transmission Incomplete
						#Previous Transmit incomplete
						bad_pkts()

					elif self.event == event_list[6]: #Transmission Complete
						#Previous Transmit Complete
						
					else: 
						#Event not found, Data Packet
			
	def make_pkts(self, transmission_header=''):

		self.pkts.append(packetizer.make_packet(transmission_header, 0))

		while data != '':

			payload = self.data[:self.payload_length]
			self.data = self.data[self.payload_length:]
			self.pkts.append(packetizer.make_packet(payload, i))

		self.pkts_copy = self.pkts

	def transmit_pkts(self):

		while len(self.pkts_copy) != 0:

			tb.msg_queue_in.insert_tail(gr.message_from_string(self.pkts_copy.pop(0)))
		
	def bad_pkts(self):
		
		self.bad_packet_indexes = self.response[3:].split(":")

		for i in self.bad_packet_indexes:

			self.pkts_copy.append(self.pkts[int(i)])

	def insert_data(self, data=''):

		self.data = data

	def strip_payload_count(self, temp):

		self.payload_count = int(temp[:temp.index(":")])
		self.response = temp[temp.index(":") + 1:]
