#!/usr/bin/env python
##################################################
# Gnuradio Python Flow Graph
# Title: Tx_Kill
# Author: Charles Judah
# Description: gnuradio flow graph
<<<<<<< .mine
# Generated: Thu May 21 16:23:42 2009
=======
# Generated: Tue May 19 15:00:04 2009
>>>>>>> .r77
##################################################

from gnuradio import gr
from gnuradio.eng_option import eng_option
from grc_gnuradio import usrp as grc_usrp
<<<<<<< .mine
from optparse import OptionParser
=======
from grc_gnuradio import wxgui as grc_wxgui
import wx
>>>>>>> .r77

class Tx_Kill(grc_wxgui.top_block_gui):

	def __init__(self, options):
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
<<<<<<< .mine
		self.const_source_x_0 = gr.sig_source_c(0, gr.GR_CONST_WAVE, 0, 0, 0)
		self.usrp_simple_sink_x_0 = grc_usrp.simple_sink_c(which=0, side="B")
=======
		self.const_source_x_0 = gr.sig_source_c(0, gr.GR_CONST_WAVE, 0, 0, 1)
		self.gr_multiply_const_vxx_0 = gr.multiply_const_vcc((variable_chooser_0, ))
		self.gr_throttle_0 = gr.throttle(gr.sizeof_gr_complex*1, 256e3)
		self.usrp_simple_sink_x_0 = grc_usrp.simple_sink_c(which=0, side='A')
>>>>>>> .r77
		self.usrp_simple_sink_x_0.set_interp_rate(500)
		self.usrp_simple_sink_x_0.set_frequency((440009220), verbose=True)
		self.usrp_simple_sink_x_0.set_gain(0)
		self.usrp_simple_sink_x_0.set_enable(True)

		##################################################
		# Connections
		##################################################
		self.connect((self.const_source_x_0, 0), (self.usrp_simple_sink_x_0, 0))

	def set_variable_chooser_0(self, variable_chooser_0):
		self.variable_chooser_0 = variable_chooser_0
		self.gr_multiply_const_vxx_0.set_k((self.variable_chooser_0, ))

if __name__ == '__main__':
	parser = OptionParser(option_class=eng_option, usage="%prog: [options]")
	(options, args) = parser.parse_args()
	tb = Tx_Kill(options)
	tb.Run()

