#!/usr/bin/env python
##################################################
# Gnuradio Python Flow Graph
# Title: dbpsk_Rx_path_UAV
# Author: UAV Group
# Description: gnuradio flow graph
# Generated: Tue Apr 21 11:41:18 2009
##################################################

from gnuradio import blks2
from gnuradio import gr
from grc_gnuradio import blks2 as grc_blks2
from grc_gnuradio import usrp as grc_usrp

class dbpsk_Rx_path_UAV(gr.top_block):

	def __init__(self):
		gr.top_block.__init__(self, "dbpsk_Rx_path_UAV")

		##################################################
		# Variables
		##################################################
		self.samp_rate = samp_rate = 32000
		self.freq_offset = freq_offset = 0

		##################################################
		# Blocks
		##################################################
		self.blks2_dxpsk_demod_0 = blks2.dbpsk_demod(
			samples_per_symbol=8,
			excess_bw=0.35,
			costas_alpha=0.175,
			gain_mu=0.175,
			mu=0.5,
			omega_relative_limit=0.005,
			gray_code=True,
		)
		self.blks2_packet_decoder_0 = grc_blks2.packet_decoder(
			item_size_out=gr.sizeof_char*1,
			access_code="",
			threshold=-1,
		)
		self.gr_file_sink_0 = gr.file_sink(gr.sizeof_char*1, "insert file name here")
		self.gr_throttle_0 = gr.throttle(gr.sizeof_gr_complex*1, (8*samp_rate))
		self.usrp_simple_source_x_0 = grc_usrp.simple_source_c(which=0, side='B', rx_ant='TX/RX')
		self.usrp_simple_source_x_0.set_decim_rate(250)
		self.usrp_simple_source_x_0.set_frequency((440e6 + freq_offset), verbose=True)
		self.usrp_simple_source_x_0.set_gain(0)

		##################################################
		# Connections
		##################################################
		self.connect((self.blks2_dxpsk_demod_0, 0), (self.blks2_packet_decoder_0, 0))
		self.connect((self.blks2_packet_decoder_0, 0), (self.gr_file_sink_0, 0))
		self.connect((self.usrp_simple_source_x_0, 0), (self.gr_throttle_0, 0))
		self.connect((self.gr_throttle_0, 0), (self.blks2_dxpsk_demod_0, 0))

	def set_samp_rate(self, samp_rate):
		self.samp_rate = samp_rate

	def set_freq_offset(self, freq_offset):
		self.freq_offset = freq_offset
		self.usrp_simple_source_x_0.set_frequency((440e6 + self.freq_offset))

if __name__ == '__main__':
	print "Running Rx module..."
	tb = dbpsk_Rx_path_UAV()
	tb.start()
	#raw_input('Press Enter to quit: ')
	tb.stop()

