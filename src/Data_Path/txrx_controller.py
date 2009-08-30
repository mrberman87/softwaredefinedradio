#!/usr/bin/env python

#Version 1.04

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
		#Tested
		#Untested: receiving packets to verify they are correct
		home_path = '/home/student/softwaredefinedradio-read-only/src/Data_Path/packetizer.py'
		self.data = ''
		if data_source == 'Error':
			self.make_pkts(error_event=True)
			self.transmit_pkts()
			return True
		elif data_source.count('/') > 0:
			fo = file(home_path, 'r')
			data = fo.read()
			fo.close()
			self.data = data
		else:
			self.data = data_source	
		self.make_pkts()
		if self.transmit_pkts():
			temp = self.receive()
		return True


########################################################################################
#					RECEIVER				       #
########################################################################################
	def receive(self):
		#Tested: w/ USRP, need to confirm logic
		time_0 = time.time()
		self.data = list()
		self.data_temp = list()
		self.hand_shaking_count = 0
		temp_event = ''
		while True:
			if self.txrx_path.msg_queue_out.empty_p() is False:
				time_0 = time.time()
				print "Found something in queue. ", time.ctime(time.time())
				#Tested: w/ USRP
				self.msgq_in()
				if self.initial_rcv:
					while len(self.data_temp) < self.pkt_count:
						self.data_temp.append('')
				elif self.initial_rcv is False and self.pkt_count != 0:
					self.pkt_num.append(self.pkt_count + ':' + self.payload)
				self.data_temp.append(self.payload)
			elif len(self.data_temp) == self.total_pkts:
				self.hand_shaking_count += 1
				self.total_pkts = None
				self.payload = ''
				self.pkt_count = None
				#Completed Frame, minimum rcvd last packet 1st time
				if self.initial_rcv:
					print "First receive. ", time.ctime(time.time())
					#Tested
					for i in range(len(self.data_temp)):
						self.data.append(self.data_temp.pop(0))
					self.initial_rcv = False
				#Completed 2nd + Frame, retrieving event
				else:
					print "2nd+ receive. ", time.ctime(time.time())
					#Untested: w/ USRP
					if self.data_temp[0] in self.event_list:
						temp_event = self.data_temp.pop(0)
						print "Temp Event: ", temp_event
					else:
						print "2nd + frame Unknown. Clearing data_temp.", time.ctime(time.time())
						temp_event = ''
						self.data_temp = list()
				#2nd + rcvd Packet Resend
				if temp_event == self.event_list[2]:
					temp_event = ''
					print "Receiving Packet Resend. ", time.ctime(time.time())
					#Untested: w/ USRP
					self.insert_missing_pkts()
					if self.frame_check():
						self.data.pop(0)
						#print ''.join(self.data)
						#return ''.join(self.data)
						return "Handshaking Complete.", time.ctime(time.time())
				#2nd + rcvd Incomplete Transmission
				elif temp_event == self.event_list[1]:
					temp_event = ''
					self.pkts_num = list()
					print "Received Incomplete Transmission. ", time.ctime(time.time())
					#Untested: w/ USRP
					self.bad_pkt_incices = (''.join(self.data_temp)).split(':')					
					self.handshaking_transmit(2)
					self.data_temp = list()
					self.cleanup()
				#Any, rcvd Transmission Complete
				elif self.data[0] == self.event_list[3] or temp_event == self.event_list[3]:
					print "Received Transmission Complete. ", time.ctime(time.time())
					#Untested: w/ USRP
					self.cleanup()
					self.pkts_num = list()
					print True
					return True
				#1st, rcvd Incomplete Transmission
				elif self.data[0] == self.event_list[1]:
					temp_data = ''
					print "Received Incomplete Transmission. ", time.ctime(time.time())
					#Untested: w/ USRP
					self.bad_pkt_indices = (''.join(self.data[1:])).split(':')
					self.handshaking_transmit(2)
					self.data_temp = list()
					self.cleanup()
				#1st, rcvd New Transmission or don't know Event
				elif self.data[0] == self.event_list[0] or self.data[0] == '':
					print "Received New Transmission or Unknown Event. ", time.ctime(time.time())
					#Tested
					if self.frame_check():
						self.data.pop(0)
						#print ''.join(self.data)
						#return ''.join(self.data)
						return "Handshaking complete."
				#Any, rcvd Error event
				elif self.data[0] == self.event_list[4] or temp_event == self.event_list[4]:
					self.cleanup()
					#print "Error"
					#return "Error"
					return "Error"
			elif int(time.time() - time_0) >= 30:
				temp_event = ''
				self.cleanup()
				return "Timeout"
			elif self.hand_shaking_count == 5:
				temp_event = ''
				self.cleanup()
				return "Handshaking maximum reached."
				

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
			print "No Errors, transmitting Transmission Complete. ", time.ctime(time.time())
			self.handshaking_transmit(3)
			self.cleanup()
			return True
		else:
			print "Missing Packets. Determining bad packet indexes. ", time.ctime(time.time())
			self.bad_pkt_indexes()
			print "Missing Packets: ", self.bad_pkt_indices
			self.handshaking_transmit(1)
			self.data_temp = list()
			self.cleanup()
			return False

	def insert_missing_pkts(self):
		#Tested: theoretical
		#Untested: w/ USRP
		temp = ''
		for i in self.pkts_num:
			self.pkt_count = i[:i.index(':')]
			self.payload = i[i.index(':') + 1:]
			self.data.pop(self.pkt_count)
			self.data.insert(self.pkt_count, self.payload)
		self.pkts_num = list()
		self.pkt_count = None
		self.payload = ''

	def msgq_in(self):
		#Tested: w/ USRP
		temp = ''
		temp = self.txrx_path.msg_queue_out.delete_head_nowait().to_string()
		self.slice_total_count_pkt_count_payload(temp)

	def handshaking_transmit(self, event_index):
		#Untested: w/ USRP
		self.handshaking_make_pkts(event_index)
		self.transmit_pkts()

	def handshaking_make_pkts(self, event_index):
		#Tested: theoretical
		#Untested: /w USRP
		bad_packet_indices = ''
		total_pkts = None
		payload = ''
		if event_index == 1: #Transmitting Incomplete Transmission w/ following packets having missing pkt numbers
			print "Transmitting Incomplete Transmission. ", time.ctime(time.time())
			bad_packet_indices = ':'.join(self.bad_pkt_indices)
			total_pkts = len(bad_packet_indices)/self.payload_length + 2
			if len(bad_packet_indices)%self.payload_length == 0:
				total_pkts -= 1
			self.pkts_temp.append(packetizer.make_packet(self.event_list[event_index], 0, total_pkts))
			for i in range(1, total_pkts):
				payload = bad_packet_indices[:self.payload_length]
				bad_packet_indices = bad_packet_indices[self.payload_length:]
				self.pkts_temp.append(packetizer.make_packet(payload, i, total_pkts))
				payload = ''
			self.bad_pkt_indices = list()
			bad_packet_indices = ''
			total_pkts = None
		elif event_index == 2: #Transmitting Packet Resend, w/ missing pkts from rcved inc. trans. pkt list
			print "Transmitting Packet Resend. ", time.ctime(time.time())
			total_pkts = None
			total_pkts = len(self.bad_pkt_indices) + 1
			self.pkts_temp.append(packetizer.make_packet(self.event_list[event_index], 0, total_pkts))
			for i in self.bad_pkt_indices:
				self.pkts_temp.append(packetizer.make_packet(self.data_split_for_pkts[int(i)], int(i), total_pkts))
			self.bad_pkt_indices = list()
		elif event_index == 3: #Transmitting Transmission Complete
			print "Transmitting Transmission Complete. ", time.ctime(time.time())
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
		print "Total Packets: ", self.total_pkts, "Time sliced. ", time.ctime(time.time())
		temp = temp[temp.index(":") + 1:]
		self.pkt_count = int(temp[:temp.index(":")])
		print "Packet Number: ", self.pkt_count, "Time sliced packet count. ", time.ctime(time.time())
		self.payload = temp[temp.index(":") + 1:]

