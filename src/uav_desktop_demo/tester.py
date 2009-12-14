#!/usr/bin/env python

from txrx_controller import txrx_controller
import time
import os, signal, sys, subprocess

fromClient,toServer = os.pipe()
fromServer,toClient = os.pipe()


def forkit(fft=False):
	pid = os.fork()
	run(pid,fft)


def run(pid,fft=False):
	if pid == 0:
		tb = txrx_controller(fc=440e6, centoff=0, foffset_tx=100e3, foffset_rx=-50e3)
		time.sleep(3)
		if fft == True:
			print 'Server: Transmitting FFT from previous command.'
			tb.transmit('/fft.png')
		while True:
			s = os.read(fromClient,1024)
			if s == 'rx':
				print 'Server: Waiting on receive'
				os.write(toClient, str(tb.receive()))
			elif s == 'close':
				print 'Server: Closing queues for shutdown.'
				tb.close_queues()
			else:
				print 'Server: Transmitting.'
				os.write(toClient, str(tb.transmit(s)))
				print 'Server: Done Transmitting.'
		
	else:
		time.sleep(3)
		temp = 'True'
		while temp == 'True':
			os.write(toServer, 'rx')
			temp = os.read(fromServer,1024)
			if temp == 'True':
				fd = open(os.getcwd() + '/rx_data', 'r')
				cmd = fd.read()
				fd.close()
				if cmd == 'Image':
					print 'Client: Taking Image.'
					pic = subprocess.Popen('uvccapture -q25 -o%s' % (os.getcwd() + '/p.jpg'), shell=True)
					time.sleep(1)
					pic.wait()
					print 'Client: Image Done.'
					os.write(toServer, '/p.jpg')
					print 'Client: Reading from pipe.'
					temp = os.read(fromServer,1024)
					print 'Client: Result of pipe is : %s' % temp
				elif cmd == 'FFT':
					print 'Client: FFT command received.'
					time.sleep(1)
					print 'Client: Closing queues.'
					os.write(toServer, 'close')
					time.sleep(1)
					print 'Client: Stopping original child process.'
					os.kill(pid, signal.SIGTERM)
					time.sleep(1)
					p = subprocess.Popen('python get_fft.py', shell=True)
					p.wait()
					print 'Client: Forking after FFT.'
					forkit(True)
				else:
					os.write(toServer, cmd)
					temp = os.read(fromServer,1024)
			else:
				os.write(toServer, 'close')
				time.sleep(1)
				os.kill(pid, signal.SIGTERM)
				sys.exit(0)
			'''if temp == 'True':
				os.write(toServer, 'rx')
				temp = os.read(fromServer,1024)'''
			#if raw_input('Kill? : ') == 'y':
			#	os.write(toServer, 'close')
			#	time.sleep(1)
			#	os.kill(pid, signal.SIGTERM)
			#	sys.exit(0)

if __name__ == '__main__':
	forkit()
