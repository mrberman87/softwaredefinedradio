#!/usr/bin/env python
##################################################
# Gnuradio Python Flow Graph
# Title: Top Block
# Generated: Wed Oct  7 11:43:30 2009
##################################################

from gnuradio import blks2
from gnuradio import gr
from gnuradio.eng_option import eng_option
from grc_gnuradio import wxgui as grc_wxgui
from optparse import OptionParser
import wx

class top_block(grc_wxgui.top_block_gui):

	def __init__(self):
		grc_wxgui.top_block_gui.__init__(self, title="Top Block")

		##################################################
		# Blocks
		##################################################
		self.blks2_dxpsk_demod_0 = blks2.dqpsk_demod(
			samples_per_symbol=16,
			excess_bw=0.35,
			costas_alpha=0.175,
			gain_mu=0.175,
			mu=0.5,
			omega_relative_limit=0.005,
			gray_code=True,
			verbose=False,
			log=False,
		)
		self.blks2_dxpsk_demod_0_0 = blks2.d8psk_demod(
			samples_per_symbol=32,
			excess_bw=0.35,
			costas_alpha=0.175,
			gain_mu=0.175,
			mu=0.5,
			omega_relative_limit=0.005,
			gray_code=True,
			verbose=False,
			log=False,
		)
		self.blks2_dxpsk_mod_0 = blks2.dqpsk_mod(
			samples_per_symbol=16,
			excess_bw=0.35,
			gray_code=True,
			verbose=False,
			log=False,
		)
		self.blks2_dxpsk_mod_0_0 = blks2.d8psk_mod(
			samples_per_symbol=32,
			excess_bw=0.35,
			gray_code=True,
			verbose=False,
			log=False,
		)

		##################################################
		# Connections
		##################################################
		self.connect((self.blks2_dxpsk_demod_0, 0), (, 0))
		self.connect((, 0), (self.blks2_dxpsk_mod_0, 0))
		self.connect((self.blks2_dxpsk_mod_0, 0), (self.blks2_dxpsk_demod_0, 0))
		self.connect((self.blks2_dxpsk_demod_0_0, 0), (, 0))
		self.connect((, 0), (self.blks2_dxpsk_mod_0_0, 0))
		self.connect((self.blks2_dxpsk_mod_0_0, 0), (self.blks2_dxpsk_demod_0_0, 0))

if __name__ == '__main__':
	parser = OptionParser(option_class=eng_option, usage="%prog: [options]")
	(options, args) = parser.parse_args()
	tb = top_block()
	tb.Run(True)

