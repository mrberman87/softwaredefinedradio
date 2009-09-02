########################################################################################
# Comment only version of txrx_controller.py. Do not run this file.		       #
########################################################################################

#Version 1.05

import tx_rx_path
import packetizer
from gnuradio import gr
import time

class txrx_controller():

	def __init__(self):
		#Events:
			# 1. 'NT' - New Transmission
			# 2. 'IN' - Incomplete Transmission
			# 3. 'PR' - Packet Resend
			# 4. 'TC' - Transmission Complete
			# 5. 'ER' - Error
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
		#Every time someone transmits something, all variables are reset to
		#initialized state.
		self.cleanup()
		#This is to transmit an error event in the case of the process failing.
		if data_source == 'Error':
			self.make_pkts(error_event=True)
			return True
		#This gives the outside the ability to give a complete file path and
		#have this script open the file and transmit it.
		elif data_source.count('/') > 0:
			fo = file(data_source, 'r')
			self.data = fo.read()
			fo.close()
		#If the outside just gives a string or input, it gets transmitted here.
		else:
			self.data = data_source
		#Make packets for a transmit call only.
		self.make_pkts()
		#Go into receive mode to complete handshaking.
		temp = self.receive()
		#Return the outcome of the handshaking.
		return temp

########################################################################################
#					RECEIVER				       #
########################################################################################
	def receive(self):
		#Initial time of calling receive for timeout.
		time_0 = time.time()
		#Clear some environment variables so there is no residual data.
		self.data = list()
		self.data_temp = list()
		#Initialize the handshaking count for this receive session.
		self.hand_shaking_count = 0
		#temp_event holds each event after the first frame reception.
		temp_event = ''
		while True:
			#Check to see if there is any payloads in the receive queue.
			if self.txrx_path.msg_queue_out.empty_p() is False:
				#Payload in the receive queue, update the timeout time.
				time_0 = time.time()
				#Get the message and slice it.
				self.msgq_in()
				#If this is the first receive, append to the temp variable
				#for purposes of determing lost packets.
				if self.initial_rcv:
					while len(self.data_temp) < self.pkt_count:
						self.data_temp.append('')
				#Any reception after the initial frame
				else:
					#Save a version of each packet with the individual counts
					#and payloads for insertion.
					self.pkt_num.append(str(self.pkt_count) + ':' + self.payload)
				#Add payload to temp location.
				self.data_temp.append(self.payload)
				#Clear some environment variables to ensure proper data
				#manipulation.
				self.pkt_count = None
				self.payload = ''
			#Last packet of initial frame found, All packets in any other receive found.
			elif len(self.data_temp) == self.total_pkts:
				#Incriment the handshaking count
				self.hand_shaking_count += 1
				#Ensure that the controller does not enter this loop again until
				#the next frame comes and makes this statement true.
				self.total_pkts = None
				#First reception, move all temp data to self.data to be analyzed.
				if self.initial_rcv:
					for i in range(len(self.data_temp)):
						self.data.append(self.data_temp.pop(0))
					self.initial_rcv = False
				#Any reception after first
				else:
					#Remove frame packet from pkt_num for insertion reasons
					self.pkt_num.pop(0)
					#Check to make sure the event in the temp data is a
					#known event.
					if self.data_temp[0] in self.event_list:
						temp_event = self.data_temp.pop(0)
					#If not a known event, reset these variables. The controller
					#will then default to the original problem in self.data
					else:
						temp_event = ''
						self.data_temp = list()
						self.pkt_num = list()
				#Received a Packet Resend on or after second receive.
				if temp_event == self.event_list[2]:
					#Clear temp_event for continuity reasons.
					temp_event = ''
					#Insert missing packets into the original reception variable
					self.insert_missing_pkts()
					#Check to see if the initial frame is complete
					if self.frame_check():
						return "Handshaking Complete."
				#Received an Incomplete Transmission on or after second receive.
				elif temp_event == self.event_list[1]:
					#Clear certain variables that have no bearing on this reception.
					temp_event = ''
					self.pkts_num = list()
					#Take all of the remaining packets in temp data and join them,
					#then split them about colons.
					self.bad_pkt_incices = (''.join(self.data_temp)).split(':')
					#Transmit Packet Resend
					self.handshaking_transmit(2)
					#Clear the temp data for next reception
					self.data_temp = list()
				#Received Transmission Complete at any point.
				elif self.data[0] == self.event_list[3] or temp_event == self.event_list[3]:
					#Cleanup variables to initialized state and return True
					self.cleanup()
					return True
				#Received Incomplete Transmission on first reception.
				elif self.data[0] == self.event_list[1]:
					#Join and split the bad packet indices in the packets trailing the 
					#frame packet.
					self.bad_pkt_indices = (''.join(self.data[1:])).split(':')
					#Transmit Packet Resend
					self.handshaking_transmit(2)]
					#Clear the temp data for next reception
					self.data_temp = list()
				#Received New Transmission or unknown event but received last packet.
				elif self.data[0] == self.event_list[0] or self.data[0] == '':
					#Check received frame for missing packets
					if self.frame_check():
						return "Handshaking complete."
				#Received Error Event, return control to outside.
				elif self.data[0] == self.event_list[4] or temp_event == self.event_list[4]:
					self.cleanup()
					return "Error"
			#Need testing to make sure this handshaking timeout padding works correctly.
			elif int(time.time() - time_1) >= 5 and self.initial_rcv is False:
				self.data_temp = list()
				if self.total_pkts != None:
					while len(self.data_temp) < self.total_pkts:
						self.data_temp.append('')
			#Overall receive timeout. This ensures the controller doesn't hang waiting for
			#data that was lost.
			elif int(time.time() - time_0) >= 35:
				temp_event = ''
				self.cleanup()
				return "Timeout"
			#Maximum number of complete frame receptions.
			elif self.hand_shaking_count == 5:
				temp_event = ''
				self.cleanup()
				return "Handshaking maximum reached."

	#Gives the outside the ability to change the frequency at which either side is transmitting
	#or receiving.
	def set_freq(self, new_freq, tx_rx=''):
		if tx_rx == 'tx':
			self.txrx_path.usrp_simple_sink_x_0.set_frequency(new_freq, verbose=True)
		elif tx_rx == 'rx':
			self.txrx_path.usrp_simple_source_x_0.set_frequency(new_freq, verbose=True)

	#These have been commented out for reason of not operating as intended.
	#def time_out_pad(self):
		#while len(self.data_temp) < self.total_pkts:
			#self.data_temp.append('')

	#def stop_trans(self):
		#self.txrx_path.stop()
		#self.txrx_path.wait()

	#def start_trans(self):
		#self.txrx_path.start()			

