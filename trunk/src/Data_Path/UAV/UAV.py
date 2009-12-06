from GPS_getter import *
import os, time, sys, signal


class UAV:
	def __init__(self, controller, toTransceiver, fromTransceiver):
		self.init_files()
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
		self.toTransceiver = toTransceiver
		self.fromTransceiver = fromTransceiver
		self.temp = temp()
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
					os.write(toTransceiver, 'close:')
					time.sleep(1)
					os.kill(pid, signal.SIGTERM)
					sys.exit(0)
				elif cmd == 'FFT':
					print 'UAV: FFT command received.'
					controller.fft = True
					os.write(toTransceiver, 'close:')
					time.sleep(1)
					print 'UAV: Stopping Transceiver process.'
					os.kill(pid, signal.SIGTERM)
					time.sleep(1)
					p = subprocess.Popen('python get_fft.py', shell=True)
					time.sleep(1)
					p.wait()
					print 'UAV: Restoring Transceiver to transmit FFT.'
					controller.forkit()
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
								os.write(toTransceiver, 'set_frequency:' + freq)
								time.sleep(1)
						if l.startswith("Timeout:"):
							junk, tmp_timeout = l.split()
							if tmp_timeout != None:
								timeout = tmp_timeout
								os.write(toTransceiver, 'set_timeout:' + timeout)
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
			elif temp == 'closing':
				print 'Transceiver Closing, exiting...'
				sys.exit(0)
			else:
				os.write(toTransceiver, 'close:')
				time.sleep(1)
				os.kill(pid, signal.SIGTERM)
				sys.exit(0)

			if self.timeout_counter == 2:
				self.go_home()
				os.write(toTransceiver, 'set_frequency:' + self.default_freq)
				time.sleep(1)
				os.write(toTransceiver, 'set_timeout:' + self.default_timeout)
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
		os.write(toTransceiver, data)
		return os.read(fromTransceiver,1024)

	def go_home(self):
		self.freq = self.default_frequency
		self.timeout = self.dafault_timeout

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
