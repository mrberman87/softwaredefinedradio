#!/usr/bin/env python
##################################################
# Gnuradio Python Flow Graph
# Title: FFT_data_aq
# Author: UAV Group
# Description: gnuradio flow graph
# Generated: Wed Sep 30 19:22:42 2009
##################################################

from gnuradio import gr
from gnuradio.eng_option import eng_option
from grc_gnuradio import usrp as grc_usrp
from grc_gnuradio import blks2 as grc_blks2
from optparse import OptionParser
import time, sys

class FFT_data_aq(gr.top_block):

        def __init__(self):
                gr.top_block.__init__(self, "FFT_data_aq")
                self.real_path = sys.argv[1]
		self.imag_path = sys.argv[2]
		self.freq = sys.argv[3]

                ##################################################
                # Blocks
                ##################################################
		self.complex_to_float = gr.complex_to_float(1)
		self.valve = grc_blks2.valve(item_size=gr.sizeof_gr_complex*1, open=bool(True))
                self.real_sink = gr.file_sink(gr.sizeof_float*1, self.real_path)
                self.imag_sink = gr.file_sink(gr.sizeof_float*1, self.imag_path)
                self.usrp_source = grc_usrp.simple_source_c(which=0, side="A", rx_ant="TX/RX")
                self.usrp_source.set_decim_rate(250)
                self.usrp_source.set_frequency(440e6, verbose=True)
                self.usrp_source.set_gain(40)

                ##################################################
                # Connections
                ##################################################
                self.connect((self.usrp_source, 0), (self.valve, 0))
                self.connect((self.valve, 0), (self.complex_to_float, 0))
                self.connect((self.complex_to_float, 0), (self.real_sink, 0))
                self.connect((self.complex_to_float, 1), (self.imag_sink, 0))

	def take_data(self):
		self.valve.set_open(bool(False))
		time.sleep(1)
		self.valve.set_open(bool(True))

if __name__ == '__main__':
        parser = OptionParser(option_class=eng_option, usage="%prog: [options]")
        (options, args) = parser.parse_args()
        tb = FFT_data_aq()
        tb.start()
	tb.take_data()
        tb.stop()

