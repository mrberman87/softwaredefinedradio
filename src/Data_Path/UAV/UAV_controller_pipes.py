#!/usr/bin/env python

#GPS Disabled : Lines 72 and 131
#Telemetry Disabled : Line 122
#Re-enable both Telemetry and GPS for actual UAV

from txrx_controller import txrx_controller
import time
import os
import signal
import sys
import subprocess
from GPS_getter import *

fromUAV,toServer = os.pipe()
fromServer,toUAV = os.pipe()

def forkit(fft=False, fft_fn='/fft.png'):
	pid = os.fork()
	run(pid, fft_fn, fft)

def init_files():
	if(not os.path.exists('image.jpg')):
		subprocess.Popen('touch image.jpg', shell=True)
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

def run(pid,fft_fn, fft=False):
	if pid == 0:
		tb = txrx_controller(fc=440e6, centoff=0, foffset_tx=100e3, foffset_rx=-50e3)
		time.sleep(1.5)
		if fft == True:
			print 'Transceiver: Transmitting FFT from previous command.'
			tb.transmit(fft_fn)
		while True:
			s = os.read(fromUAV,1024)
			s = s.split(':')
			print str(s)
			if s[0] == 'rx':
				print 'Transceiver: Waiting on receive'
				os.write(toUAV, str(tb.receive()))
			elif s[0] == 'close':
				print 'Transceiver: Closing queues for shutdown.'
				tb.close_queues()
			elif s[0] == 'set_frequency':
				time.sleep(1)
				print 'Transceiver: Changing Frequency.'
				tb.set_frequency(s[1])
			elif s[0] == 'set_timeout':
				print 'Transceiver: Changing timeout.'
				tb.set_frame_time_out(s[1])
			elif s[0] == ':':
				pass
			else:
				print 'Transceiver: Transmitting.'
				os.write(toUAV, str(tb.transmit(s[0])))
				print 'Transceiver: Done Transmitting.'
		
	else:
		class UAV():
			def __init__(self):
				self.cwd = os.getcwd()
				self.rtn_list = ['False', 'Timeout',  'Handshaking Maximum Reached', 'Error']
				#self.GPS = GPS_getter()
				self.default_freq = '440e6'
				self.default_timeout = '45'
				self.freq = self.default_freq
				self.timeout = self.default_timeout
				self.timeout_counter = 0
				self.image_filename = '/image.jpg'
				self.telemetry_filename = '/misc.dat'
				self.fft_filename = '/fft.png'
				self.rx_filename = '/rx_data'
				self.run()

			def run(self):
				time.sleep(1.5)
				while True:
					temp = self.proc_com('rx:')
					if temp == 'True':
						self.timeout_counter = 0
						try:
							cmd = self.get_command()
						except:
							print 'UAV: Failed to open file'
							cmd = 'UAV: Failed to retreive command from file.:'
						if cmd == 'Image':
							print 'UAV: Taking Image.'
							pic = subprocess.Popen('uvccapture -q25 -o%s' % (self.cwd + self.image_filename), shell=True)
							time.sleep(1)
							pic.wait()
							print 'UAV: Image Done.'
							temp = self.proc_com(self.image_filename + ':')
							print 'UAV: Result of pipe is : %s' % temp
						elif cmd == 'Close':
							os.write(toServer, 'close:')
							time.sleep(1)
							os.kill(pid, signal.SIGTERM)
							sys.exit(0)
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
							print 'UAV: Telemetry command received.'
							#self.retrieve_telemetry()
							fd = open(self.cwd + self.telemetry_filename, 'w')
							fd.write('87\n12.5')
							fd.close()
							temp = self.proc_com(self.telemetry_filename + ':')
							print 'UAV: Result of pipe is : %s' % temp
							self.clear_file(self.telemetry_filename)			
						elif cmd == 'GPS':
							print 'UAV: Getting GPS.'
							#self.GPS.get_gps('w', cwd + telemetry_filename)
							fd = open(self.cwd + self.telemetry_filename, 'w')
							fd.write('GPSD,P=34.241188 -118.529098,A=?,V=0.110,E=? ? ?')
							fd.close()
							temp = self.proc_com(self.telemetry_filename + ':')
							print 'UAV: Result of pipe is : %s' % temp
							self.clear_file(self.telemetry_filename)			
						elif cmd == 'Settings':
							tmp_freq = None
							tmp_timeout = None
							fd = open(self.cwd + self.rx_filename, 'r')
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
										time.sleep(1)
							fd.close()
							self.clear_file(self.rx_filename)
						else:
							if cmd.count(':') > 0:
								temp = self.proc_com(cmd)
							else:
								temp = self.proc_com(cmd + ':')
					elif temp in rtn_list:
						self.timeout_counter += 1
						print 'UAV: Return from Transceiver Process not True... ', temp
						print 'Incrimenting Go Home Counter : %d' % self.timeout_counter
					else:
						os.write(toServer, 'close:')
						time.sleep(1)
						os.kill(pid, signal.SIGTERM)
						sys.exit(0)

					if self.timeout_counter == 2:
						self.go_home()
						os.write(toServer, 'set_frequency:' + self.default_freq)
						time.sleep(1)
						os.write(toServer, 'set_timeout:' + self.default_timeout)
						time.sleep(1)

			def retrieve_telemetry(self):
				temprature = subprocess.Popen('python temp.py', shell=True)
				time.sleep(1)
				temprature.wait()
				batt = subprocess.Popen('python batt.py', shell=True)
				time.sleep(1)
				batt.wait()

			def get_command(self):
				fd = open(self.cwd + self.rx_filename, 'r')
				tmp = fd.readline().strip('\n').strip()
				fd.close()
				return tmp

			def clear_file(self, path):
				fd = open(self.cwd + path, 'w')
				fd.write('')
				fd.close()

			def proc_com(self, data):
				os.write(toServer, data)
				return os.read(fromServer,1024)

			def go_home(self):
				self.freq = self.default_frequency
				self.timeout = self.dafault_timeout
		u = UAV()
				
if __name__ == '__main__':
	init_files()
	forkit()
