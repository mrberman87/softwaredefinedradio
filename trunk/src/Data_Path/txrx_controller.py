#!/usr/bin/env python

#Version 2.02

import txrx_dbpsk
import txrx_dqpsk
import txrx_d8psk 
import time, os
import packetizer
from gnuradio import gr

class txrx_controller():

	def __init__(self, fc, centoff, foffset_tx, foffset_rx, hand_shaking_max=5, frame_time_out=45, 
			pay_load_length=128, work_directory = os.path.expanduser('~') + '/Desktop', 
			version='bpsk', rx_file='/rx_data'):
		self.event_list = ['N', 'I', 'P', 'C', 'E']
		self.hand_shaking_maximum = hand_shaking_max
		self.working_directory = work_directory
		self.payload_length = pay_load_length
		self.frame_timeout = frame_time_out
		self.new_transmission_data = list()
		self.data_split_for_pkts = list()
		self.pkts_for_resend = list()
		self.rx_filename = rx_file
		self.rx_osc_f_offset = -50e3
		self.hand_shaking_count = 0
		self.total_pkts = None
		self.scheme = version
		self.pkt_num = None
		self.payload = ''
		self.event = ''
		self.fc = fc
		self.carrier_offset = centoff
		self.rx_f_offset = foffset_rx
		self.tx_f_offset = foffset_tx
		#If UAV:	rx = -50e3,	tx = 100e3, 	cent = 0, 	fc = 440e6
		#if Ground:	rx =  50e3,	tx = 0,		cent = 11e3,	fc = 440e6
		if   version == 'bpsk':
			self.txrx_path = txrx_dbpsk.tx_rx_path(
				f_offset_rx=self.rx_f_offset, f_offset_tx=self.tx_f_offset, 
				cent_off=self.carrier_offset, f_c=self.fc)
			self.txrx_path.start()
		elif version == 'qpsk':
			self.txrx_path = txrx_dqpsk.tx_rx_path(
				f_offset_rx=self.rx_f_offset, f_offset_tx=self.tx_f_offset, 
				cent_off=self.carrier_offset, f_c=self.fc)
			self.txrx_path.start()
		elif version == '8psk':
			self.txrx_path = txrx_d8psk.tx_rx_path(
				f_offset_rx=self.rx_f_offset, f_offset_tx=self.tx_f_offset, 
				cent_off=self.carrier_offset, f_c=self.fc)
			self.txrx_path.start()

########################################################################################
#					TRANSMITTER				       #
########################################################################################
	def transmit(self, data_source):
		self.full_cleanup()		
		if data_source == 'Error':
			self.make_pkts(4)
			return True
		elif data_source.count('/') > 0:
			try:
				fo = open(self.working_directory + data_source, 'r')
				temp_data = fo.read()
				fo.close()
			except:
				return False
		else:
			temp_data = data_source	
		self.make_pkts(0, temp_data)
		temp = self.receive()
		return temp

########################################################################################
#					RECEIVER				       #
########################################################################################
	def receive(self):
		time_0 = time.time()
		self.new_transmission_data = list()
		self.hand_shaking_count = 0
		faking_frame_completion = False
		while True:
			if (self.txrx_path.msg_queue_out.empty_p() is False) or faking_frame_completion:
				if faking_frame_completion is False:
					time_0 = time.time()
					queue_item = self.msgq_in()
					self.slice_packet(queue_item)
				#New Transmission Event
				if self.event == self.event_list[0]:
					print "N : ", self.pkt_num
					if faking_frame_completion:
						self.rcvd_new_transmission(True)
					else:
						self.rcvd_new_transmission()
					if self.pkt_num == (self.total_pkts - 1):
						faking_frame_completion = False
						self.hand_shaking_count += 1
						if self.frame_check():
							return True
				#Incomplete Transmission Event
				elif self.event == self.event_list[1]:
					print "I : ", self.pkt_num
					if faking_frame_completion is False:
						self.rcvd_incomplete_transmission()
					if self.pkt_num == (self.total_pkts - 1):
						faking_frame_completion = False
						self.hand_shaking_count += 1	
						self.make_pkts(2)
						self.event_cleanup()
						self.pkts_for_resend = list()
				#Packet Resend Event
				elif self.event == self.event_list[2]:
					print "P : ", self.pkt_num
					if faking_frame_completion is False:
						self.rcvd_packet_resend()
					if self.pkt_num == (self.total_pkts - 1):
						faking_frame_completion = False
						self.hand_shaking_count += 1
						if self.frame_check():
							return True
				#Transmission Complete
				elif self.event == self.event_list[3]:
					print "C : ", self.pkt_num
					self.full_cleanup()
					return True
				#Error Event
				elif self.event == self.event_list[4]:
					self.full_cleanup()
					return 'Error'
				#Unknown Event
				else:
					self.event_cleanup()
			#Used to keep the total number of receives to a maximum
			if self.hand_shaking_count == self.hand_shaking_maximum:
				self.full_cleanup()
				return 'Handshaking Maximum Reached'
			#Used to give control back to the outside controller
			if int(time.time() - time_0) >= self.frame_timeout:
				self.full_cleanup()
				return 'Timeout'
			#Used to fake a frame completion for handshaking
			if (self.event in self.event_list) and (int(time.time() - time_0) >= 5):
				faking_frame_completion = True
				self.pkt_num = self.total_pkts - 1

