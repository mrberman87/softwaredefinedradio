#!/usr/bin/env python

from txrx_controller import txrx_controller
import time
import os
import signal
import sys
import subprocess
from GPS_getter import *

fromUAV,toServer = os.pipe()
fromServer,toUAV = os.pipe()

rtn_list = ['False', 'Timeout',  'Handshaking Maximum Reached', 'Error']
GPS = GPS_getter()
rx_filename = '/rx_data'
image_filename = '/p.jpg:'
telemetry_filename = '/misc.dat:'
fft_filename = '/fft.png:'
cwd = os.getcwd()
timeout_counter = 0

def forkit(fft=False):
	pid = os.fork()
	run(pid,fft)

def retrieve_telemetry():
	temprature = subprocess.Popen('python temp.py', shell=True)
	time.sleep(1)
	temprature.wait()
	batt = subprocess.Popen('python batt.py', shell=True)
	time.sleep(1)
	batt.wait()

def get_command():
	fd = open(cwd + rx_filename, 'r')
	tmp = fd.readline().strip('\n').strip()
	fd.close()
	return tmp

def clear_file(path):
	fd = open(cwd + path, 'w')
	fd.write('')
	fd.close()

def go_home():
	freq = '440e6'
	timeout = '45'
	default_freq = '440e6'
	default_timeout = '45'

def init_files():
	if(not os.path.exists('p.jpg')):
		subprocess.Popen('touch p.jpg', shell=True)
	if(not os.path.exists('fft.png')):
		subprocess.Popen('touch fft.png', shell=True)
	if(not os.path.exists('misc.dat')):
		subprocess.Popen('touch misc.dat', shell=True)
	if(not os.path.exists('imaginary')):
		subprocess.Popen('touch imaginary', shell=True)
	if(not os.path.exists('real')):
		subprocess.Popen('touch real', shell=True)
	if(not os.path.exists('rx_data')):
		subprocess.Popen('touch rx_data', shell=True)

def proc_com(data):
	os.write(toServer, data)
	return os.read(fromServer,1024)

def run(pid,fft=False):
	if pid == 0:
		tb = txrx_controller(fc=freq, centoff=0, foffset_tx=100e3, foffset_rx=-50e3)
		time.sleep(1.5)
		if fft == True:
			print 'Transceiver: Transmitting FFT from previous command.'
			tb.transmit(fft_filename)
		while True:
			s = os.read(fromUAV,1024).split(':')
			if s[0] == 'rx':
				print 'Transceiver: Waiting on receive'
				os.write(toUAV, str(tb.receive()))
			elif s[0] == 'close':
				print 'Transceiver: Closing queues for shutdown.'
				tb.close_queues()
			elif s[0] == 'set_frequency':
				tb.set_frequency(s[1])
			elif s[0] == 'set_timeout':
				tb.set_frame_time_out(s[1])
			else:
				print 'Transceiver: Transmitting.'
				os.write(toUAV, str(tb.transmit(s[0])))
				print 'Transceiver: Done Transmitting.'
		
	else:
		time.sleep(1.5)
		while True:
			temp = proc_com('rx:')
			if temp == 'True':
				timeout_counter = 0
				try:
					cmd = get_command()
				except:
					print 'UAV: Failed to open file'
					cmd = 'UAV: Failed to retreive command from file.:'
				if cmd == 'Image':
					print 'UAV: Taking Image.'
					pic = subprocess.Popen('uvccapture -q25 -o%s' % (cwd + image_filename), shell=True)
					time.sleep(1)
					pic.wait()
					print 'UAV: Image Done.'
					temp = proc_com(image_filename)
					print 'UAV: Result of pipe is : %s' % temp
				elif cmd == 'FFT':
					print 'UAV: FFT command received.'
					os.write(toServer, 'close:')
					time.sleep(1)
					print 'UAV: Stopping Transceiver process.'
					os.kill(pid, signal.SIGTERM)
					time.sleep(1)
					p = subprocess.Popen('python get_fft.py', shell=True)
					time.sleep(1)
					p.wait()
					print 'UAV: Restoring Transceiver to transmit FFT.'
					forkit(True)
				elif cmd == 'Telemetry':
					retrieve_telemetry()
					temp = proc_com(telemetry_filename)
					print 'UAV: Result of pipe is : %s' % temp
					clear_file(telemetry_filename.strip(':'))			
				elif cmd == 'GPS':
					print 'UAV: Getting GPS.'
					GPS.get_gps('w', cwd + telemetry_filename)
					temp = proc_com(telemetry_filename)
					print 'UAV: Result of pipe is : %s' % temp
					clear_file(telemetry_filename.strip(':'))			
				elif cmd == 'Settings':
					tmp_freq = None
					tmp_timeout = None
					fd = open(cwd + rx_filename, 'r')
					for l in fd:
						if l.startswith("Freq:"):
							junk, tmp_freq = l.split()
							if tmp_freq != None:
								freq = tmp_freq
								os.write(toServer, 'set_frequency:' + freq)
						time.sleep(1)
						if l.startswith("Timeout:"):
							junk, tmp_timeout = l.split()
							if tmp_timeout != None:
								timeout = tmp_timeout
								os.write(toServer, 'set_timeout:' + timeout)
					fd.close()
					clear_file(rx_filename.strip(':'))
				else:
					if cmd.count(':') > 0:
						temp = proc_com(cmd)
					else:
						temp = proc_com(cmd + ':')
			elif temp in rtn_list:
				timeout_counter += 1
				print 'UAV: Return from Transceiver Process not True... ', temp
				print 'Incrimenting Go Home Counter.'
			else:
				os.write(toServer, 'close:')
				time.sleep(1)
				os.kill(pid, signal.SIGTERM)
				sys.exit(0)

			if timeout_counter == 3:
				go_home()
				os.write(toServer, 'set_frequency:' + default_freq)
				time.sleep(1.5)
				os.write(toServer, 'set_timeout:' + default_timeout)
				
if __name__ == '__main__':
	init_files()
	go_home()
	forkit()
