#!/usr/bin/env python

import tx_rx_path
import packetizer
from gnuradio import gr

class txrx_controller():

	def __init__(self):
		self.event = ''
		#Event List:
		#EW - New Transmission: when data is dropped into this controller.
		#IN - Incomlete Transmission: when data is lost in the last tx.
		#PR - Packet Resend: Sending the packets that were dropped in last tx.
		#TC - Transmission Complete: Original receive side has all data.
		#UV - Unknown Event: If first packet is dropped, frame pkt is lost.
		self.event_list = ['EW', 'IN', 'PR', 'TC', 'UV']
		self.tx = True
		self.bad_pkt_indexes = list()
		self.data = ''
		self.data_temp = list()
		self.pkts = list()
		self.pkts_copy = list()
		self.payload_length = 1024
		self.pkt_count = None
		self.total_pkts = None
		self.payload = ''
		#Call and start the USRP transmit path
		tb = tx_rx_path.tx_rx_path()
		tb.Start()
			

########################################################################################
#					RECEIVER
########################################################################################
	def receive(self):
		#Block transmit from outside while receiving/handshaking.
		self.tx = False
		#Ensure self.data is an empty list.
		self.data = list()
		#Ensure temp is empty before use.
		temp = ''
		#Ensure self.data_temp is an empty list.
		self.data_temp = list()
		while self.tx is False:
			#Looking for items in the queue while receiving
			if tb.msg_queue_out.empty_p() is False:
				#Queue no longer empty, get first item in the queue
				temp = tb.msg_queue_out.delete_head_nowait().to_string()
				#Strip Total packet count, individual packet count, payload
				strip_totalcount__pktcount_payload(temp)
				#To account for lost packets/denied packets
				#Append empty strings in place of packets that are found to
				#to be lost. The logic is, if the individual packet count is
				#greater than the length of self.data, then there was a lost
				#packet or packet denied by the crc checking. Append empty
				#strings so that those can be checked and indexed later for
				#bad packet indexes to be retreived.
				while len(self.data) < self.pkt_count:
					self.data.append('')
				#Once self.data is the correct length, add the current payload
				#onto the list.
				self.data.append(self.payload)
			#If this statement is true, we received at least one packet, and
			#the last packet which caused the append operation to bring the length
			#of self.data to the length of the total number of packets in the frame.
			elif len(self.data) == self.total_pkts:
				#This is to save the data that was received. Since we may need
				#make multiple send and receives, and update a list to complete
				#the frame, self.data is the instance storage location and 
				#self.data_temp is the actual location for all data to be stored
				#to be sent to Mike's controller. This happens only the first time
				#meaning we are receiving a confirmation or a new transmission and
				#need to keep the initial reception safe.
				if len(self.data_temp) == 0:	
					#Move over the entire length of the received data and
					#save it into self.data_temp.
					for i in range(self.data):
						self.data_temp.append(self.data[i])
				#The first packet was lost somehow and the frame event isn't known.
				if self.data[0] == '':
					#Don't know what the event is
				else:
					#Know Event, respond to event
					if self.data[0] == event_list[0]: #New Transmission
					if self.data[0] == event_list[1]: #Incomplete
					if self.data[0] == event_list[2]: #Packet Resend
					if self.data[0] == event_list[3]: #Transmission Complete
					if self.data[0] == event_list[5]: #Unknown Event
		cleanup()
	
	def handshaking_transmit(self, event_index):
		#Need to fix
		handshaking_make_pkts(event_index)
		transmit_pkts()

	def handshaking_make_pkts(event_index):
		#This is only for the receive path during handshaking and should not be called
		#by an outside source. Make the frame packet for this event.
		self.pckts_copy.append(packetizer.make_packet(self.event_list[event_index], 0))
		#Loop over the pkts which still holds the original frame. Use the indexes from
		#the bad_pkt_indexes method to copy these packets again into self.pkts_copy to
		#be sent again.
		for i in self.bad_packet_indexes:
			self.pkts_copy.append(self.pkts[int(i)])

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
		#Tested
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
#					TRANSMITTER
########################################################################################
	def transmit(self, data):
		#if statment used to block transmitting while handshaking/receiving is 
		#occuring. Don't want to transmit while in receive mode unless expressly
		#for the handshaking process.
		if self.tx is True:
			#Clear the variables in the init method that are commonly used.
			cleanup()
			#Block self.data from the outside
			self.data = data
			#Make the frame packet, and packets of the data. 
			make_pkts()
			#Transmit the frame through the transmit path and the USRP.
			transmit_pkts()
			#Return True to signify transmit occured and is complete.
			return True
		#Not supposed to be transmitting will drop the request to transmit down 
		#to this else statement.
		else:
			#Return False is the outside tries to transmit while in receive
			#mode. This signifies that there is currently a handshaking 
			#process going on.
			return False

	def make_pkts(self):
		#Needs Test to make sure the data_pkts is long enough,loop is correct.
		#Determine total number of payloads for this frame. The total
		#number is derived by taking the length of the data given by the
		#outside and dividing it by the payload length, this will round
		#down as it is integer division. Adding 2 at the end is for the
		#round down operation and also the framer packet which is not
		#initially contained in the data given by the outside.
		self.total_pkts = len(self.data)/self.payload_length + 2
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
			self.pkts_copy.append(self.pkts[i])

########################################################################################
#				MISCELLANEOUS OPERATIONS
########################################################################################
	def transmit_pkts(self):
		#Actually sends self.pkts_copy starting with the head down the transmit
		#path to the USRP. It always move along the entire length of pkts_copy.
		while len(self.pkts_copy) != 0:
			tb.msg_queue_in.insert_tail(gr.message_from_string(self.pkts_copy.pop(0)))

	def cleanup(self):
		#This is to cleanup between new transmissions and handshaking processes.
		#Don't want residules to be haging around inside variables.
		self.event = ''
		self.tx = True
		self.bad_pkt_indexes = list()
		self.data = ''
		self.data_temp = list()
		self.pkts = list()
		self.pkts_copy = list()
		self.payload_length = 1024
		self.pkt_count = None
		self.total_pkts = None
		self.payload = ''
