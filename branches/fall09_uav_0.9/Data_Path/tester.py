#!/usr/bin/env python

from txrx_controller import txrx_controller
import time

tb = txrx_controller(fc=440e6, centoff=11e3, foffset_tx=0, foffset_rx=50e3, version='bpsk')
time.sleep(2)

while raw_input('T to continue: ') == 'T':
	temp = tb.transmit(raw_input('Message: '))
	#temp = tb.receive()
	print temp
	#fd = open('/home/gnuradio/Desktop/rx_data', 'r')
	#print "File Contents: \n", fd.read()
	#fd.close()
