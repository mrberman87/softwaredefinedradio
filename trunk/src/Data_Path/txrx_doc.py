#!/usr/bin/env python
########################################################################################
#		Have to finish comments and updating Documentation
########################################################################################




import tx_rx_path
import packetizer
from gnuradio import gr

class txrx_controller():

	def __init__(self):
		#Event List:
		#EW - New Transmission: when data is dropped into this controller.
		#IN - Incomlete Transmission: when data is lost in the last tx.
		#PR - Packet Resend: Sending the packets that were dropped in last tx.
		#TC - Transmission Complete: Original receive side has all data.
		self.event_list = ['EW', 'IN', 'PR', 'TC']
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
#					TRANSMITTER
########################################################################################
	def transmit(self, data):
		#to set the home directory for file input, need to edit for other login/UAV
		home_path = '/home/charles/softwaredefinedradio/src/'
		#Ensure self.data is empty, in case multiple user transmits are called
		self.data = ''
		#This is for accepting files as well as direct data via function call
		if data_source.count('/') > 0:
			fo = file(home_path + data_source, 'r')
			data = fo.read()
			fo.close()
			self.data = data
		else:
			self.data = data_source
		#Packetize all data for transmission
		make_pkts(self)
		#Transmit the packets through the USRP
		transmit_pkts(self)
		#Return true to signify operation of packetization and queueing is complete
		return True

########################################################################################
#					RECEIVER
########################################################################################
	def receive(self):
		#Ensure self.data is an empty list.
		self.data = list()
		#Ensure self.data_temp is an empty list.
		self.data_temp = list()
		#Ensure temp is empty before use.
		temp_event = ''
		while True:
			#Looking for items in the queue while receiving
			if tb.msg_queue_out.empty_p() is False:
				msgq_in()
				#To account for lost packets/denied packets
				#Append empty strings in place of packets that are found to
				#to be lost. The logic is, if the individual packet count is
				#greater than the length of self.data, then there was a lost
				#packet or packet denied by the crc checking. Append empty
				#strings so that those can be checked and indexed later for
				#bad packet indexes to be retreived.
				while len(self.data_temp) < self.pkt_count:
					self.data_temp.append('')
				#Once self.data is the correct length, add the current payload
				#onto the list.
				self.data_temp.append(self.payload)
			#If this statement is true, we received at least one packet, and
			#the last packet which caused the append operation to bring the length
			#of self.data_temp to the length of the total number of packets in the frame.
			elif len(self.data_temp) == self.total_pkts:
				#This is to save the data that was received. Since we may need
				#make multiple send and receives, and update a list to complete
				#the frame, self.data is the instance storage location and 
				#self.data_temp is the actual location for all data to be stored
				#to be sent to Mike's controller. This happens only the first time
				#meaning we are receiving a confirmation or a new transmission and
				#need to keep the initial reception safe.
				if len(self.data) == 0:	
					#Move over the entire length of the received data and
					#save it into self.data_temp.
					for i in range(self.data_temp):
						self.data.append(self.data_temp.pop(0))
				#2nd time receiving and need to know event for how to handle
				#the information that is coming in.
				else:
					temp_event = self.data_temp[0] #To ensure the back and forth happens more than once
				#Unknown event: clear temporary rcvd data. This is to ensure that if we don't know
				#what the data is, we don't do anything.
				if temp_event == '': 
					self.data_temp = list()
					break
				#Received Packet Resend as 2nd received frame. Have to insert packets into the original frame.
				if temp_event == event_list[2]:
					insert_missing_pkts(self)
					#Check to see if the original frame is complete
					if frame_check(self) is True:
						#If the frame has all packets delete the event identifier in self.data and 
						#return the payloads that contain the original data to be sent.
						self.data.pop(0)
						return ''.join(self.data)
				#Received Incomplete Transmission as 2nd received frame or later. 2nd packet will always contain
				#a list of indices of the missing packets. Split them between colons and put them into the list.
				#Transmit the missing packets along with a frame packet. Clear self.data_temp for next rcv
				elif temp_event == event_list[1]:
					self.bad_pkt_indices = self.data_temp[1].split(':')
					handshaking_transmit(2)
					self.data_temp = list()
				#Newest event is Transmission Complete, cleanup variables and return True to the overall controller
				elif temp_event == event_list[3]:
					cleanup(self)
					return True
				#If newest frame event unknown, default to original self.data issue	
				#Check to see if rcvd Transmission Complete
				elif (self.data[0] == event_list[3] and temp_event == '') or temp_event == event_list[3]:
					cleanup(self)
					return True
				#Initially rcvd Incomplete Transmission. Split the missing packet indices and re-transmit them.
				elif self.data[0] == event_list[1]:
					self.bad_pkt_indices = self.data[1].split(':')
					handshaking_transmit(2)
					self.data_temp = list()
				#Initially rcvd New Transmission or the Frame packet was lost. Check the frame and proceed
				#with frame check logic. If frame check returns true, then return the new frame minus the event.
				elif self.data[0] == event_list[0] or self.data[0] == '':
					if frame_check(self) is True:
						self.data.pop(0)
						return ''.join(self.data)

