#!/usr/bin/env python
##################################################
# Gnuradio Python Flow Graph
# Title: untitled
# Author: unknown
# Description: gnuradio flow graph
# Generated: Wed Apr  1 23:05:50 2009
##################################################

from gnuradio import blks2
from gnuradio import gr
from grc_gnuradio import blks2 as grc_blks2
from grc_gnuradio import wxgui as grc_wxgui
import numpy
import wx

class top_block(grc_wxgui.top_block_gui):

	def __init__(self):
		grc_wxgui.top_block_gui.__init__(
			self,
			title="GRC - Executing: untitled",
		)

		##################################################
		# Variables
		##################################################
		self.samp_rate = samp_rate = 32000

		##################################################
		# Blocks
		##################################################
		self.blks2_dxpsk_mod_0 = blks2.dbpsk_mod(
			samples_per_symbol=8,
			excess_bw=0.35,
			gray_code=True,
		)
		self.blks2_packet_encoder_0 = grc_blks2.packet_mod_b(grc_blks2.packet_encoder(
				samples_per_symbol=2,
				bits_per_symbol=1,
				access_code="",
				pad_for_usrp=True,
			),
			payload_length=1000,
		)
		self.gr_file_sink_0 = gr.file_sink(gr.sizeof_gr_complex*1, "/home/sab/Desktop/data.dat")
		self.gr_throttle_1 = gr.throttle(gr.sizeof_gr_complex*1, (16*samp_rate))
		self.random_source_x_0 = gr.vector_source_b(numpy.random.randint(0, 2, 1000), True)

		##################################################
		# Connections
		##################################################
		self.connect((self.random_source_x_0, 0), (self.blks2_packet_encoder_0, 0))
		self.connect((self.blks2_packet_encoder_0, 0), (self.blks2_dxpsk_mod_0, 0))
		self.connect((self.blks2_dxpsk_mod_0, 0), (self.gr_throttle_1, 0))
		self.connect((self.gr_throttle_1, 0), (self.gr_file_sink_0, 0))

	def set_samp_rate(self, samp_rate):
		self.samp_rate = samp_rate

if __name__ == '__main__':
	tb = top_block()
	tb.Run()

