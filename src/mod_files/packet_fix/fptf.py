#!/usr/bin/env python
##################################################
# Gnuradio Python Flow Graph
# Title: fptf
# Author: Charles Judah
# Description: gnuradio flow graph
# Generated: Mon May 25 17:59:45 2009
##################################################

from gnuradio import blks2
from gnuradio import gr
from grc_gnuradio import blks2 as grc_blks2

class fptf(gr.top_block):

	def __init__(self):
		gr.top_block.__init__(self, "fptf")

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
		self.blks2_dxpsk_mod_0 = blks2.dbpsk_mod(
			samples_per_symbol=8,
			excess_bw=0.35,
			gray_code=True,
		)
		self.blks2_packet_decoder_0 = grc_blks2.packet_demod_b(grc_blks2.packet_decoder(
				access_code="",
				threshold=-1,
				callback=lambda ok, payload: self.blks2_packet_decoder_0.recv_pkt(ok, payload),
			),
		)
		self.blks2_packet_encoder_0 = grc_blks2.packet_mod_b(grc_blks2.packet_encoder(
				samples_per_symbol=8,
				bits_per_symbol=1,
				access_code="",
				pad_for_usrp=True,
			),
			payload_length=1024,
		)
		self.gr_file_sink_0 = gr.file_sink(gr.sizeof_char*1, "/home/sab/Desktop/copy")
		self.gr_file_source_0 = gr.file_source(gr.sizeof_char*1, "/home/sab/Desktop/image", False)
		self.gr_throttle_0 = gr.throttle(gr.sizeof_char*1, 256e3)

		##################################################
		# Connections
		##################################################
		self.connect((self.gr_file_source_0, 0), (self.blks2_packet_encoder_0, 0))
		self.connect((self.blks2_packet_encoder_0, 0), (self.blks2_dxpsk_mod_0, 0))
		self.connect((self.blks2_dxpsk_mod_0, 0), (self.blks2_dxpsk_demod_0, 0))
		self.connect((self.blks2_packet_decoder_0, 0), (self.gr_throttle_0, 0))
		self.connect((self.blks2_dxpsk_demod_0, 0), (self.blks2_packet_decoder_0, 0))
		self.connect((self.gr_throttle_0, 0), (self.gr_file_sink_0, 0))

if __name__ == '__main__':
	tb = fptf()
	tb.start()
	raw_input('Press Enter to quit: ')
	tb.stop()

