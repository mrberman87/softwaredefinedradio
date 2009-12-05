#!/usr/bin/env python

import dpsk
import time, os
import packetizer
from gnuradio import gr

class txrx_controller():

	def __init__(self, fc, centoff, foffset_tx, foffset_rx, frame_time_out=45, 
			work_directory = os.getcwd(), version='bpsk', rx_file='/rx_data'):
		self.event_list = ['N', 'I', 'P', 'C', 'E', 'K']
		self.version_list = ['bpsk', 'qpsk']
		self.hand_shaking_maximum = 15
		self.working_directory = work_directory
		self.payload_length = 128
		self.frame_timeout = frame_time_out
		self.new_transmission_data = list()
		self.data_split_for_pkts = list()
		self.pkts_for_resend = list()
		self.rx_filename = rx_file
		self.hand_shaking_count = 0
		self.total_pkts = None
		self.scheme = version
		self.pkt_num = None
		self.payload = ''
		self.event = ''
		fd = open(os.path.expanduser('~') + '/softwaredefinedradio/src/ground_components/log.dat', 'w')
		fd.write('')
		fd.close()
		self.fc = fc
		self.carrier_offset = centoff
		self.rx_f_offset = foffset_rx
		self.tx_f_offset = foffset_tx
		#If UAV:	rx = -50e3,	tx = 100e3, 	cent = 0, 	fc = 440e6
		#if Ground:	rx =  50e3,	tx = 0,		cent = 11e3,	fc = 440e6
		self.txrx_path = dpsk.tx_rx_path(self.fc, self.carrier_offset, 
			self.tx_f_offset, self.rx_f_offset, self.scheme)
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
				self.make_pkts(0, temp_data)
			except:
				return False
		elif data_source.lower() == 'ka':
			self.make_pkts(5)
		else:
			self.make_pkts(0, data_source)
		return self.receive()

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
					self.slice_packet(self.msgq_in())
				#New Transmission Event
				if self.event == self.event_list[0]:
					#print "N : ", self.pkt_num
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
					#print "I : ", self.pkt_num
					if faking_frame_completion is False:
						self.rcvd_incomplete_transmission()
					if self.pkt_num == (self.total_pkts - 1):
						faking_frame_completion = False
						self.hand_shaking_count += 1	
						self.make_pkts(2)
						self.event_cleanup()
				#Packet Resend Event
				elif self.event == self.event_list[2]:
					#print "P : ", self.pkt_num
					if faking_frame_completion is False:
						self.rcvd_packet_resend()
					if self.pkt_num == (self.total_pkts - 1):
						faking_frame_completion = False
						self.hand_shaking_count += 1
						if self.frame_check():
							return True
				#Transmission Complete Event
				elif self.event == self.event_list[3]:
					if self.payload == self.event_list[3]:
						#print "C : ", self.payload
						self.write_log("C : " + self.payload)
						self.full_cleanup()
						return True
					elif self.payload == self.event_list[5]:
						#print "C : ", self.payload
						self.write_log("C : " + self.payload)
						self.full_cleanup()
						return 'ka'
					else:
						self.full_cleanup()
						return True
				#Error Event
				elif self.event == self.event_list[4]:
					self.full_cleanup()
					return 'Error'
				#Keep Alive Event
				elif self.event == self.event_list[5]:
					self.make_pkts(3, temp_data=self.event_list[5])
					self.event_cleanup()						
				#Unknown Event
				else:
					self.write_log('Unknown Event: ' + self.event)
					#print "Unknown Event: ", self.event
					self.event_cleanup()
			#Used to keep the total number of receives to a maximum
			if self.hand_shaking_count == self.hand_shaking_maximum:
				self.full_cleanup()
				self.write_log('Handshaking Maximum Reached')
				return 'Handshaking Maximum Reached'
			#Used to give control back to the outside controller
			if int(time.time() - time_0) >= self.frame_timeout:
				self.full_cleanup()
				self.write_log('Timeout')
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
			if len(self.payload) <= self.payload_length:
				self.new_transmission_data.append(self.payload)
			else:
				self.new_transmission_data.append('Failed')

	#Handler of individual packets tagged with Incomplete Transmission Event
	def rcvd_incomplete_transmission(self):
		if len(self.payload) <= self.payload_length:
			failed_pkts = list()
			failed_pkts = self.payload.split(':')
			for i in range(len(failed_pkts)):
				self.pkts_for_resend.append(failed_pkts.pop(-1))

	#Handler of individual packets tagged with Packet Resend Event
	def rcvd_packet_resend(self):
		self.payload = self.payload.split(':', 1)
		if len(self.payload[1]) <= self.payload_length:
			if self.new_transmission_data[int(self.payload[0])] == 'Failed':
				self.new_transmission_data[int(self.payload[0])] = self.payload[1]

	#Check the received frame to see if all packets are accounted for
	def frame_check(self):
		self.write_log("Number of Failed Packets: " + str(self.new_transmission_data.count('Failed')))
		if self.new_transmission_data.count('Failed') == 0:
			try:
				fo = open(self.working_directory + self.rx_filename, 'w')
				fo.write(''.join(self.new_transmission_data))
				fo.close()
			except:
				pass
			self.make_pkts(3)
			self.full_cleanup()		
			time.sleep(1.5)
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
		self.total_pkts = int(pkt[0])
		self.pkt_num = int(pkt[1])
		self.event = pkt[2]
		self.payload = pkt[3]

