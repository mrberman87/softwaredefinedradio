#!/usr/bin/env python
##################################################
# Gnuradio Python Flow Graph
# Title: dbpsk_Tx_path_UAV
# Author: UAV Group 4/21/2009
# Description: gnuradio flow graph
# Generated: Tue Apr 21 11:17:13 2009
##################################################

from gnuradio import blks2
from gnuradio import gr
from grc_gnuradio import blks2 as grc_blks2
from grc_gnuradio import usrp as grc_usrp

class dbpsk_Tx_path_UAV(gr.top_block):

	def __init__(self):
		gr.top_block.__init__(self, "dbpsk_Tx_path_UAV")

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
		self.blks2_packet_encoder_0 = grc_blks2.packet_encoder(
			item_size_in=gr.sizeof_char*1,
			samples_per_symbol=8,
			bits_per_symbol=1,
			access_code="",
			pad_for_usrp=True,
			payload_length=1024,
		)
		self.gr_file_source_0 = gr.file_source(gr.sizeof_char*1, "insert file name here", False)
		self.gr_throttle_0 = gr.throttle(gr.sizeof_gr_complex*1, (8*samp_rate))
		self.usrp_simple_sink_x_0 = grc_usrp.simple_sink_c(which=0, side='A')
		self.usrp_simple_sink_x_0.set_interp_rate(500)
		self.usrp_simple_sink_x_0.set_frequency((440e6 + freq_offset), verbose=True)
		self.usrp_simple_sink_x_0.set_gain(-1)
		self.usrp_simple_sink_x_0.set_enable(True)

		##################################################
		# Connections
		##################################################
		self.connect((self.gr_throttle_0, 0), (self.usrp_simple_sink_x_0, 0))
		self.connect((self.blks2_dxpsk_mod_0, 0), (self.gr_throttle_0, 0))
		self.connect((self.blks2_packet_encoder_0, 0), (self.blks2_dxpsk_mod_0, 0))
		self.connect((self.gr_file_source_0, 0), (self.blks2_packet_encoder_0, 0))

	def set_samp_rate(self, samp_rate):
		self.samp_rate = samp_rate

	def set_freq_offset(self, freq_offset):
		self.freq_offset = freq_offset
		self.usrp_simple_sink_x_0.set_frequency((440e6 + self.freq_offset))

if __name__ == '__main__':
	tb = dbpsk_Tx_path_UAV()
	tb.start()
	#if buffer in USRP is empty, stop
	while(buffer not empty):
		pass
	tb.stop()