########################################################################################
#				RECEIVER TOOLS					       #
########################################################################################
	#Handler of individual packets tagged with New Transmission Event
	def rcvd_new_transmission(self, faking_frame_completion = False):
		while len(self.new_transmission_data) < self.pkt_num:
			self.new_transmission_data.append('Failed')
		if faking_frame_completion:
			self.new_transmission_data.append('Failed')
		else:
			if len(self.payload) <= self.payload_length:
				self.new_transmission_data.append(self.payload)
			else:
				self.new_transmission_data.append('Failed')

	#Handler of individual packets tagged with Incomplete Transmission Event
	def rcvd_incomplete_transmission(self):
		if len(self.payload) <= self.payload_length:
			failed_pkts = self.payload.split(':')
			num_failed_pkts = len(failed_pkts)
		else:
			max_splits = self.payload_length/4
			failed_pkts = self.payload.split(':', max_splits)
			if len(failed_pkts[-1]) > 3:
				failed_pkts.pop(-1)

			num_failed_pkts = len(failed_pkts)
		for i in range(num_failed_pkts):
			self.pkts_for_resend.append(failed_pkts.pop(0))


	#Handler of individual packets tagged with Packet Resend Event
	def rcvd_packet_resend(self):
		self.payload = self.payload.split(':', 1)
		original_pkt_number = int(self.payload.pop(0))
		temp_payload = self.payload.pop(0)
		if (len(temp_payload) <= self.payload_length) and (self.new_transmission_data[original_pkt_number] == 'Failed'):
			self.new_transmission_data.pop(original_pkt_number)
			self.new_transmission_data.insert(original_pkt_number, temp_payload)

	#Check the received frame to see if all packets are accounted for
	def frame_check(self):
		temp = self.new_transmission_data.count('Failed')
		print "Number of Failed Packets: ", temp
		if temp == 0:
			try:
				fo = open(self.working_directory + self.rx_filename, 'w')
				fo.write(''.join(self.new_transmission_data))
				fo.close()
			except:
				pass
			self.make_pkts(3)
			self.full_cleanup()
			return True
		else:
			self.make_pkts(1)
			self.event_cleanup()
			return False

	#Return the first item in the flow graph's Receive Queue
	def msgq_in(self):
		return self.txrx_path.msg_queue_out.delete_head_nowait().to_string()

	#Determine the missing packet indices in New Transmission Data
	def bad_pkt_indices(self):
		index = 0
		n_index = 0
		missing_pkts = list()
		while len(missing_pkts) < self.new_transmission_data.count('Failed'):
			index = self.new_transmission_data.index('Failed', n_index)
			missing_pkts.append(str(index))
			n_index = index + 1
		return missing_pkts

	#Remove, Total Number of Packets in the Frame, Packet Number, Event, and Payload
	def slice_packet(self, pkt):
		pkt = pkt.split(':', 3)
		self.total_pkts = int(pkt.pop(0))
		self.pkt_num = int(pkt.pop(0))
		self.event = pkt.pop(0)
		self.payload = pkt.pop(0)

