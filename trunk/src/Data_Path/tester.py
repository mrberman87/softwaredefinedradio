#!/usr/bin/env python

from txrx_controller import txrx_controller
import time

tb = txrx_controller(fc=440e6, centoff=11e3, foffset_tx=0, foffset_rx=50e3, frame_time_out = 45)
time.sleep(2)
#temp = tb.transmit('Image')
temp = tb.receive()
print temp