########################################################################################
#				RECEIVER TOOLS					       #
########################################################################################

def frame_check(self):
	#Count the number of missing packets, if zero then respond with Transmission Complete and clean up. Also, return true
	if self.data.count('') == 0:
		handshaking_transmit(3)
		cleanup(self)
		return True
	#Frame has missing packets, determine those indices that refer to the missing packets and make a payload out of them.
	#Transmit the frame event Incomplete Transmission and a single packet with the indices of missing packets. Return
	#false to show all of the data is unnacounted for.
	else:
		bad_pkt_indexes(self)
		handshaking_transmit(1)
		self.data_temp = list()
		return False

def insert_missing_pkts(self):
	#Takes a rcvd frame of re-transmitted packets and inserts them into the original data rcvd variable at the locations
	#determined by each packet's packet number. 
	for i in range(1, len(self.data_temp)):
		slice_total_count_pkt_count_payload(self.data_temp.pop(1))
		self.data.pop(self.pkt_count)
		self.data.insert(self.pkt_count, self.payload)			

def msgq_in(self):
	#Untested: msgq retrieval
	#Queue no longer empty, get first item in the queue
	#Slice Total packet count, individual packet count, payload
	temp = ''
	temp = self.txrx_path.msg_queue_out.delete_head_nowait().to_string()
	slice_total_count_pkt_count_payload(temp)	

def handshaking_transmit(self, event_index):
	#Need to fix
	handshaking_make_pkts(event_index)
	transmit_pkts()

def handshaking_make_pkts(event_index):
	#This is only for the receive path during handshaking and should not be called
	#by an outside source.
	#Transmitting Incomplete Transmission event w/ 2nd packet having missing pkt numbers from self.data
	if event_index == 1:
		self.pkts_temp.append(packetizer.make_packet(self.event_list[event_index], 0, 2))
		self.pkts_temp.append(packetizer.make_packet(':'.join(self.bad_pkt_indices), 1, 2))
	#Transmitting Packet Resend event, w/ missing pkts from rcvd incoming transmission pkt list
	elif event_index == 2:
		#Total pkts in response is the number of missing packets plus the frame pckt
		total_pkts = len(self.bad_pkt_indices) + 1
		self.pkts_temp.append(packetizer.make_packet(self.event_list[event_index], 0, total_pkts))
		for i in range(len(self.bad_pkt_indices)):
			self.pkts_temp.append(self.pkts[int(self.bad_pkt_indices[i])])
	#Transmitting Transmission Complete
	elif event_index == 3:
		self.pkts_temp.append(packetizer.make_packet(self.event_list[event_index], 0, 1))

