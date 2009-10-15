#!/usr/bin/env python
##################################################
# Gnuradio Python Flow Graph
# Title: FFT_data_aq
# Author: UAV Group
# Description: gnuradio flow graph
# Generated: Wed Oct 14 20:20:39 2009
##################################################

from gnuradio import blks2
from gnuradio import gr
from grc_gnuradio import wxgui as grc_wxgui
import numpy
import wx

class FFT_data_aq(grc_wxgui.top_block_gui):

	def __init__(self):
		grc_wxgui.top_block_gui.__init__(
			self,
			title="GRC - Executing: FFT_data_aq",
		)

		##################################################
		# Variables
		##################################################
		self.samp_rate = samp_rate = 32000
		self.freq_offset = freq_offset = 0

		##################################################
		# Blocks
		##################################################
		self.blks2_dxpsk_mod_0 = blks2.dbpsk_mod(
			samples_per_symbol=8,
			excess_bw=0.35,
			gray_code=True,
		)
		self.gr_file_sink_0 = gr.file_sink(gr.sizeof_gr_complex*1, "/home/student/Documents/RC.dat")
		self.gr_throttle_0 = gr.throttle(gr.sizeof_gr_complex*1, 256e3)
		self.random_source_x_0 = gr.vector_source_b(numpy.random.randint(0, 1, 1024), True)

		##################################################
		# Connections
		##################################################
		self.connect((self.random_source_x_0, 0), (self.blks2_dxpsk_mod_0, 0))
		self.connect((self.blks2_dxpsk_mod_0, 0), (self.gr_throttle_0, 0))
		self.connect((self.gr_throttle_0, 0), (self.gr_file_sink_0, 0))

	def set_samp_rate(self, samp_rate):
		self.samp_rate = samp_rate

	def set_freq_offset(self, freq_offset):
		self.freq_offset = freq_offset

if __name__ == '__main__':
	tb = FFT_data_aq()
	tb.Run()

