#!/usr/bin/env python

from txrx_controller import txrx_controller
import time
import os, signal, sys

fromClient,toServer = os.pipe()
fromServer,toClient = os.pipe()

pid = os.fork()

if pid == 0:
	tb = txrx_controller(fc=440e6, centoff=11.19e3, foffset_tx=0, foffset_rx=50e3, version='bpsk')
	time.sleep(1)
	while True:
		s = os.read(fromClient,1024)
		if s == 'rx':
			os.write(toClient, str(tb.receive()))
		elif s == 'close':
			tb.close_queues()
		else:
			os.write(toClient, str(tb.transmit(s)))
		
else:
	time.sleep(3)
	temp = 'True'
	while temp == 'True':
		os.write(toServer, raw_input('Enter Command : '))
		temp = os.read(fromServer,1024)
		if temp == 'True':
			os.write(toServer, 'rx')
			temp = os.read(fromServer,1024)
		if raw_input('Kill? : ') == 'y':
			os.write(toServer, 'close')
			time.sleep(1)
			os.kill(pid, signal.SIGTERM)
			sys.exit(0)
