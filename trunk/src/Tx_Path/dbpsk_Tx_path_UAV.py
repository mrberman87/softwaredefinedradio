#!/usr/bin/env python
##################################################
# Gnuradio Python Flow Graph
# Title: dbpsk_Tx_path_UAV
# Author: UAV Group 4/21/2009
# Description: gnuradio flow graph
<<<<<<< .mine
# Generated: Thu May 21 15:59:44 2009
=======
# Generated: Tue May 19 16:42:39 2009
>>>>>>> .r77
##################################################

from gnuradio import blks2
from gnuradio import gr
from gnuradio.eng_option import eng_option
from grc_gnuradio import blks2 as grc_blks2
from grc_gnuradio import usrp as grc_usrp
from optparse import OptionParser

class dbpsk_Tx_path_UAV(gr.top_block):

	def __init__(self, options):
		gr.top_block.__init__(self, "dbpsk_Tx_path_UAV")

		##################################################
<<<<<<< .mine
=======
		# Variables
		##################################################
		self.variable_chooser_0 = variable_chooser_0 = [8000, 0][0]
		self.samp_rate = samp_rate = 32000
		self.freq_offset = freq_offset = -3100

		##################################################
>>>>>>> .r77
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
<<<<<<< .mine
		self.blks2_packet_encoder_0 = grc_blks2.packet_mod_b(grc_blks2.packet_encoder(
				samples_per_symbol=8,
				bits_per_symbol=1,
				access_code="",
				pad_for_usrp=False,
			),
			payload_length=64,
=======
		self.blks2_packet_encoder_0 = grc_blks2.packet_mod_b(grc_blks2.packet_encoder(
				samples_per_symbol=8,
				bits_per_symbol=1,
				access_code="",
				pad_for_usrp=False,
			),
			payload_length=1024,
>>>>>>> .r77
		)
<<<<<<< .mine
		self.gr_file_source_0 = gr.file_source(gr.sizeof_char*1, "/home/michael/softwaredefinedradio/src/uav_components/controller/padded_dbpsk_Tx_path_UAV.py", False)
		self.gr_multiply_const_vxx_0 = gr.multiply_const_vcc((8000, ))
		self.gr_throttle_0 = gr.throttle(gr.sizeof_gr_complex*1, 256e3)
		self.usrp_simple_sink_x_0 = grc_usrp.simple_sink_c(which=0, side="B")
=======
		self.gr_file_source_0 = gr.file_source(gr.sizeof_char*1, "/home/sab/softwaredefinedradio/src/Tx_Path/Command", True)
		self.gr_multiply_const_vxx_0 = gr.multiply_const_vcc((variable_chooser_0, ))
		self.gr_throttle_0 = gr.throttle(gr.sizeof_gr_complex*1, (8*samp_rate))
		self.usrp_simple_sink_x_0 = grc_usrp.simple_sink_c(which=0, side='A')
>>>>>>> .r77
		self.usrp_simple_sink_x_0.set_interp_rate(500)
<<<<<<< .mine
		self.usrp_simple_sink_x_0.set_frequency(440000800, verbose=True)
		self.usrp_simple_sink_x_0.set_gain(0)
=======
		self.usrp_simple_sink_x_0.set_frequency(439997900, verbose=True)
		self.usrp_simple_sink_x_0.set_gain(-1)
>>>>>>> .r77
		self.usrp_simple_sink_x_0.set_enable(True)

		##################################################
		# Connections
		##################################################
		self.connect((self.blks2_dxpsk_mod_0, 0), (self.gr_throttle_0, 0))
		self.connect((self.blks2_packet_encoder_0, 0), (self.blks2_dxpsk_mod_0, 0))
		self.connect((self.gr_file_source_0, 0), (self.blks2_packet_encoder_0, 0))
		self.connect((self.gr_throttle_0, 0), (self.gr_multiply_const_vxx_0, 0))
		self.connect((self.gr_multiply_const_vxx_0, 0), (self.usrp_simple_sink_x_0, 0))

<<<<<<< .mine
=======
	def set_variable_chooser_0(self, variable_chooser_0):
		self.variable_chooser_0 = variable_chooser_0
		self.gr_multiply_const_vxx_0.set_k((self.variable_chooser_0, ))

	def set_samp_rate(self, samp_rate):
		self.samp_rate = samp_rate

	def set_freq_offset(self, freq_offset):
		self.freq_offset = freq_offset

>>>>>>> .r77
if __name__ == '__main__':
	parser = OptionParser(option_class=eng_option, usage="%prog: [options]")
	(options, args) = parser.parse_args()
	tb = dbpsk_Tx_path_UAV(options)
	tb.start()
	raw_input('Press Enter to quit: ')
	tb.stop()

