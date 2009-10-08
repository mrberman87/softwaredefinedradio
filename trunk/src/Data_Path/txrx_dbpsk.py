#!/usr/bin/env python
##################################################
# Gnuradio Python Flow Graph
# Title: Transmit and Receive Path
# Author: Charles Judah
# Generated: Tue Aug 11 13:17:45 2009
##################################################

##################################################
#	     Operating Frequencies		 #
##################################################
#	USRP 1		#	USRP 2		 #
#			#			 #
# Tx:	fc		#	fc + 100e3	 #
# Rx:	fc + 50e3	#	fc - 50e3	 #
#			#			 #
##################################################

from gnuradio import blks2
from gnuradio import gr
from gnuradio.eng_option import eng_option
from gnuradio.gr import firdes
from grc_gnuradio import blks2 as grc_blks2
from grc_gnuradio import usrp as grc_usrp
from optparse import OptionParser

class tx_rx_path(gr.top_block):

	def __init__(self, f_offset_rx, f_offset_tx, cent_off, f_c):
		gr.top_block.__init__(self, "Transmit and Receive Path")

		##################################################
		# Variables
		##################################################
		self.filter_offset_rx = f_offset_rx
		self.filter_offset_tx = f_offset_tx
		self.center_f_offset = cent_off
		self.fc = f_c
		self.sps = 8

		##################################################
		# Blocks
		##################################################
		self.low_pass_filter_0 = gr.fir_filter_ccf(1, firdes.low_pass(
			1, 256e3, 25e3, 5e3, firdes.WIN_HAMMING, 6.76))
		self.low_pass_filter_1 = gr.fir_filter_ccf(1, firdes.low_pass(
			1, 256e3, 25e3, 5e3, firdes.WIN_HAMMING, 6.76))
		self.blks2_dxpsk_demod_0 = blks2.dbpsk_demod(
			samples_per_symbol=self.sps,
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
			samples_per_symbol=self.sps,
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
		self.gr_multiply_const_vxx_0 = gr.multiply_const_vcc(((4500), ))
		self.gr_multiply_xx_0 = gr.multiply_vcc(1)
		self.gr_sig_source_x_0_0 = gr.sig_source_c(256e3, gr.GR_COS_WAVE, -50e3, 1, 0)
		self.msg_queue_out = gr.msg_queue()
		self.gr_message_sink_0 = gr.message_sink(gr.sizeof_char*1, self.msg_queue_out, False)
		self.gr_message_source_0 = gr.message_source(gr.sizeof_char*1)
		self.msg_queue_in = self.gr_message_source_0.msgq()
		self.usrp_simple_sink_x_0 = grc_usrp.simple_sink_c(which=0, side="A")
		self.usrp_simple_sink_x_0.set_interp_rate(500)
		self.usrp_simple_sink_x_0.set_frequency((self.fc + self.filter_offset_tx + self.center_f_offset))
		self.usrp_simple_sink_x_0.set_gain(0)
		self.usrp_simple_sink_x_0.set_enable(True)
		self.usrp_simple_sink_x_0.set_auto_tr(True)
		self.usrp_simple_source_x_0 = grc_usrp.simple_source_c(which=0, side="A", rx_ant="RX2")
		self.usrp_simple_source_x_0.set_decim_rate(250)
		self.usrp_simple_source_x_0.set_frequency((self.fc + self.filter_offset_rx + self.center_f_offset))
		self.usrp_simple_source_x_0.set_gain(40)

		##################################################
		# Connections
		##################################################
		#Transmitter
		self.connect((self.gr_message_source_0, 0), (self.blks2_dxpsk_mod_0, 0))
		self.connect((self.blks2_dxpsk_mod_0, 0), (self.gr_multiply_const_vxx_0, 0))
		self.connect((self.gr_multiply_const_vxx_0, 0), (self.low_pass_filter_0, 0))
		self.connect((self.low_pass_filter_0, 0), (self.usrp_simple_sink_x_0, 0))
		#Receiver
		self.connect((self.usrp_simple_source_x_0, 0), (self.gr_multiply_xx_0, 0))
		self.connect((self.gr_sig_source_x_0_0, 0), (self.gr_multiply_xx_0, 1))
		self.connect((self.gr_multiply_xx_0, 0), (self.low_pass_filter_1, 0))
		self.connect((self.low_pass_filter_1, 0), (self.blks2_dxpsk_demod_0, 0))
		self.connect((self.blks2_dxpsk_demod_0, 0), (self.blks2_packet_decoder_0, 0))
		self.connect((self.blks2_packet_decoder_0, 0), (self.gr_message_sink_0, 0))
