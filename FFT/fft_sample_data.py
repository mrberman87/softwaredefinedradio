#!/usr/bin/env python
##################################################
# Gnuradio Python Flow Graph
# Title: Top Block
# Generated: Sun Nov 15 22:55:24 2009
##################################################

from gnuradio import blks2
from gnuradio import gr
from gnuradio.eng_option import eng_option
from grc_gnuradio import blks2 as grc_blks2
from optparse import OptionParser
import numpy
import time
import sys

class top_block(gr.top_block):

	def __init__(self):
		gr.top_block.__init__(self, "Top Block")
		self.real_path = sys.argv[1]
		self.imag_path = sys.argv[2]
		self.fc        = sys.argv[3]
		print self.fc
		##################################################
		# Blocks
		##################################################
		self.blks2_dxpsk_mod_0 = blks2.dbpsk_mod(
			samples_per_symbol=8,
			excess_bw=0.35,
			gray_code=True,
			verbose=False,
			log=False,
		)
		self.blks2_valve_0 = grc_blks2.valve(item_size=gr.sizeof_gr_complex*1, open=bool(True))
		self.gr_complex_to_float_0 = gr.complex_to_float(1)
		self.gr_file_sink_0 = gr.file_sink(gr.sizeof_float*1, self.real_path)
		self.gr_file_sink_0_0 = gr.file_sink(gr.sizeof_float*1, self.imag_path)
		self.gr_throttle_0_0 = gr.throttle(gr.sizeof_gr_complex*1, 256e3)
		self.random_source_x_0 = gr.vector_source_b(map(int, numpy.random.randint(0, 2, 1024)), True)

		##################################################
		# Connections
		##################################################
		self.connect((self.blks2_valve_0, 0), (self.gr_throttle_0_0, 0))
		self.connect((self.gr_throttle_0_0, 0), (self.gr_complex_to_float_0, 0))
		self.connect((self.random_source_x_0, 0), (self.blks2_dxpsk_mod_0, 0))
		self.connect((self.blks2_dxpsk_mod_0, 0), (self.blks2_valve_0, 0))
		self.connect((self.gr_complex_to_float_0, 1), (self.gr_file_sink_0_0, 0))
		self.connect((self.gr_complex_to_float_0, 0), (self.gr_file_sink_0, 0))

	def take_data(self):
		self.blks2_valve_0.set_open(bool(False))
		time.sleep(1)
		self.blks2_valve_0.set_open(bool(True))

if __name__ == '__main__':
	parser = OptionParser(option_class=eng_option, usage="%prog: [options]")
	(options, args) = parser.parse_args()
	tb = top_block()
	tb.start()
	tb.take_data()
	tb.stop()

