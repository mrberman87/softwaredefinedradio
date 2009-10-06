#!/usr/bin/env python
##################################################
# Gnuradio Python Flow Graph
# Title: FFT_data_aq
# Author: UAV Group
# Description: gnuradio flow graph
# Generated: Wed Sep 30 19:22:42 2009
##################################################

from gnuradio import gr
from gnuradio.eng_option import eng_option
from grc_gnuradio import usrp as grc_usrp
from optparse import OptionParser

class FFT_data_aq(gr.top_block):

	def __init__(self):
		gr.top_block.__init__(self, "FFT_data_aq")

		##################################################
		# Variables
		##################################################
		self.samp_rate = samp_rate = 32000
		self.freq_offset = freq_offset = 0

		##################################################
		# Blocks
		##################################################
		self.gr_file_sink_0 = gr.file_sink(gr.sizeof_gr_complex*1, "/home/sab/Desktop/RC.dat")
		self.usrp_simple_source_x_0 = grc_usrp.simple_source_c(which=0, side="A", rx_ant="TX/RX")
		self.usrp_simple_source_x_0.set_decim_rate(250)
		self.usrp_simple_source_x_0.set_frequency((440e6 + freq_offset), verbose=True)
		self.usrp_simple_source_x_0.set_gain(-1)

		##################################################
		# Connections
		##################################################
		self.connect((self.usrp_simple_source_x_0, 0), (self.gr_file_sink_0, 0))

	def set_samp_rate(self, samp_rate):
		self.samp_rate = samp_rate

	def set_freq_offset(self, freq_offset):
		self.freq_offset = freq_offset
		self.usrp_simple_source_x_0.set_frequency((440e6 + self.freq_offset))

if __name__ == '__main__':
	parser = OptionParser(option_class=eng_option, usage="%prog: [options]")
	(options, args) = parser.parse_args()
	tb = FFT_data_aq()
	tb.start()
	raw_input('Press Enter to quit: ')
	tb.stop()