########################################################################################
#				RECEIVER TOOLS					       #
########################################################################################
	#Check initial frame for missing packets.
	def frame_check(self):
		#Check for any missing packets.
		if self.data.count('') == 0:
			#No missing packets, write received data to a file.
			fo = open('/home/student/Desktop/p', 'w')
			fo.write(''.join(self.data[1:]))
			fo.close()
			#Transmit Transmission Complete
			self.handshaking_transmit(3)
			self.cleanup()
			return True
		else:
			#There are missing packets in self.data
			#Determine missing packet indices
			self.bad_pkt_indexes()
			#Transmit Incomplete Transmission
			self.handshaking_transmit(1)
			self.data_temp = list()
			return False

	#Insert Missing Packets
	def insert_missing_pkts(self):
		#Clear variables to ensure no erroneous results
		self.pkt_count = None
		self.payload = ''
		#Set the contents of self.pkts into i incrimentally
		for i in self.pkt_num:
			#Slice packet count
			self.pkt_count = int(i[:i.index(':')])
			#Slice payload
			self.payload = i[i.index(':') + 1:]
			#Remove the empty string
			self.data.pop(self.pkt_count)
			#Insert the payload
			self.data.insert(self.pkt_count, self.payload)
		#Clear event variables for next reception
		self.pkt_num = list()
		self.pkt_count = None
		self.payload = ''

	def msgq_in(self):
		#Create a temp variable to hold the payloads
		temp = ''
		temp = self.txrx_path.msg_queue_out.delete_head_nowait().to_string()
		#Slice the payloads
		self.slice_total_count_pkt_count_payload(temp)

	#Transmitter for the handshaking process
	def handshaking_transmit(self, event_index):
		#Create a variable for the total number of packets in the event following
		total_pkts = None
		payload = ''
		#Event Index - Incomplete Transmission
		if event_index == 1:
			#Create a variable for the bad packet indices
			bad_packet_indices = ''
			#Join all of the indices and delimit them with colons
			bad_packet_indices = ':'.join(self.bad_pkt_indices)
			#Determine total number of packets. Integer division always rounds down
			#so there is two extra being added, one for the round down packet and one 
			#for the framer packet.
			total_pkts = len(bad_packet_indices)/self.payload_length + 2
			#If the length bad packet indices is a multiple of the payload length
			#then there was no round down and need to remove the addition of that 
			#packet from the total number.
			if len(bad_packet_indices)%self.payload_length == 0:
				total_pkts -= 1
			#Create and transmit the framer packet
			self.transmit_pkts(packetizer.make_packet(self.event_list[event_index], 0, total_pkts))
			#Transmit the rest of the frame starting with packet 1 to the total number of packets
			for i in range(1, total_pkts):
				#Slice off the payload
				payload = bad_packet_indices[:self.payload_length]
				#reconstruct bad packet indices without the first payloads data
				bad_packet_indices = bad_packet_indices[self.payload_length:]
				#Make the packet and transmit it.
				self.transmit_pkts(packetizer.make_packet(payload, i, total_pkts))
				#Clear payload
				payload = ''
			#Transmit a bit pad for the message source queue to force the queue to flush packets
			self.transmit_pkts('1010101010101010')
			#Clear bad packet indices for the next attempt
			self.bad_pkt_indices = list()
		#Packet Resend Event
		elif event_index == 2:
			#Ensure total_pkts is empty
			total_pkts = None
			#Total packets is the number of packets to be resent plus the frame packet
			total_pkts = len(self.bad_pkt_indices) + 1
			#Make then transmit the framer packet
			self.transmit_pkts(packetizer.make_packet(self.event_list[event_index], 0, total_pkts))
			#For all the indices contained in bad packet indices
			for i in self.bad_pkt_indices:
				#Make and transmit all of the missing packets from the original payloads
				self.transmit_pkts(packetizer.make_packet(self.data_split_for_pkts[int(i)], int(i), total_pkts))
			#Transmit a bit pad for the message source queue to force the queue to flush packets
			self.transmit_pkts('1010101010101010')
			#Clear bad packet indices for the next attempt
			self.bad_pkt_indices = list()
		#Transmission Complete Event, transmit a single packet with 'TC' as the event
		elif event_index == 3:
			self.transmit_pkts(packetizer.make_packet(self.event_list[event_index], 0, 1))
			self.transmit_pkts('1010101010101010')

	#Determine the missing packets as denoted by '' in the self.data
	def bad_pkt_indexes(self):
		#Initial cleanup work to make sure there are no residuals
		self.bad_pkt_indices = list()
		index = 0
		n_index = 0
		#While the length of bad packet indices is less than the number of empty strings
		while len(self.bad_pkt_indices) < self.data.count(''):
			#Determine the index of the first/next empty string
			index = self.data.index('', n_index)
			#Save that index number as a string into bad packet indices
			self.bad_pkt_indices.append(str(index))
			#Incriment n_index such that it always looks at the position after the colon just found
			n_index = index + 1

	#Remove the total packet count, packet number, and payload by slicing
	def slice_total_count_pkt_count_payload(self, temp):
		#Slice the total packet count
		self.total_pkts = int(temp[:temp.index(":")])
		#Adjust temp to continue
		temp = temp[temp.index(":") + 1:]
		#Save packet number
		self.pkt_count = int(temp[:temp.index(":")])
		#Save payload
		self.payload = temp[temp.index(":") + 1:]