########################################################################################
#				COMMON TOOLS					       #
########################################################################################
	def make_pkts(self, event_index, temp_data=''):
		#Transmitting New Transmission
		if event_index == 0:
			total_pkts = len(temp_data)/self.payload_length + 1
			if len(temp_data)%self.payload_length == 0:
				total_pkts -= 1
			for i in range(total_pkts):
				payload = temp_data[:self.payload_length]
				self.data_split_for_pkts.append(payload)
				temp_data = temp_data[self.payload_length:]
				pkt = packetizer.make_packet( total_pkts, i, 
					self.event_list[0], payload, scheme = self.scheme)
				self.transmit_pkts(pkt)
		#Transmitting Incomplete Transmission
		elif event_index == 1:
			bad_pkts = self.bad_pkt_indices()
			max_items_per_packet = self.payload_length/4
			total_pkts = len(bad_pkts)/max_items_per_packet + 1
			if len(bad_pkts)%(max_items_per_packet) == 0:
				total_pkts -= 1
			for i in range(total_pkts):
				payload = bad_pkts[:max_items_per_packet]
				bad_pkts = bad_pkts[max_items_per_packet:]
				pkt_payload = ':'.join(payload)
				pkt = packetizer.make_packet( \
					total_pkts, i, self.event_list[event_index], pkt_payload, 
					scheme = self.scheme)
				self.transmit_pkts(pkt)
		#Transmitting Packet Resend
		elif event_index == 2:
			counter = 0
			total_pkts = len(self.pkts_for_resend)
			for i in self.pkts_for_resend:
				payload = self.data_split_for_pkts[int(i)]
				pkt = packetizer.make_packet( \
					total_pkts, counter, self.event_list[event_index],  
					payload, scheme = self.scheme, original_payload_count = i)
				self.transmit_pkts(pkt)
				counter += 1
		#Transmitting: Transmission Complete, Error Event, Ready to Send, Clear to Send in order
		elif event_index == 3:
			pkt = packetizer.make_packet( \
				1, 0, self.event_list[event_index], 
				self.event_list[event_index], scheme = self.scheme)
			self.transmit_pkts(pkt)
		#Transmitting Error Event
		elif event_index == 4:
			pkt = packetizer.make_packet( \
				1, 0, self.event_list[event_index], 
				self.event_list[event_index], scheme = self.scheme)
			self.transmit_pkts(pkt)

	#Queue a packet in the transceiver flow graph
	def transmit_pkts(self, msg):
		msg_0 = gr.message_from_string(msg)
		self.txrx_path.msg_queue_in.insert_tail(msg_0)

	def event_cleanup(self):
		self.event = ''
		self.payload = ''
		self.pkt_num = None
		self.total_pkts = None

	def full_cleanup(self):
		self.hand_shaking_count = 0
		self.new_transmission_data = list()
		self.pkts_for_resend = list()
		self.data_split_for_pkts = list()
		self.event = ''
		self.pkt_num = None
		self.total_pkts = None
		self.payload = ''

########################################################################################
#				USER TOOLS					       #
########################################################################################
	def set_payload_length(self, new_length):
		try:
			self.payload_length = int(new_length)
		except:
			return False
	
	def set_hand_shaking_maximum(self, new_max):
		try:
			self.hand_shaking_maximum = int(new_max)
		except:
			return False

	def set_frame_time_out(self, new_timeout):
		try:
			self.frame_timeout = int(new_timeout)
		except:
			return False

	def set_frequency(self, fc, tx_rx, change_c_offset=False, centoff=0, change_rx_offset=False, 
			foffset_rx=0, change_tx_offset=False, foffset_tx=0,):

		if fc > 400.025e6 and fc < 499.075e6:
			self.fc = fc
		else:
			return "Invalid Carrier Frequency."
		if change_c_offset:
			self.carrier_offset = centoff
		if change_rx_offset:
			self.rx_f_offset = foffset_rx
			self.txrx_path.gr_sig_source_x_0_0.set_frequency(self.rx_osc_f_offset - 50e3)
		if change_tx_offset:
			self.tx_f_offset = foffset_tx

		if tx_rx == 'tx':
			tx_freq = self.fc + self.carrier_offset + self.tx_f_offset
			try:
				self.txrx_path.usrp_simple_sink_x_0.set_frequency( \
					tx_freq, verbose=True)
			except:
				return False
		elif tx_rx == 'rx':
			rx_freq = self.fc + self.carrier_offset + self.rx_f_offset
			try:
				self.txrx_path.usrp_simple_source_x_0.set_frequency( \
					rx_freq, verbose=True)
			except:
				return False
		elif tx_rx == 'txrx':
			rx_freq = self.fc + self.carrier_offset + self.rx_f_offset
			tx_freq = self.fc + self.carrier_offset + self.tx_f_offset
			try:
				self.txrx_path.usrp_simple_source_x_0.set_frequency( \
					rx_freq, verbose=True)
			except:
				return False
			try:
				self.txrx_path.usrp_simple_sink_x_0.set_frequency( \
					tx_freq, verbose=True)
			except:
				return False

	def set_rx_path(self, new_path):
		if os.path.exists(new_path):
			self.work_directory = new_path
			return True
		return False

	def set_rx_filename(self, new_name):
		self.rx_filename = new_name
