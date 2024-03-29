from GPS_getter import *
import os, time, sys, signal


class UAV():
	def __init__(self, controller, toTransceiver, fromTransceiver, GPS=False, Telemetry=False):
		self.init_files()
		self.cwd = os.getcwd()
		self.rtn_list = ['False', 'Timeout',  'Handshaking Maximum Reached', 'Error']
		self.GPS_condition = GPS
		if self.GPS_condition:
			self.GPS = GPS_getter()
		self.Telemetry_condition = Telemetry
		self.default_freq = '440000000'
		self.default_timeout = '45'
		self.freq = self.default_freq
		self.timeout = self.default_timeout
		self.timeout_counter = 0
		self.image_filename = '/image.jpg'
		self.telemetry_filename = '/misc.dat'
		self.fft_filename = '/fft.png'
		self.rx_filename = '/rx_data'
		self.toTransceiver = toTransceiver
		self.fromTransceiver = fromTransceiver
		self.controller = controller
		self.temp = ''
		self.run_UAV()

	def run_UAV(self):
		while True:
			self.temp = self.proc_com('rx:')
			if self.temp == 'True':
				self.timeout_counter = 0
				try:
					cmd = self.get_command()
				except:
					#print 'UAV: Failed to open file'
					cmd = ''
				if cmd == 'Image':
					#print 'UAV: Taking Image.'
					fnull = open(os.devnull, 'w')
					pic = subprocess.Popen('uvccapture -q100 -o%s' % (self.cwd + self.image_filename), stdout=fnull, stderr=fnull, shell=True)
					time.sleep(1)
					pic.wait()
					fnull.close()
					#print 'UAV: Image Done.'
					self.temp = self.proc_com(self.image_filename + ':')
					#print 'UAV: Result of pipe is : %s' % self.temp
				elif cmd == 'Close':
					os.write(self.toTransceiver, 'close:')
					time.sleep(1)
					os.kill(self.controller.pid, signal.SIGTERM)
					sys.exit(0)
				elif cmd == 'FFT':
					#print 'UAV: FFT command received.'
					self.controller.fft = 'True'
					os.write(self.toTransceiver, 'close:')
					time.sleep(1)
					#print 'UAV: Stopping Transceiver process.'
					os.kill(self.controller.pid, signal.SIGTERM)
					time.sleep(1)
					p = subprocess.Popen('python get_fft.py', shell=True)
					time.sleep(1)
					p.wait()
					#print 'UAV: Restoring Transceiver to transmit FFT.'
					self.controller.forkit()
				elif cmd == 'Telemetry':
					#print 'UAV: Telemetry command received.'
					if self.Telemetry_condition:
						self.retrieve_telemetry()
					else:
						fd = open(self.cwd + self.telemetry_filename, 'w')
						fd.write('00.0\n00.0')
						fd.close()
					self.temp = self.proc_com(self.telemetry_filename + ':')
					#print 'UAV: Result of pipe is : %s' % self.temp
					self.clear_file(self.telemetry_filename)
									
				elif cmd == 'GPS':
					#print 'UAV: Getting GPS.'
					if self.GPS_condition:
						self.GPS.get_gps('w', self.cwd + self.telemetry_filename)
					else:
						fd = open(self.cwd + self.telemetry_filename, 'w')
						fd.write('GPSD,P=0 0,A=0,V=0,E=0 0 0')
						fd.close()
					self.temp = self.proc_com(self.telemetry_filename + ':')
					#print 'UAV: Result of pipe is : %s' % self.temp
					self.clear_file(self.telemetry_filename)			
				elif cmd == 'Settings':
					self.retrieve_settings()
					self.clear_file(self.rx_filename)
				elif cmd == '':
					pass
				else:
					if cmd.count(':') > 0:
						self.temp = self.proc_com(cmd)
					else:
						self.temp = self.proc_com(cmd + ':')
			elif self.temp in self.rtn_list:
				self.timeout_counter += 1
				#print 'UAV: Return from Transceiver Process not True... ', self.temp
				#print 'Incrimenting Go Home Counter : %d' % self.timeout_counter
			elif self.temp == 'closing':
				#print 'Transceiver Closing, exiting...'
				sys.exit(0)
			else:
				os.write(self.toTransceiver, 'close:')
				time.sleep(1)
				os.kill(self.controller.pid, signal.SIGTERM)
				sys.exit(0)

			if self.timeout_counter == 2:
				self.go_home()
				os.write(self.toTransceiver, 'set_frequency:' + self.default_freq)
				time.sleep(1)
				os.write(self.toTransceiver, 'set_timeout:' + self.default_timeout)
				time.sleep(1)
				self.timeout_counter = 0

	def retrieve_telemetry(self):
		temprature = subprocess.Popen('python temp.py', shell=True)
		time.sleep(1)
		temprature.wait()
		batt = subprocess.Popen('python batt.py', shell=True)
		time.sleep(1)
		batt.wait()

	def retrieve_settings(self):
		tmp_freq = None
		tmp_timeout = None
		fd = open(self.cwd + self.rx_filename, 'r')
		for l in fd:
			if l.startswith("Freq:"):
				junk, tmp_freq = l.split()
				if tmp_freq != None:
					self.freq = tmp_freq
					os.write(self.toTransceiver, 'set_frequency:' + self.freq)
					time.sleep(1)
			if l.startswith("Timeout:"):
				junk, tmp_timeout = l.split()
				if tmp_timeout != None:
					self.timeout = tmp_timeout
					os.write(self.toTransceiver, 'set_timeout:' + self.timeout)
					time.sleep(1)
		fd.close()

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
		os.write(self.toTransceiver, data)
		return os.read(self.fromTransceiver,1024)

	def go_home(self):
		self.freq = self.default_freq
		self.timeout = self.default_timeout

	def init_files(self):
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