########################################################################################
#				TRANSMITTER TOOLS				       #
########################################################################################
	def make_pkts(self, error_event=False):
		#Make sure total_pkts is None
		total_pkts = None
		#If not an error event
		if error_event is False:
			#Same the frame event in data split for packets
			self.data_split_for_pkts.append('NT')
			#Total packets is the length of the message divided by the
			#payload length + 2 to account for round down and the frame pkt
			total_pkts = len(self.data)/self.payload_length + 2
			#Remove 1 from the total count if the length of the data is
			#exactly equal to a multiple of the payload length
			if len(self.data)%self.payload_length == 0:
				total_pkts -= 1
			#Make and Transmit the frame packet
			self.transmit_pkts(packetizer.make_packet(self.event_list[0], 0, total_pkts))
			#Loop over the rest of the message
			for i in range(1, total_pkts):
				#Slice the payload
				payload = self.data[:self.payload_length]
				#Save the payload for handshaking
				self.data_split_for_pkts.append(payload)
				#Adjust self.data to everything after the payload length
				self.data = self.data[self.payload_length:]
				#Make and transmit the packet
				self.transmit_pkts(packetizer.make_packet(payload, i, total_pkts))
			#Transmit a queue pad
			self.transmit_pkts('1010101010101010')
		else:
			#Error Event, transmit error event and pad it
			self.transmit_pkts(packetizer.make_packet(self.event_list[4], 0, 1))
			self.transmit_pkts('1010101010101010')

########################################################################################
#				COMMON TOOLS					       #
########################################################################################
	def transmit_pkts(self, msg):
		#Make a message from the given input to transmit_pkts
		msg_0 = gr.message_from_string(msg)
		#Queue the message into the transceiver flowgraph
		self.txrx_path.msg_queue_in.insert_tail(msg_0)

	def cleanup(self):
		self.initial_rcv = True
		self.bad_pkt_indices = list()
		self.hand_shaking_count = 0
		self.data = list()
		self.data_temp = list()
		self.data_split_for_pkts = list()
		self.pkt_num = list()
		self.payload_length = 128
		self.pkt_count = None
		self.total_pkts = None
		self.payload = ''
