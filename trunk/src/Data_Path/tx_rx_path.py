#!/usr/bin/env python
##################################################
# Gnuradio Python Flow Graph
# Title: Transmit and Receive Path
# Author: Charles Judah
# Generated: Tue Aug 11 13:17:45 2009
##################################################

from gnuradio import blks2
from gnuradio import gr
from gnuradio.eng_option import eng_option
from gnuradio.gr import firdes
from grc_gnuradio import blks2 as grc_blks2
from grc_gnuradio import usrp as grc_usrp
from optparse import OptionParser

class tx_rx_path(gr.top_block):

	def __init__(self):
		gr.top_block.__init__(self, "Transmit and Receive Path")

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
			verbose=False,
			log=False,
		)
		self.blks2_dxpsk_mod_0 = blks2.dbpsk_mod(
			samples_per_symbol=8,
			excess_bw=0.35,
			gray_code=True,
			verbose=False,
			log=False,
		)
		self.blks2_packet_decoder_0 = grc_blks2.packet_demod_b(grc_blks2.packet_decoder(
				access_code="",
				threshold=-1,
				callback=lambda ok, payload: self.blks2_packet_decoder_0.recv_pkt(ok, payload),
			),
		)
		self.gr_multiply_const_vxx_0 = gr.multiply_const_vcc((8000, ))
		self.msg_queue_out = gr.msg_queue()
		self.gr_message_sink_0 = gr.message_sink(gr.sizeof_char*1, self.msg_queue_out, False)
		self.gr_message_source_0 = gr.message_source(gr.sizeof_char*1)
		self.msg_queue_in = self.gr_message_source_0.msgq()
		self.usrp_simple_sink_x_0 = grc_usrp.simple_sink_c(which=0, side="A")
		self.usrp_simple_sink_x_0.set_interp_rate(500)
		self.usrp_simple_sink_x_0.set_frequency(440e6, verbose=True)
		self.usrp_simple_sink_x_0.set_gain(0)
		self.usrp_simple_sink_x_0.set_enable(True)
		self.usrp_simple_sink_x_0.set_auto_tr(True)
		self.usrp_simple_source_x_0 = grc_usrp.simple_source_c(which=0, side="A", rx_ant="RX2")
		self.usrp_simple_source_x_0.set_decim_rate(250)
		self.usrp_simple_source_x_0.set_frequency(440.05e6, verbose=True)
		self.usrp_simple_source_x_0.set_gain(20)

		##################################################
		# Connections
		##################################################
		self.connect((self.gr_message_source_0, 0), (self.blks2_dxpsk_mod_0, 0))
		self.connect((self.blks2_dxpsk_mod_0, 0), (self.gr_multiply_const_vxx_0, 0))
		self.connect((self.gr_multiply_const_vxx_0, 0), (self.usrp_simple_sink_x_0, 0))
		self.connect((self.usrp_simple_source_x_0, 0), (self.blks2_dxpsk_demod_0, 0))
		self.connect((self.blks2_dxpsk_demod_0, 0), (self.blks2_packet_decoder_0, 0))
		self.connect((self.blks2_packet_decoder_0, 0), (self.gr_message_sink_0, 0))
