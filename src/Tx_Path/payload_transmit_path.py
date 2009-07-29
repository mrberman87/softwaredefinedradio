#!/usr/bin/env python
##################################################
# Gnuradio Python Flow Graph
# Title: Payload Transmit Path
# Author: Charles Judah
# Generated: Tue Jul 28 09:49:02 2009
##################################################

from gnuradio import gr, blks2
from gnuradio.eng_option import eng_option
from grc_gnuradio import usrp as grc_usrp
from optparse import OptionParser

class payload_transmit_path(gr.top_block):

	def __init__(self):
		gr.top_block.__init__(self, "Payload Transmit Path")

		##################################################
		# Blocks
		##################################################

		#DPSK Modulator
		self.blks2_dxpsk_mod_0 = blks2.dbpsk_mod(
			#Adjusts bandwidth and data rate
			samples_per_symbol=8,
			#Amount of excess bandwidth for raised cosine
			excess_bw=0.35,
			#Leave true to be able to use BER known functions
			gray_code=True,
			#True to see what the Modulator information is
			verbose=False,
			#Unknown what goes in log or where it's located
			log=False,
		)
		#Constant Multiplier for amplitude adjustment before USRP receives data
		self.gr_multiply_const_vxx_0 = gr.multiply_const_vcc((80, ))
		#Message Source to receive data from outside of the script
		self.gr_message_source_0 = gr.message_source(gr.sizeof_char*1)
		#Data destination to be sent out over RF
		#Which refers to how many USRPS are connected to the computer, 0 for 1 connected
		#Side refers to which side on the motherboard, ours is A
		self.usrp_simple_sink_x_0 = grc_usrp.simple_sink_c(which=0, side="A")
		#Interpolation the USRP will do to reach 128 MS/s
		self.usrp_simple_sink_x_0.set_interp_rate(500)
		#Set frequency of USRP to transmit frequency 
		#verbose=True to print frequency information
		self.usrp_simple_sink_x_0.set_frequency(445e6, verbose=False)
		#Gain unknown effect at this time
		self.usrp_simple_sink_x_0.set_gain(0)
		#set_enable(True) makes transmit enabled
		self.usrp_simple_sink_x_0.set_enable(True)
		#set_auto_tr(True) enables auto t/r for the RFX series boards only
		self.usrp_simple_sink_x_0.set_auto_tr(True)

		##################################################
		# Connections:
		#[Message Source]->[Modulator]->[Amplitude Multiplier]->[USRP] 
		##################################################
		
		self.connect((self.gr_multiply_const_vxx_0, 0), (self.usrp_simple_sink_x_0, 0))
		self.connect((self.blks2_dxpsk_mod_0, 0), (self.gr_multiply_const_vxx_0, 0))
		self.connect((self.gr_message_source_0, 0), (self.blks2_dxpsk_mod_0, 0))

#Testing method acting as outside higher block calling the class to transmit
def main():
	#Assign the transmit path class to tb
	tb = payload_transmit_path()
	#start the transmit path
	tb.start()
	#variable to help control the data acquisition/passing loop to make it stable
	end_loop = 0
	#loop to receive data from the user
	while True:
		data = ''
		#currently a user input file path to test data acquisition into the transmit path
		new_file = raw_input("Enter Location >> ")
		#to handle input output errors if location is wrong
		try:
			#attempt to open the file
			ui = open(new_file, 'r')
			#attempt to read the file
			data = ui.read()
			#close the file
			ui.close()
		#In the case of an improper file location, the exception will catch it and handle it
		except IOError:
			#Inform the user their path was wrong
			print "Invalid file path."
			#Ensure data has nothing in it
			data = ''
		#If data has nothing in it, basically the script was unable to open a file for data
		if data != '':
			#This is where the magic happens
			#tb references the payload_transmit_path class
			#gr_message_source_0 is the destination of all outside data
			#msgq() is the message queue associated with the message source
			#insert_tail() receives two arguements, thus requires the next comment
			#gr.message_from_string() takes a string input and formats it for insert_tail's message format
			#This process always inserts into the bottom of the queue while the queue is always read from
			#the head.
			tb.gr_message_source_0.msgq().insert_tail(gr.message_from_string(data))
		#Determine if user wants to stop, mainly for testing purposes
		end_loop = raw_input("1 to quit. >> ")
		#If user entered 1 leave while loop
		if end_loop == '1':
			#leave while loop and go to next line outside of while
			break
	#sends the message source the signal that there is no more data and to clean itself out
	tb.gr_message_source_0.msgq().insert_tail(gr.message(1))
	#stops the flow graph
	tb.stop()

#Is the first thing to run in any python script
if __name__ == '__main__':
	#Option parser GRC adds to all flow graphs now
	parser = OptionParser(option_class=eng_option, usage="%prog: [options]")
	(options, args) = parser.parse_args()
	#Attempt to run the main() definition
	try:
		#Where the work is done
		main()
	#At keyboard interrupt
	except KeyboardInterrupt:
		#Do nothing but still gets handle taken care of
		pass

