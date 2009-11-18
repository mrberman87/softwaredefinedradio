########################################################################################
# Comment only version of txrx_controller.py. Do not run this file.		       #
########################################################################################
#!/usr/bin/env python

#Version 2.02

import tx_rx_path, packetizer
import time, os
from gnuradio import gr

class txrx_controller():

	def __init__(self, hand_shaking_max=5, frame_time_out=45, pay_load_length=128, \
			work_directory = os.path.expanduser('~') + '/Desktop'):
		#Events:
		# 1. N - New Transmission
		# 2. I - Incomplete Transmission
		# 3. P - Packet Resend
		# 4. C - Transmission Complete
		# 5. E - Error
		# 6. RTS - Ready To Send
		# 7. CTS - Clear To Send
		self.event_list = ['N', 'I', 'P', 'C', 'E', 'RTS', 'CTS']
		self.hand_shaking_maximum = hand_shaking_max
		self.working_directory = work_directory
		self.payload_length = pay_load_length
		self.frame_timeout = frame_time_out
		self.new_transmission_data = list()
		self.data_split_for_pkts = list()
		self.pkts_for_resend = list()
		self.hand_shaking_count = 0
		self.total_pkts = None
		self.pkt_num = None
		self.payload = ''
		self.event = ''
		self.txrx_path = tx_rx_path.tx_rx_path()
		self.txrx_path.start()

########################################################################################
#					TRANSMITTER				       #
########################################################################################
	def transmit(self, data_source):
		#Cleanup all variables prior to sending new transmission
		self.full_cleanup()
		#Transmit RTS to initialize link
		self.make_pkts(5)
		#If received CTS then link is initialized and continue with transmit
		if self.receive() == True:
			#Error and transmitting to other side
			if data_source == 'Error':
				self.make_pkts(4)
				return True
			#Using File input from default directory
			elif data_source.count('/') > 0:
				#Attempt to open file and handle any errors
				try:
					fo = file(self.working_directory + data_source, 'r')
					temp_data = fo.read()
					fo.close()
				#File failed to open, return false
				except:
					return False
			#Variable passed in is data itself
			else:
				temp_data = data_source
			#Transmit New Transmission with the data from file or passed
			#in directly
			self.make_pkts(0, temp_data)
			#Go into receive mode to complete any handshaking required
			temp = self.receive()
			#Return result of receive
			return temp
		#Did not receive CTS from other transmitter, link not established
		else:
			return False