########################################################################################
#				COMMON TOOLS					       #
########################################################################################
	def write_log(self, data):
		if str(data) != '':
			fd = open(os.getcwd() + '/log.dat','a')
			fd.write(str(data) + '\n')
			fd.close()
		
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
				pkt = packetizer.make_packet(total_pkts, i, 
					self.event_list[event_index], payload, 
					scheme = self.scheme)
				self.transmit_pkts(pkt)
		#Transmitting Incomplete Transmission
		elif event_index == 1:
			bad_pkts = self.bad_pkt_indices()
			#This assumes pkt numbers in the 3 digit range to comply
			#with payload length of 128 bytes
			max_items_per_packet = 32
			total_pkts = len(bad_pkts)/max_items_per_packet + 1
			if len(bad_pkts)%(max_items_per_packet) == 0:
				total_pkts -= 1
			for i in range(total_pkts):
				payload = bad_pkts[:max_items_per_packet]
				bad_pkts = bad_pkts[max_items_per_packet:]
				pkt_payload = ':'.join(payload)
				pkt = packetizer.make_packet(total_pkts, i, 
					self.event_list[event_index], pkt_payload, 
					scheme = self.scheme)
				self.transmit_pkts(pkt)
		#Transmitting Packet Resend
		elif event_index == 2:
			counter = 0
			total_pkts = len(self.pkts_for_resend)
			for i in self.pkts_for_resend:
				try:
					payload = self.data_split_for_pkts[int(i)]
					pkt = packetizer.make_packet(total_pkts, counter, 
						self.event_list[event_index],  payload, 
						scheme = self.scheme, original_payload_count = i)
					self.transmit_pkts(pkt)
				except:
					print "Invalid Index at i = ", i
				counter += 1
			self.pkts_for_resend = list()
		#Transmitting: Transmission Complete, Error Event, Ready to Send, Clear to Send in order
		elif event_index == 3:
			if temp_data == '':
				pkt = packetizer.make_packet(1, 0, self.event_list[event_index], 
					self.event_list[event_index], scheme = self.scheme)
			else:
				pkt = packetizer.make_packet(1, 0, self.event_list[event_index], 
					temp_data, scheme = self.scheme)
			self.transmit_pkts(pkt)
		#Transmitting Error Event
		elif event_index == 4:
			pkt = packetizer.make_packet(1, 0, self.event_list[event_index], 
				self.event_list[event_index], scheme = self.scheme)
			self.transmit_pkts(pkt)
		#Tranmitting Keep Alive Event
		elif event_index == 5:
			pkt = packetizer.make_packet(1, 0, self.event_list[event_index],
				self.event_list[event_index], scheme = self.scheme)
			self.transmit_pkts(pkt)
		self.transmit_pkts(16*'\x55')		

	#Queue a packet in the transceiver flow graph
	def transmit_pkts(self, msg):
		self.txrx_path.msg_queue_in.insert_tail(gr.message_from_string(msg))

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
	def set_frame_time_out(self, new_timeout):
		self.frame_timeout = int(new_timeout)

	def set_frequency(self, fc, offset=''):
		fc = int(fc)
		if (fc >= 420025000) and (fc <= 449975000):
			self.fc = fc
			if offset != '':
				self.carrier_offset = offset
			rx_freq = self.fc + self.carrier_offset + self.rx_f_offset
			tx_freq = self.fc + self.carrier_offset + self.tx_f_offset
			try:
				self.txrx_path.usrp_simple_source_x_0.set_frequency(
					rx_freq, verbose=False)
			except:
				pass
				#self.write_log('Unable to change TX frequency')
				#print "Unable to change receive frequency. txrx_controller line 328"
			try:
				self.txrx_path.usrp_simple_sink_x_0.set_frequency(
					tx_freq, verbose=False)
			except:
				pass
				#self.write_log('Unable to change RX frequency')
				#print "Unable to change transmit frequency. txrx_controller line 333"
		else:
			#self.write_log('Frequency not within FCC regs.')
			print "Invalid Fc (Not within bounds: Fc >= 420025000 and Fc <= 449975000). txrx_controller line 335"

	def set_rx_path(self, new_path):
		self.working_directory = new_path
		self.write_log(self.working_directory)

	def set_rx_filename(self, new_name):
		self.rx_filename = new_name
		#self.write_log(self.rx_filename)

	def close_queues(self):
		self.txrx_path.msg_queue_in.insert_tail(gr.message(1))
		self.txrx_path.msg_queue_out.insert_tail(gr.message(1))