def bad_pkt_indexes(self):
	#Tested
	#Index refers to the point in the list where the empty string is found
	#denoting a missed packet. n_index is used to ensure that all index 
	#values are searched over. The slicing works at the positional index
	#in n_index and thats why I used the last index location of the empty
	#string and added one, to start looking at the next index location.
	index = 0
	n_index = 0
	#Look only so long as the number of bad packet indexes is less than
	#the total number of missed packets
	while len(self.bad_pkt_indexes) < self.data.count(''):
		#Search through self.data for the empty strings denoting missed
		#packets. n_index as described above.
		index = self.data.index('', n_index)
		#Save the index locations as a string for easy concatination.
		self.bad_pkt_indexes.append(str(index))
		#Incriment n_index so the search will move past the last index
		#value found.
		n_index = index + 1

def strip_totalcount_pktcount_payload(self, temp):
	#This strips out the total packet count, individual payload count,
	#and the payload for this packet from the message sink queue.
	#The total packet count is always first and is delimited with a colon.
	self.total_pkts = int(temp[:temp.index(":")])
	#Update temp to be able to use the index finding function.
	temp = temp[temp.index(":") + 1:]
	#After the total number of packets, the individual payload count is
	#delimited with a colon. Slice this out.
	self.pkt_count = int(temp[:temp.index(":")])
	#Don't need to update temp, only 1 colon left that is important to the
	#packet process. Save the payload which is after the second colon always.
	self.payload = temp[temp.index(":") + 1:]

########################################################################################
#				TRANSMITTER TOOLS				       #
########################################################################################

def make_pkts(self):
	#Needs Test to make sure the data_pkts is long enough,loop is correct.
	#Determine total number of payloads for this frame. The total
	#number is derived by taking the length of the data given by the
	#outside and dividing it by the payload length, this will round
	#down as it is integer division. Adding 2 at the end is for the
	#round down operation and also the framer packet which is not
	#initially contained in the data given by the outside.
	self.total_pkts = len(self.data)/self.payload_length + 2
	#This if statement is to protect against extra packets when the integer division
	#is a whole number.
	if len(self.data)%2 == 0:
		total_pkts -= 1
	#Create the first packet which will contain the framer information.
	#This will contain the total number of packets, the packet number,
	#and the payload with the event information. 
	#Example: "123:0:Event ID" The event ID will always be 2 characters
	#long. The framer packet and all other packets will be delimited with
	#colons.
	self.pkts.append(packetizer.make_packet(self.event_list[0], 0))
	#Need to verify the range to be correct. Create the rest of the packets
	#from the data from outside. This consumes everything in self.data. 
	for i in range(1, self.total_pkts):
		#The current payload is everything from index zero to the
		#payload length.
		payload = self.data[:self.payload_length]
		#Reset the outside data to reflect that this data was consumed 
		#by payload.
		self.data = self.data[self.payload_length:]
		#Add the latest packet to the pkts list. All packets will contain
		#the total frame packet count, the individual packet number, and
		#the payload.
		self.pkts.append(packetizer.make_packet(payload, i. self.total_pkts))
	#Create a copy of the pkts that will be consumed in the transmit process.
	#This is for retention of fully made packets that may need to be sent
	#back to the other device in the event of lost packets.
	for i in range(len(self.pkts))
		self.pkts_temp.append(self.pkts[i])

########################################################################################
#					COMMON OPERATIONS
########################################################################################
def transmit_pkts(self):
	#Actually sends self.pkts_temp starting with the head down the transmit
	#path to the USRP. It always move along the entire length of pkts_copy.
	for i in range(len(self.pkts_temp)):
		msg = gr.message_from_string(self.pkts_temp.pop(0))
		self.txrx_path.msg_queue_in.insert_tail(msg)

def cleanup(self):
	#This is to cleanup between new transmissions and handshaking processes.
	#Don't want residules to be haging around inside variables.
	self.bad_pkt_indices = list()
	self.pkts = list()
	self.pkts_temp = list()
	self.pkt_count = None
	self.total_pkts = None
	self.payload = ''
