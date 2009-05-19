#!/usr/bin/env python
##################################################
# Gnuradio Python Flow Graph
# Title: Tx_Kill
# Author: Charles Judah
# Description: gnuradio flow graph
# Generated: Tue May 19 10:56:37 2009
##################################################

from gnuradio import gr
from grc_gnuradio import usrp as grc_usrp

class Tx_Kill(gr.top_block):

	def __init__(self):
		gr.top_block.__init__(self, "Tx_Kill")

		##################################################
		# Blocks
		##################################################
		self.const_source_x_0 = gr.sig_source_c(0, gr.GR_CONST_WAVE, 0, 0, 1)
		self.gr_multiply_const_vxx_0 = gr.multiply_const_vcc((0, ))
		self.gr_throttle_0 = gr.throttle(gr.sizeof_gr_complex*1, 256e3)
		self.usrp_simple_sink_x_0 = grc_usrp.simple_sink_c(which=0, side='A')
		self.usrp_simple_sink_x_0.set_interp_rate(500)
		self.usrp_simple_sink_x_0.set_frequency((440009220), verbose=True)
		self.usrp_simple_sink_x_0.set_gain(0)
		self.usrp_simple_sink_x_0.set_enable(True)

		##################################################
		# Connections
		##################################################
		self.connect((self.gr_multiply_const_vxx_0, 0), (self.usrp_simple_sink_x_0, 0))
		self.connect((self.gr_throttle_0, 0), (self.gr_multiply_const_vxx_0, 0))
		self.connect((self.const_source_x_0, 0), (self.gr_throttle_0, 0))

if __name__ == '__main__':
	tb = Tx_Kill()
	tb.start()
	raw_input('Press Enter to quit: ')
	tb.stop()

