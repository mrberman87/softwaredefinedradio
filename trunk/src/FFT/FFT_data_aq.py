#!/usr/bin/env python
##################################################
# Gnuradio Python Flow Graph
# Title: FFT_data_aq
# Author: UAV Group
# Description: gnuradio flow graph
# Generated: Tue Apr 21 09:25:28 2009
##################################################

from gnuradio import gr
from grc_gnuradio import usrp as grc_usrp
import time

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
		self.gr_file_sink_0 = gr.file_sink(gr.sizeof_gr_complex*1, "/uav/RC.dat")
		self.gr_throttle_0 = gr.throttle(gr.sizeof_gr_complex*1, (3*samp_rate))
		self.usrp_simple_source_x_0 = grc_usrp.simple_source_c(which=0, side='A', rx_ant='TX/RX')
		self.usrp_simple_source_x_0.set_decim_rate(250)
		self.usrp_simple_source_x_0.set_frequency((440e6 + freq_offset), verbose=True)
		self.usrp_simple_source_x_0.set_gain(-1)

		##################################################
		# Connections
		##################################################
		self.connect((self.gr_throttle_0, 0), (self.gr_file_sink_0, 0))
		self.connect((self.usrp_simple_source_x_0, 0), (self.gr_throttle_0, 0))

	def set_samp_rate(self, samp_rate):
		self.samp_rate = samp_rate

	def set_freq_offset(self, freq_offset):
		self.freq_offset = freq_offset
		self.usrp_simple_source_x_0.set_frequency((440e6 + self.freq_offset))

if __name__ == '__main__':
	tb = FFT_data_aq()
	tb.start()
	time.sleep(2)
	tb.stop()