########################################################################################
#				TRANSMITTER TOOLS				       #
########################################################################################

	def make_pkts(self, error_event=False):
		#Tested: w/ USRP
		total_pkts = None
		if error_event is False:
			self.data_split_for_pkts.append('')
			total_pkts = len(self.data)/self.payload_length + 2
			if len(self.data)%self.payload_length == 0:
				total_pkts -= 1
			self.pkts_temp.append(packetizer.make_packet(self.event_list[0], 0, total_pkts))
			for i in range(1, total_pkts):
				payload = self.data[:self.payload_length]
				self.data_split_for_pkts.append(payload)
				self.data = self.data[self.payload_length:]
				self.pkts_temp.append(packetizer.make_packet(payload, i, total_pkts))
		else:
			self.pkts_temp.append(packetizer.make_packet(self.event_list[4], 0, 1))

########################################################################################
#				COMMON TOOLS					       #
########################################################################################
	def transmit_pkts(self):
		#Tested: w/ USRP
		for i in range(len(self.pkts_temp)):
			msg = gr.message_from_string(self.pkts_temp.pop(0))
			self.txrx_path.msg_queue_in.insert_tail(msg)
		print "Queueing of all packets complete. ", time.ctime(time.time())
		self.txrx_path.msg_queue_in.insert_tail(gr.message_from_string('10101010'))
		self.txrx_path.msg_queue_in.insert_tail(gr.message_from_string('10101010'))
		return True

	def cleanup(self):
		#No Testing needed
		self.bad_pkt_indices = list()
		self.pkts_temp = list()
		self.pkt_count = None
		self.total_pkts = None
		self.payload = ''