########################################################################################
#					RECEIVER				       #
########################################################################################
	def receive(self):
		#Set an initial time for the frame timeout
		time_0 = time.time()
		#Clear the New Transmission data for reception of new frame
		self.new_transmission_data = list()
		#Ensure the number of handshakes is zero for correct counting
		self.hand_shaking_count = 0
		#Initialize the faking frame completion in the event of a frame lost
		faking_frame_completion = False
		#Repeat until a return statement is called
		while True:
			#If the queue is not empty, or faking the frame continue
			if (self.txrx_path.msg_queue_out.empty_p() is False) or faking_frame_completion:
				#Not faking the frame
				if faking_frame_completion is False:
					#Real item in queue, update the time
					time_0 = time.time()
					#Retrieve item from queue
					queue_item = self.msgq_in()
					#Separate all pieces needed for event handling
					self.slice_packet(queue_item)
				#New Transmission Event Received
				if self.event == self.event_list[0]:
					#If faking the frame, pass True to ensure only certain
					#events happen to avoid errors
					if faking_frame_completion:
						self.rcvd_new_transmission(True)
					#Not faking frame, real new transmission packet
					else:
						#Handle new transmission packet
						self.rcvd_new_transmission()
					#Check to see if the current packet is the last
					#packet in the frame
					if self.pkt_num == (self.total_pkts - 1):
						#Last packet found, reset faking frame
						faking_frame_completion = False
						#Incriment Handshaking count
						self.hand_shaking_count += 1
						#Check frame for completeness
						if self.frame_check():
							#Frame complete, return True
							return True
				#Incomplete Transmission Event Received (list of missing packets)
				elif self.event == self.event_list[1]:
					#Not faking frame completion
					if faking_frame_completion is False:
						#Handle incomplete transmission packet
						self.rcvd_incomplete_transmission()
					#Check to see if the current packet is the last
					#packet in the frame
					if self.pkt_num == (self.total_pkts - 1):
						#Last packet found, reset faking frame
						faking_frame_completion = False
						#Incriment Handshaking count
						self.hand_shaking_count += 1
						#Transmit Packet Resend from the list
						#received in the current frame	
						self.make_pkts(2)
						#Cleanup the event information
						self.event_cleanup()
						#Clear the packets that were resent
						self.pkts_for_resend = list()
				#Packet Resend Event Received
				elif self.event == self.event_list[2]:
					#Not faking frame completion
					if faking_frame_completion is False:
						#Handle Packet Resend Packet
						self.rcvd_packet_resend()
					#Check to see if the current packet is the last
					#packet in the frame
					if self.pkt_num == (self.total_pkts - 1):
						#Last packet found, reset faking frame
						faking_frame_completion = False
						#Incriment Handshaking count
						self.hand_shaking_count += 1
						#Check frame for completeness
						if self.frame_check():
							#Frame complete, return True
							return True
				#Transmission Complete Received
				elif self.event == self.event_list[3]:
					#Cleanup all variables
					self.full_cleanup()
					#Return True
					return True
				#Error Event Received
				elif self.event == self.event_list[4]:
					#At some point, the other transmitter suffered
					#an error, clear this transmission's variables
					self.full_cleanup()
					#Return Error to overall controller
					return 'Error'
				#Ready To Send Event Received
				elif self.event == self.event_list[5]:
					#Transmit CTS to initialize link
					self.make_pkts(6)
					#Cleanup event variables for new frame
					self.event_cleanup()
				#Clear to Send Event Received
				elif self.event == self.event_list[6]:
					#Return True to signify link initialized
					return True
				#Unknown Event
				else:
					#Received a packet with an unknown event,
					#clear event variables and continue
					self.event_cleanup()
			#Used to keep the total number of receives to a maximum
			if self.hand_shaking_count == self.hand_shaking_maximum:
				#Reached maximum number of handshakes, clear all
				#variables and return Handshaking Max Reached
				self.full_cleanup()
				return 'Handshaking Maximum Reached'
			#Used to give control back to the outside controller
			if int(time.time() - time_0) >= self.frame_timeout:
				#Frame timeout reached, clear all variables
				#and give control back to overall controller
				self.full_cleanup()
				return 'Timeout'
			#Used to fake a frame completion for handshaking
			if (self.event in self.event_list) and (int(time.time() - time_0) >= 10):
				#Know event from a packet received in this frame, 
				#fame the frame completion and work with what is known.
				faking_frame_completion = True
				self.pkt_num = self.total_pkts - 1

