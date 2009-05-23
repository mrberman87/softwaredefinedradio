#!/usr/bin/env python
##################################################
# Gnuradio Python Flow Graph
# Title: dbpsk_Rx_path_UAV
# Author: UAV Group
# Description: gnuradio flow graph
# Generated: Thu May 21 15:40:07 2009
##################################################

from gnuradio import blks2
from gnuradio import gr
from gnuradio.eng_option import eng_option
from grc_gnuradio import blks2 as grc_blks2
from grc_gnuradio import usrp as grc_usrp
from grc_gnuradio import wxgui as grc_wxgui
from optparse import OptionParser
import wx

class dbpsk_Rx_path_UAV(grc_wxgui.top_block_gui):

	def __init__(self, options):
		grc_wxgui.top_block_gui.__init__(
			self,
			title="GRC - Executing: dbpsk_Rx_path_UAV",
		)

		##################################################
		# Variables
		##################################################
		self.samp_rate = samp_rate = 32000

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
		self.blks2_packet_decoder_0 = grc_blks2.packet_demod_b(grc_blks2.packet_decoder(
				access_code="",
				threshold=-1,
				callback=lambda ok, payload: self.blks2_packet_decoder_0.recv_pkt(ok, payload),
			),
		)
		self.gr_file_sink_0 = gr.file_sink(gr.sizeof_char*1, "/home/michael/Desktop/gay_studd")
		self.gr_throttle_0 = gr.throttle(gr.sizeof_gr_complex*1, (8*samp_rate))
		self.usrp_simple_source_x_0 = grc_usrp.simple_source_c(which=0, side="B", rx_ant="TX/RX")
		self.usrp_simple_source_x_0.set_decim_rate(250)
		self.usrp_simple_source_x_0.set_frequency(440e6, verbose=True)
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

if __name__ == '__main__':
	parser = OptionParser(option_class=eng_option, usage="%prog: [options]")
	(options, args) = parser.parse_args()
	tb = dbpsk_Rx_path_UAV(options)
	tb.Run()

