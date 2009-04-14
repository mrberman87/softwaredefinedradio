#!/usr/bin/env python
##################################################
# Gnuradio Python Flow Graph
# Title: untitled
# Author: unknown
# Description: gnuradio flow graph
# Generated: Wed Apr  1 21:21:57 2009
##################################################

from gnuradio import gr

class top_block(gr.top_block):

	def __init__(self):
		gr.top_block.__init__(self, "untitled")

		##################################################
		# Variables
		##################################################
		self.samp_rate = samp_rate = 32e3

		##################################################
		# Blocks
		##################################################
		self.gr_file_sink_0 = gr.file_sink(gr.sizeof_float*1, "/home/sab/Desktop/Crap.dat")
		self.gr_sig_source_x_0 = gr.sig_source_f(2*440e6, gr.GR_COS_WAVE, 440e6, 1, 0)
		self.gr_throttle_0 = gr.throttle(gr.sizeof_float*1, 2*440e6)

		##################################################
		# Connections
		##################################################
		self.connect((self.gr_throttle_0, 0), (self.gr_file_sink_0, 0))
		self.connect((self.gr_sig_source_x_0, 0), (self.gr_throttle_0, 0))

	def set_samp_rate(self, samp_rate):
		self.samp_rate = samp_rate

if __name__ == '__main__':
	tb = top_block()
	tb.start()
	raw_input('Press Enter to quit: ')
	tb.stop()

