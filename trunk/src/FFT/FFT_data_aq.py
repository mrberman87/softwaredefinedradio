#!/usr/bin/env python
##################################################
# Gnuradio Python Flow Graph
# Title: FFT_data_aq
# Author: UAV Group
# Description: gnuradio flow graph
# Generated: Thu Sep 17 00:26:46 2009
##################################################

from gnuradio import gr
from gnuradio.eng_option import eng_option
from gnuradio.wxgui import fftsink2
from grc_gnuradio import usrp as grc_usrp
from grc_gnuradio import wxgui as grc_wxgui
from optparse import OptionParser
import wx

class FFT_data_aq(grc_wxgui.top_block_gui):

	def __init__(self):
		grc_wxgui.top_block_gui.__init__(self, title="FFT_data_aq")

		##################################################
		# Variables
		##################################################
		self.samp_rate = samp_rate = 32000
		self.freq_offset = freq_offset = 0

		##################################################
		# Blocks
		##################################################
		self.gr_throttle_0 = gr.throttle(gr.sizeof_gr_complex*1, (3*samp_rate))
		self.usrp_simple_source_x_0 = grc_usrp.simple_source_c(which=0, side="A", rx_ant="TX/RX")
		self.usrp_simple_source_x_0.set_decim_rate(250)
		self.usrp_simple_source_x_0.set_frequency((440e6 + freq_offset), verbose=True)
		self.usrp_simple_source_x_0.set_gain(-1)
		self.wxgui_fftsink2_0 = fftsink2.fft_sink_c(
			self.GetWin(),
			baseband_freq=0,
			y_per_div=10,
			y_divs=10,
			ref_level=50,
			sample_rate=96000,
			fft_size=1024,
			fft_rate=30,
			average=False,
			avg_alpha=None,
			title="FFT Plot",
			peak_hold=False,
		)
		self.Add(self.wxgui_fftsink2_0.win)

		##################################################
		# Connections
		##################################################
		self.connect((self.usrp_simple_source_x_0, 0), (self.gr_throttle_0, 0))
		self.connect((self.gr_throttle_0, 0), (self.wxgui_fftsink2_0, 0))

	def set_samp_rate(self, samp_rate):
		self.samp_rate = samp_rate

	def set_freq_offset(self, freq_offset):
		self.freq_offset = freq_offset
		self.usrp_simple_source_x_0.set_frequency((440e6 + self.freq_offset))

if __name__ == '__main__':
	parser = OptionParser(option_class=eng_option, usage="%prog: [options]")
	(options, args) = parser.parse_args()
	tb = FFT_data_aq()
	tb.Run(True)