########################################################################################
#				RECEIVER TOOLS					       #
########################################################################################
	#Handler of individual packets tagged with New Transmission Event
	def rcvd_new_transmission(self, faking_frame_completion=False):
		#If the current packet number is not the next one after the
		#current position in the index, pad for the lost packets
		while len(self.new_transmission_data) < self.pkt_num:
			self.new_transmission_data.append('Failed')
		#Faking frame completion, no payload data known
		if faking_frame_completion:
			self.new_transmission_data.append('Failed')
		#Not faking frame completion, know payload data
		else:
			#Ensure the error of concatinating two payloads at the
			#receive queue does not affect the end file. 
			if len(self.payload) <= self.payload_length:
				self.new_transmission_data.append(self.payload)
			#Packet received failed to be the correct maximum length
			else:
				self.new_transmission_data.append('Failed')

	#Handler of individual packets tagged with Incomplete Transmission Event
	def rcvd_incomplete_transmission(self):
		#Check to see if payload meets length requirements
		if len(self.payload) <= self.payload_length:
			#Payload is corrent length, split the packet numbers
			failed_pkts = self.payload.split(':')
			#Determine the total number of failed packets in this packet
			num_failed_pkts = len(failed_pkts)
		#Failed length test
		else:
			#Split the first correct number of packet numbers to 
			#reduce the number of resends. 4 represents 999: the
			#max number of packets this system will see with a 
			#colon delimiting the different packet numbers
			max_splits = self.payload_length/4
			#Split the payload apart to obtain the packet numbers
			failed_pkts = self.payload.split(':', max_splits)
			#If the length of the last item in failed_pkts is
			#greater than the largest length of the 3 digit
			#packet number, then delete it from the list.
			if len(failed_pkts[-1]) > 3:
				failed_pkts.pop(-1)
			#Determine the total number of packets from the length
			num_failed_pkts = len(failed_pkts)
		#Add the packet numbers to pkts for resend
		for i in range(num_failed_pkts):
			self.pkts_for_resend.append(failed_pkts.pop(0))


	#Handler of individual packets tagged with Packet Resend Event
	def rcvd_packet_resend(self):
		#Split the payload
		self.payload = self.payload.split(':', 1)
		#Get the original packet number of the current payload
		original_pkt_number = int(self.payload.pop(0))
		#Get the temporary payload
		temp_payload = self.payload.pop(0)
		#If the temporary payload meets the length requirements and is actually missing
		if (len(temp_payload) <= self.payload_length) and (self.new_transmission_data[original_pkt_number] == 'Failed'):
			#Remove the 'Failed' Tag from the list
			self.new_transmission_data.pop(original_pkt_number)
			#Insert the missing payload
			self.new_transmission_data.insert(original_pkt_number, temp_payload)

	#Check the received frame to see if all packets are accounted for
	def frame_check(self):
		#Count the number of 'Failed' tags, if zero then no missing packets
		if self.new_transmission_data.count('Failed') == 0:
			#Attempt to open the file for writing handling any exceptions
			try:
				fo = open(self.working_directory + '/rx_data', 'w')
				fo.write(''.join(self.new_transmission_data))
				fo.close()
			#Exception occured, do not write to file
			except:
				pass
			#Transmit Transmission Complete
			self.make_pkts(3)
			#Cleanup all variables
			self.full_cleanup()
			#Return True
			return True
		#Frame not complete
		else:
			#Transmit Transmission Incomplete
			self.make_pkts(1)
			#Cleanup event variables
			self.event_cleanup()
			#Return False
			return False

	#Return the first item in the flow graph's Receive Queue
	def msgq_in(self):
		return self.txrx_path.msg_queue_out.delete_head_nowait().to_string()

	#Determine the missing packet indices in New Transmission Data
	def missing_pkt_numbers(self):
		#Holds the current index value where the item was found
		index = 0
		#Holds the next index value after the current item
		n_index = 0
		#Initialize the missing pkts for this run
		missing_pkts = list()
		#Run until the number of missing packets is equal to the number of
		#missing packets in new transmission data
		while len(missing_pkts) < self.new_transmission_data.count('Failed'):
			#Find the first index containing 'Failed' af and after n_index
			index = self.new_transmission_data.index('Failed', n_index)
			#append the index value in missing packets as a string
			missing_pkts.append(str(index))
			#Incriment n_index so it is always one step after the current
			#index value to continue searching
			n_index = index + 1
		#Return the list of missing packets
		return missing_pkts

	#Remove, Total Number of Packets in the Frame, Packet Number, Event, and Payload
	def slice_packet(self, pkt):
		# [Total Number of Packets]:[Packet Number in this Frame]:[Event]:[Payload]
		#Split pkt into the 3 pieces being popped after
		pkt = pkt.split(':', 3)
		#First is total number of packets in this frame
		self.total_pkts = int(pkt.pop(0))
		#Second is the packet number corresponding to the number in the current frame
		self.pkt_num = int(pkt.pop(0))
		#Event of this specific packet
		self.event = pkt.pop(0)
		#Payload
		self.payload = pkt.pop(0)

