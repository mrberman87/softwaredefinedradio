#!/usr/bin/env python

from txrx_controller import txrx_controller
import time

tb = txrx_controller(fc=440e6, centoff=0, foffset_tx=100e3, foffset_rx=-50e3, version='qpsk')
time.sleep(2)

while raw_input('T to continue: ') == 'T':
	temp = tb.transmit(raw_input('Message: '))
	#temp = tb.receive()
	print temp
