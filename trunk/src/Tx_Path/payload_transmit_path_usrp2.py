#!/usr/bin/env python
##################################################
# Gnuradio Python Flow Graph
# Title: Payload Transmit Path
# Author: Charles Judah
# Generated: Tue Jul 28 09:49:02 2009
##################################################

from gnuradio import gr, blks2
from gnuradio import usrp2
from gnuradio.eng_option import eng_option
from optparse import OptionParser

class payload_transmit_path(gr.top_block):

	def __init__(self):
		gr.top_block.__init__(self, "Payload Transmit Path USRP2")

		##################################################
		# Blocks
		##################################################
		self.blks2_dxpsk_mod_0 = blks2.dbpsk_mod(
			samples_per_symbol=8,
			excess_bw=0.35,
			gray_code=True,
			verbose=False,
			log=False,
		)
		self.gr_message_source_0 = gr.message_source(gr.sizeof_char*1)
		self.usrp2_sink_xxxx_0 = usrp2.sink_32fc("eth1", "00:50:c2:85:31:ad")
		self.usrp2_sink_xxxx_0.set_interp(500)
		self.usrp2_sink_xxxx_0.set_center_freq(2.4e9)
		self.usrp2_sink_xxxx_0.set_gain(1)

		##################################################
		# Connections:
		#[Message Source]->[Modulator]->[Amplitude Multiplier]->[USRP2] 
		##################################################	
		self.connect((self.blks2_dxpsk_mod_0, 0), (self.usrp2_sink_xxxx_0, 0))
		self.connect((self.gr_message_source_0, 0), (self.blks2_dxpsk_mod_0, 0))

def main():
	tb = payload_transmit_path()
	tb.start()
	end_loop = 0
	while True:
		data = ''
		new_file = raw_input("Enter Location >> ")
		try:
			ui = open(new_file, 'r')
			data = ui.read()
			ui.close()
		except IOError:
			print "Invalid file path."
			data = ''
		if data != '':
			tb.gr_message_source_0.msgq().insert_tail(gr.message_from_string(data))
		end_loop = raw_input("1 to quit. >> ")
		if end_loop == '1':
			break
	tb.gr_message_source_0.msgq().insert_tail(gr.message(1))
	tb.stop()

if __name__ == '__main__':
	parser = OptionParser(option_class=eng_option, usage="%prog: [options]")
	(options, args) = parser.parse_args()
	try:
		main()
	except KeyboardInterrupt:
		pass
