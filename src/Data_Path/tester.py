#!/usr/bin/env python

from txrx_controller import txrx_controller
import time

tb = txrx_controller(fc=440e6, centoff=0, foffset_tx=0, foffset_rx=0)
time.sleep(2)
#temp = tb.transmit('/data.txt')
temp = tb.receive()
print temp
