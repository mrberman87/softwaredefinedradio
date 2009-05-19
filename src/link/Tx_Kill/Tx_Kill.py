#!/usr/bin/env python
##################################################
# Gnuradio Python Flow Graph
# Title: Tx_Kill
# Author: Charles Judah
# Description: gnuradio flow graph
# Generated: Tue May 19 15:00:04 2009
##################################################

from gnuradio import gr
from grc_gnuradio import usrp as grc_usrp
from grc_gnuradio import wxgui as grc_wxgui
import wx

class Tx_Kill(grc_wxgui.top_block_gui):

	def __init__(self):
		grc_wxgui.top_block_gui.__init__(
			self,
			title="GRC - Executing: Tx_Kill",
		)

		##################################################
		# Variables
		##################################################
		self.variable_chooser_0 = variable_chooser_0 = [1, 0][0]

		##################################################
		# Controls
		##################################################
		_variable_chooser_0_control = grc_wxgui.radio_buttons_horizontal_control(
			window=self.GetWin(),
			callback=self.set_variable_chooser_0,
			label="Tx_Stop",
			index=0,
			choices=[1, 0],
			labels=[],
		)
		self.Add(_variable_chooser_0_control)

		##################################################
		# Blocks
		##################################################
		self.const_source_x_0 = gr.sig_source_c(0, gr.GR_CONST_WAVE, 0, 0, 1)
		self.gr_multiply_const_vxx_0 = gr.multiply_const_vcc((variable_chooser_0, ))
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

	def set_variable_chooser_0(self, variable_chooser_0):
		self.variable_chooser_0 = variable_chooser_0
		self.gr_multiply_const_vxx_0.set_k((self.variable_chooser_0, ))

if __name__ == '__main__':
	tb = Tx_Kill()
	tb.Run()

