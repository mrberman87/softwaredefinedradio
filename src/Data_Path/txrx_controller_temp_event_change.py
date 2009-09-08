#!/usr/bin/env python

#Version 2.0

import tx_rx_path
import packetizer
from gnuradio import gr
import time

class txrx_controller():

	def __init__(self, hand_shaking_max=5, frame_time_out=35, pay_load_length=128):
		self.event_list = ['N', 'I', 'P', 'C', 'E']
		self.hand_shaking_count = 0
		self.hand_shaking_maximum = hand_shaking_max
		self.frame_timeout = frame_time_out
		self.new_transmission_data = list()
		self.pkts_for_resend = list()
		self.data_split_for_pkts = list()
		self.payload_length = pay_load_length
		self.event = ''
		self.pkt_num = None
		self.total_pkts = None
		self.payload = ''
		self.txrx_path = tx_rx_path.tx_rx_path()
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
				fo = file(data_source, 'r')
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
					print 'New Transmission Event, ', 'Packet Number: ', self.pkt_num
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
					print 'Incomplete Transmission Event, ', 'Packet Number: ', self.pkt_num
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
					print 'Packet Resent Event, ', 'Packet Number: ', self.pkt_num
					if faking_frame_completion is False:
						self.rcvd_packet_resend()
					if self.pkt_num == (self.total_pkts - 1):
						faking_frame_completion = False
						self.hand_shaking_count += 1
						if self.frame_check():
							return True
				#Transmission Complete
				elif self.event == self.event_list[3]:
					print 'Transmission Complete'
					self.full_cleanup()
					return True
				#Error Event
				elif self.event == self.event_list[4]:
					print 'Error Event'
					self.full_cleanup()
					return 'Error'
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
			if (self.event in self.event_list) and (int(time.time() - time_0) >= 10):
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
			self.new_transmission_data.append(self.payload)

	#Handler of individual packets tagged with Incomplete Transmission Event
	def rcvd_incomplete_transmission(self):
		failed_pkts = (self.payload).split(':')
		num_failed_pkts = len(failed_pkts)
		for i in range(num_failed_pkts):
			self.pkts_for_resend.append(failed_pkts.pop(0))

	#Handler of individual packets tagged with Packet Resend Event
	def rcvd_packet_resend(self):
		fourth_colon = (self.payload).index(':')
		original_pkt_number = int(self.payload[: fourth_colon])
		temp_payload = self.payload[fourth_colon + 1 :]
		if self.new_transmission_data[original_pkt_number] == 'Failed':
			self.new_transmission_data.pop(original_pkt_number)
			self.new_transmission_data.insert(original_pkt_number, temp_payload)

	#Check the received frame to see if all packets are accounted for
	def frame_check(self):
		if self.new_transmission_data.count('Failed') == 0:
			try:
				fo = open('/home/sab/Desktop/p', 'w')
				fo.write(''.join(self.new_transmission_data))
				fo.close()
			except:
				print 'Invalid File Path for saving data.'
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
		first_colon = pkt.index(':')
		second_colon = pkt.index(':', first_colon + 1)
		third_colon = pkt.index(':', second_colon + 1)
		self.total_pkts = int(pkt[: first_colon])
		self.pkt_num = int(pkt[first_colon + 1 : second_colon])
		self.event = pkt[second_colon + 1 : third_colon]
		self.payload = pkt[third_colon + 1 :]

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
				self.transmit_pkts(packetizer.make_packet( \
					total_pkts, i, self.event_list[0], payload))
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
					total_pkts, i, self.event_list[event_index], pkt_payload)
				self.transmit_pkts(pkt)
		#Transmitting Packet Resend
		elif event_index == 2:
			counter = 0
			total_pkts = len(self.pkts_for_resend)
			for i in self.pkts_for_resend:
				payload = self.data_split_for_pkts[int(i)]
				pkt = packetizer.make_packet( \
					total_pkts, counter, self.event_list[event_index], \ 
					payload, original_payload_count = i)
				self.transmit_pkts(pkt)
				counter += 1
		#Transmitting Transmission Complete
		elif event_index == 3:
			pkt = packetizer.make_packet( \
				1, 0, self.event_list[event_index], \
				self.event_list[event_index])
			self.transmit_pkts(pkt)
		#Transmitting Error Event
		elif event_index == 4:
			pkt = packetizer.make_packet( \
				1, 0, self.event_list[event_index], \
				self.event_list[event_index])
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

	def set_frequency(self, new_freq, tx_rx):
		if tx_rx == 'tx':
			try:
				self.txrx_path.usrp_simple_sink_x_0.set_frequency( \
					new_freq, verbose=True)
			except:
				return False
		elif tx_rx == 'rx':
			try:
				self.txrx_path.usrp_simple_source_x_0.set_frequency( \
					new_freq, verbose=True)
			except:
				return False

