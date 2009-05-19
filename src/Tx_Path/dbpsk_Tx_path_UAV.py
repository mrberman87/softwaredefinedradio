#!/usr/bin/env python
##################################################
# Gnuradio Python Flow Graph
# Title: dbpsk_Tx_path_UAV
# Author: UAV Group 4/21/2009
# Description: gnuradio flow graph
# Generated: Tue May 19 16:42:39 2009
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
		self.variable_chooser_0 = variable_chooser_0 = [8000, 0][0]
		self.samp_rate = samp_rate = 32000
		self.freq_offset = freq_offset = -3100

		##################################################
		# Controls
		##################################################
		_variable_chooser_0_control = grc_wxgui.drop_down_control(
			window=self.GetWin(),
			callback=self.set_variable_chooser_0,
			label='variable_chooser_0',
			index=0,
			choices=[8000, 0],
			labels=[],
		)
		self.Add(_variable_chooser_0_control)

		##################################################
		# Blocks
		##################################################
		self.blks2_dxpsk_mod_0 = blks2.dbpsk_mod(
			samples_per_symbol=8,
			excess_bw=0.35,
			gray_code=True,
		)
		self.blks2_packet_encoder_0 = grc_blks2.packet_mod_b(grc_blks2.packet_encoder(
				samples_per_symbol=8,
				bits_per_symbol=1,
				access_code="",
				pad_for_usrp=False,
			),
			payload_length=1024,
		)
		self.gr_file_source_0 = gr.file_source(gr.sizeof_char*1, "/home/sab/softwaredefinedradio/src/Tx_Path/Command", True)
		self.gr_multiply_const_vxx_0 = gr.multiply_const_vcc((variable_chooser_0, ))
		self.gr_throttle_0 = gr.throttle(gr.sizeof_gr_complex*1, (8*samp_rate))
		self.usrp_simple_sink_x_0 = grc_usrp.simple_sink_c(which=0, side='A')
		self.usrp_simple_sink_x_0.set_interp_rate(500)
		self.usrp_simple_sink_x_0.set_frequency(439997900, verbose=True)
		self.usrp_simple_sink_x_0.set_gain(-1)
		self.usrp_simple_sink_x_0.set_enable(True)

		##################################################
		# Connections
		##################################################
		self.connect((self.blks2_dxpsk_mod_0, 0), (self.gr_throttle_0, 0))
		self.connect((self.blks2_packet_encoder_0, 0), (self.blks2_dxpsk_mod_0, 0))
		self.connect((self.gr_file_source_0, 0), (self.blks2_packet_encoder_0, 0))
		self.connect((self.gr_throttle_0, 0), (self.gr_multiply_const_vxx_0, 0))
		self.connect((self.gr_multiply_const_vxx_0, 0), (self.usrp_simple_sink_x_0, 0))

	def set_variable_chooser_0(self, variable_chooser_0):
		self.variable_chooser_0 = variable_chooser_0
		self.gr_multiply_const_vxx_0.set_k((self.variable_chooser_0, ))

	def set_samp_rate(self, samp_rate):
		self.samp_rate = samp_rate

	def set_freq_offset(self, freq_offset):
		self.freq_offset = freq_offset

if __name__ == '__main__':
	tb = dbpsk_Tx_path_UAV()
	tb.start()
	raw_input('Press Enter to quit: ')
	tb.stop()

