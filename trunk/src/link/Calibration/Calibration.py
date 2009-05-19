#!/usr/bin/env python
##################################################
# Gnuradio Python Flow Graph
# Title: Calibration
# Author: Charles
# Description: gnuradio flow graph
# Generated: Mon May 18 12:18:40 2009
##################################################

from gnuradio import blks2
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
			max=10000,
			num_steps=200,
			slider_length=200,
		)
		self.Add(_freq_offset_control)

		##################################################
		# Blocks
		##################################################
		self.blks2_dxpsk_mod_0 = blks2.dqpsk_mod(
			samples_per_symbol=8,
			excess_bw=0.35,
			gray_code=False,
		)
		self.gr_multiply_const_vxx_1 = gr.multiply_const_vcc((7000, ))
		self.gr_throttle_0 = gr.throttle(gr.sizeof_gr_complex*1, 256e3)
		self.gr_vector_source_x_0 = gr.vector_source_b((0, 0, 0, 1, 1, 0, 1, 1), True)
		self.usrp_simple_sink_x_1 = grc_usrp.simple_sink_c(which=0, side='B')
		self.usrp_simple_sink_x_1.set_interp_rate(500)
		self.usrp_simple_sink_x_1.set_frequency((440e6+freq_offset), verbose=True)
		self.usrp_simple_sink_x_1.set_gain(0)
		self.usrp_simple_sink_x_1.set_enable(True)

		##################################################
		# Connections
		##################################################
		self.connect((self.gr_throttle_0, 0), (self.gr_multiply_const_vxx_1, 0))
		self.connect((self.gr_multiply_const_vxx_1, 0), (self.usrp_simple_sink_x_1, 0))
		self.connect((self.blks2_dxpsk_mod_0, 0), (self.gr_throttle_0, 0))
		self.connect((self.gr_vector_source_x_0, 0), (self.blks2_dxpsk_mod_0, 0))

	def set_samp_rate(self, samp_rate):
		self.samp_rate = samp_rate

	def set_freq_offset(self, freq_offset):
		self.freq_offset = freq_offset
		self.usrp_simple_sink_x_1.set_frequency((440e6+self.freq_offset))

if __name__ == '__main__':
	tb = Calibration()
	tb.Run()

