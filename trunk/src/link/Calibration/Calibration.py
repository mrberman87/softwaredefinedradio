#!/usr/bin/env python
##################################################
# Gnuradio Python Flow Graph
# Title: Calibration
# Author: Charles
# Description: gnuradio flow graph
# Generated: Tue May 19 16:40:03 2009
##################################################

from gnuradio import blks2
from gnuradio import gr
from grc_gnuradio import usrp as grc_usrp
from grc_gnuradio import wxgui as grc_wxgui
import numpy
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
		self.variable_chooser_0 = variable_chooser_0 = [8000, 0][0]
		self.variable_0 = variable_0 = 0
		self.samp_rate = samp_rate = 32000
		self.freq_offset = freq_offset = 0

		##################################################
		# Controls
		##################################################
		_variable_chooser_0_control = grc_wxgui.radio_buttons_horizontal_control(
			window=self.GetWin(),
			callback=self.set_variable_chooser_0,
			label='variable_chooser_0',
			index=0,
			choices=[8000, 0],
			labels=[],
		)
		self.Add(_variable_chooser_0_control)
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
		self.gr_multiply_const_vxx_1 = gr.multiply_const_vcc((variable_chooser_0, ))
		self.gr_throttle_0 = gr.throttle(gr.sizeof_gr_complex*1, 256e3)
		self.random_source_x_0 = gr.vector_source_b(numpy.random.randint(0, 1, 1000), True)
		self.usrp_simple_sink_x_1 = grc_usrp.simple_sink_c(which=0, side='A')
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
		self.connect((self.random_source_x_0, 0), (self.blks2_dxpsk_mod_0, 0))

	def set_variable_chooser_0(self, variable_chooser_0):
		self.variable_chooser_0 = variable_chooser_0
		self.gr_multiply_const_vxx_1.set_k((self.variable_chooser_0, ))

	def set_variable_0(self, variable_0):
		self.variable_0 = variable_0

	def set_samp_rate(self, samp_rate):
		self.samp_rate = samp_rate

	def set_freq_offset(self, freq_offset):
		self.freq_offset = freq_offset
		self.usrp_simple_sink_x_1.set_frequency((440e6+self.freq_offset))

if __name__ == '__main__':
	tb = Calibration()
	tb.Run()