########################################################################################
#				COMMON TOOLS					       #
########################################################################################
	def make_pkts(self, event_index, temp_data=''):
		#Transmitting New Transmission
		if event_index == 0:
			#Determine total number of packets needed
			total_pkts = len(temp_data)/self.payload_length + 1
			#If the length of the data to be sent is a multiple of the
			#current payload length, then there was no round down and 
			#the +1 is extra and needs to be removed
			if len(temp_data)%self.payload_length == 0:
				total_pkts -= 1
			#Starts at 0 and goes to total_pkts - 1
			for i in range(total_pkts):
				#Slice off the payload without changing the data
				payload = temp_data[:self.payload_length]
				#Save the payload for a packet resend event
				self.data_split_for_pkts.append(payload)
				#Remove this payloads data from the original data
				temp_data = temp_data[self.payload_length:]
				#Make the packet and transmit it
				self.transmit_pkts(packetizer.make_packet( \
					total_pkts, i, self.event_list[0], payload))
		#Transmitting Incomplete Transmission
		elif event_index == 1:
			#Determine the missing packets
			missing_pkts = self.missing_pkt_numbers()
			#For each packet to be standalone and to conform to a max
			#payload size, there can only be so many packet numbers
			#transmitted per packet
			max_items_per_packet = self.payload_length/4
			#Determine total number of packets, adding 1 for round down
			#if not multiple
			total_pkts = len(missing_pkts)/max_items_per_packet + 1
			#If the number of missing packets is a mutliple of the 
			#max items per packet then remove the round down adjustment
			if len(missing_pkts)%(max_items_per_packet) == 0:
				total_pkts -= 1
			#Start at 0 and goes to total_pkts - 1
			for i in range(total_pkts):
				#Slice the payload from missing packets w/out changing the data
				payload = missing_pkts[:max_items_per_packet]
				#Edit the data to remove the current payload
				missing_pkts = missing_pkts[max_items_per_packet:]
				#Create the string to be placed into the packet as the payload
				pkt_payload = ':'.join(payload)
				#Create the packet
				pkt = packetizer.make_packet( \
					total_pkts, i, self.event_list[event_index], pkt_payload)
				#Transmit the packet
				self.transmit_pkts(pkt)
		#Transmitting Packet Resend
		elif event_index == 2:
			#Used to incriment the packet number of this frame
			counter = 0
			#Total packets for this event is the total number of packets that
			#need to be resent
			total_pkts = len(self.pkts_for_resend)
			#i takes on the values contained in pkts_for_resend
			for i in self.pkts_for_resend:
				#Payload is the original payload from the initial send
				payload = self.data_split_for_pkts[int(i)]
				#Make the packet including the original payload count
				pkt = packetizer.make_packet( \
					total_pkts, counter, self.event_list[event_index],  
					payload, original_payload_count = i)
				#Transmit the packet
				self.transmit_pkts(pkt)
				#Incriment this transmissions packet number counter
				counter += 1
		#Transmitting: Transmission Complete, Error Event, Ready to Send, Clear to Send in order
		elif event_index == 3 or event_index == 4 or event_index == 5 or event_index == 6:
			#Make the only packet required for any of the above events
			#Each of these events are single packet responses where only the event is
			#of importance but the payload contains the event as well just to ensure 
			#proper packet make-up.
			pkt = packetizer.make_packet( \
				1, 0, self.event_list[event_index], 
				self.event_list[event_index])
			#Transmit the packet
			self.transmit_pkts(pkt)

	#Queue a packet in the transceiver flow graph
	def transmit_pkts(self, msg):
		#Create a message from a string
		msg_0 = gr.message_from_string(msg)
		#Queue the item in the flow graph
		self.txrx_path.msg_queue_in.insert_tail(msg_0)

	#Used to cleanup while still handshaking
	def event_cleanup(self):
		self.event = ''
		self.payload = ''
		self.pkt_num = None
		self.total_pkts = None

	#Used to cleanup for new transmission and finished receiving
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

	def set_rx_path(self, new_path):
		if os.path.exists(new_path):
			self.work_directory = new_path
			return True
		return False

