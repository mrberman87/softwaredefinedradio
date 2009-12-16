#!/usr/bin/env python

from gnuradio import blks2
from gnuradio import gr
from gnuradio.eng_option import eng_option
from gnuradio.gr import firdes
from grc_gnuradio import blks2 as grc_blks2
from grc_gnuradio import usrp as grc_usrp
from optparse import OptionParser

class tx_rx_path(gr.top_block):

	def __init__(self, fc, centoff, foffset_tx, foffset_rx, scheme):
		gr.top_block.__init__(self, "Transmit and Receive Path")

		##################################################
		# Variables
		##################################################
		self.filter_offset_rx = foffset_rx
		self.filter_offset_tx = foffset_tx
		self.center_f_offset = centoff
		self.scheme = scheme
		self.fc = fc
		self.sps = 8

		##################################################
		# Blocks
		##################################################
		self.low_pass_filter_0 = gr.fir_filter_ccf(1, firdes.low_pass(
			1, 256e3, 25e3, 5e3, firdes.WIN_HAMMING, 6.76))
		self.low_pass_filter_1 = gr.fir_filter_ccf(1, firdes.low_pass(
			1, 256e3, 25e3, 5e3, firdes.WIN_HAMMING, 6.76))
		if self.scheme == 'bpsk':
			self.dbpsk_demod = blks2.dbpsk_demod(
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
			self.dbpsk_mod = blks2.dbpsk_mod(
				samples_per_symbol=self.sps,
				excess_bw=0.35,
				gray_code=True,
				verbose=False,
				log=False,
			)
		"""elif self.scheme == 'qpsk':
			self.dqpsk_demod = blks2.dqpsk_demod(
				samples_per_symbol=self.sps,
				excess_bw=0.40,
				costas_alpha=0.175,
				gain_mu=0.175,
				mu=0.5,
				omega_relative_limit=0.005,
				gray_code=True,
				verbose=False,
				log=False,
			)
			self.dqpsk_mod = blks2.dqpsk_mod(
				samples_per_symbol=self.sps,
				excess_bw=0.40,
				gray_code=True,
				verbose=False,
				log=False,
			)
		elif self.scheme == '8psk':
			self.d8psk_demod = blks2.d8psk_demod(
				samples_per_symbol=self.sps,
				excess_bw=0.45,
				costas_alpha=0.175,
				gain_mu=0.175,
				mu=0.5,
				omega_relative_limit=0.005,
				gray_code=True,
				verbose=False,
				log=False,
			)
			self.d8psk_mod = blks2.d8psk_mod(
				samples_per_symbol=self.sps,
				excess_bw=0.45,
				gray_code=True,
				verbose=False,
				log=False,
			)
		"""
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
		'''self.usrp_simple_sink_x_0 = grc_usrp.simple_sink_c(which=0, side="A")
		self.usrp_simple_sink_x_0.set_interp_rate(500)
		self.usrp_simple_sink_x_0.set_frequency((self.fc + self.filter_offset_tx + self.center_f_offset))
		self.usrp_simple_sink_x_0.set_gain(0)
		self.usrp_simple_sink_x_0.set_enable(True)
		self.usrp_simple_sink_x_0.set_auto_tr(True)
		self.usrp_simple_source_x_0 = grc_usrp.simple_source_c(which=0, side="A", rx_ant="RX2")
		self.usrp_simple_source_x_0.set_decim_rate(250)
		self.usrp_simple_source_x_0.set_frequency((self.fc + self.filter_offset_rx + self.center_f_offset))
		self.usrp_simple_source_x_0.set_gain(40)'''

		##################################################
		# Connections
		##################################################
		#Transmitter
		if self.scheme == 'bpsk':
			self.connect((self.gr_message_source_0, 0), (self.dbpsk_mod, 0))
			self.connect((self.dbpsk_mod, 0), (self.gr_multiply_const_vxx_0, 0))
		"""elif self.scheme == 'qpsk':
			self.connect((self.gr_message_source_0, 0), (self.dqpsk_mod, 0))
			self.connect((self.dqpsk_mod, 0), (self.gr_multiply_const_vxx_0, 0))
		elif self.scheme == '8psk':
			self.connect((self.gr_message_source_0, 0), (self.d8psk_mod, 0))
			self.connect((self.d8psk_mod, 0), (self.gr_multiply_const_vxx_0, 0))
		"""
		self.connect((self.gr_multiply_const_vxx_0, 0), (self.low_pass_filter_0, 0))
		#self.connect((self.low_pass_filter_0, 0), (self.usrp_simple_sink_x_0, 0))

		#Receiver
		#self.connect((self.usrp_simple_source_x_0, 0), (self.gr_multiply_xx_0, 0))
		#self.connect((self.gr_sig_source_x_0_0, 0), (self.gr_multiply_xx_0, 1))
		#self.connect((self.gr_multiply_xx_0, 0), (self.low_pass_filter_1, 0))
		if self.scheme == 'bpsk':
			#self.connect((self.low_pass_filter_1, 0), (self.dbpsk_demod, 0))
			self.connect((self.low_pass_filter_0, 0), (self.dbpsk_demod, 0))
			self.connect((self.dbpsk_demod, 0), (self.blks2_packet_decoder_0, 0))
		"""elif self.scheme == 'qpsk':
			self.connect((self.low_pass_filter_1, 0), (self.dqpsk_demod, 0))
			self.connect((self.dqpsk_demod, 0), (self.blks2_packet_decoder_0, 0))
		elif self.scheme == '8psk':
			self.connect((self.low_pass_filter_1, 0), (self.d8psk_demod, 0))
			self.connect((self.d8psk_demod, 0), (self.blks2_packet_decoder_0, 0))
		"""
		self.connect((self.blks2_packet_decoder_0, 0), (self.gr_message_sink_0, 0))
