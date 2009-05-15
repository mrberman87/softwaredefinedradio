#!/usr/bin/env python
##################################################
# Gnuradio Python Flow Graph
# Title: Calibration
# Author: Charles
# Description: gnuradio flow graph
# Generated: Fri May 15 11:53:00 2009
##################################################

from gnuradio import gr
from grc_gnuradio import usrp as grc_usrp
from grc_gnuradio import wxgui as grc_wxgui
import wx

class Calibration(grc_wxgui.top_block_gui):

	def __init__(self):
		grc_wxgui.top_block_gui.__init__(
			self,
			title="GRC - Executing: Calibration",
		)

		##################################################
		# Variables
		##################################################
		self.samp_rate = samp_rate = 32000
		self.freq_offset = freq_offset = 0

		##################################################
		# Controls
		##################################################
		_freq_offset_control = grc_wxgui.slider_horizontal_control(
			window=self.GetWin(),
			callback=self.set_freq_offset,
			label='freq_offset',
			value=freq_offset,
			min=-10000,
			max=0,
			num_steps=200,
			slider_length=200,
		)
		self.Add(_freq_offset_control)

		##################################################
		# Blocks
		##################################################
		self.gr_multiply_const_vxx_0 = gr.multiply_const_vcc((8000, ))
		self.gr_sig_source_x_0 = gr.sig_source_c(samp_rate, gr.GR_COS_WAVE, 1e3, 1, 0)
		self.gr_throttle_0 = gr.throttle(gr.sizeof_gr_complex*1, (8*samp_rate))
		self.usrp_simple_sink_x_0 = grc_usrp.simple_sink_c(which=0, side='A')
		self.usrp_simple_sink_x_0.set_interp_rate(500)
		self.usrp_simple_sink_x_0.set_frequency((440e6+freq_offset), verbose=True)
		self.usrp_simple_sink_x_0.set_gain(0)
		self.usrp_simple_sink_x_0.set_enable(True)

		##################################################
		# Connections
		##################################################
		self.connect((self.gr_sig_source_x_0, 0), (self.gr_throttle_0, 0))
		self.connect((self.gr_multiply_const_vxx_0, 0), (self.usrp_simple_sink_x_0, 0))
		self.connect((self.gr_throttle_0, 0), (self.gr_multiply_const_vxx_0, 0))

	def set_samp_rate(self, samp_rate):
		self.samp_rate = samp_rate
		self.gr_sig_source_x_0.set_sampling_freq(self.samp_rate)

	def set_freq_offset(self, freq_offset):
		self.freq_offset = freq_offset
		self.usrp_simple_sink_x_0.set_frequency((440e6+self.freq_offset))

if __name__ == '__main__':
	tb = Calibration()
	tb.Run()

