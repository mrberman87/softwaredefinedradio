#!/usr/bin/env python

import os, ctypes, usb, time
from daemon import *
from txrx_controller import *
from GPS_getter import *
from wd_reset import *

class uav_controller():
	def run(self):
		#set priority
		os.system("renice 0 %d" % os.getpid())
		libc = ctypes.CDLL('libc.so.6')
		libc.prctl(15, 'UAV Controller', 0, 0, 0)
		self.log("Starting Up: pid = %d" % os.getpid())
		self.dev = usb.core.find(idVendor=65534, idProduct=2)
		self.dev.set_configuration()
		self.dev.reset()
		self.wd1 = wd_reset('/uav/daemon_pids/wd1_controller.wd', 5).start()
		self.wd2 = wd_reset('/uav/daemon_pids/wd2_controller.wd', 5).start()
		self.init_vars()
		self.init_files()
		#self.check_saved_vars()
		self.trans = txrx_controller(work_directory='/uav', version = '8psk')
		self.gps = GPS_getter()
		time.sleep(2)
		#self.set_params()
		
		rx = True
		tx = True
		
		#This is the main controller section of code
		while True:
			if rx:
				print "Test Point!!!"
				tmp = self.trans.receive()
				if tmp is True or tmp == 'Transmission Complete':
					tx = self.exec_command(self.get_command())
					self.errors = 0
				elif tmp == 'Handshaking Maximum Reached' or tmp == 'Timeout':
					self.send_error(tmp)
					tx = True
					self.errors = self.errors + 1
				elif tmp == 'Error':
					tx = True
					self.errors = self.errors + 1
			
			if self.errors > 3:
				self.log("Had more than 3 errors, going home!")
				self.go_home()
				self.set_params()
			
			if tx:
				print "transmitting: " + self.f_name_tx
				tmp = self.trans.transmit(self.f_name_tx)
				if tmp is True or tmp == 'Transmission Complete':
					rx = True
				elif tmp == 'Handshaking Maximum Reached' or tmp == 'Timeout' or tmp == 'Error':
					rx = False
	
	def send_error(self, msg):
		fd = open('/uav/misc.dat', 'w')
		fd.write(msg)
		fd.close()
		self.f_name_tx = '/misc.dat'
	
	def exec_command(self, command):
		if(command == "settings"):
			self.log("Changing Settings")
			_file = open(self.f_name_rx, 'r')
			_file.readline()
			self.tx_freq = int(_file.readline().strip('\n').strip())
			self.rx_freq = int(_file.readline().strip('\n').strip())
			self.time_0 = int(_file.readline().strip('\n').strip())
			self.hand_max = int(_file.readline().strip('\n').strip())
			_file.close()
			#self.set_params()
			self.log("Changing Settings: Tx Freq = %d, Rx Freq = %d, Timeout Time = %d, Handshaking Max = %d" % (self.tx_freq, self.rx_freq, self.time_0, self.hand_max))
			return False
		elif(command == "picture"):
			self.log("Taking Picture")
			os.system("uvccapture -q100 -o/uav/pic.jpg")
			time.sleep(1.5)
			self.f_name_tx = "/pic.jpg"
			return True
		elif(command == "fft"):
			self.log("Getting FFT Data")
			del self.trans
			self.dev.reset()
			time.sleep(2)
			os.spawnl(os.P_WAIT, '/usr/bin/python', 'python', 'get_fft.py')
			self.dev.reset()
			time.sleep(2)
			self.trans = txrx_controller(work_directory='/uav', version = '8psk')
			time.sleep(2)
			#self.set_params()
			self.f_name_tx = "/fft_image.jpeg"
			return True
		elif(command == "sensors"):
			self.log("Getting Telemetry Data")
			os.spawnl(os.P_WAIT, '/usr/bin/python', 'python', 'telemetry.py')
			self.gps.get_gps('w')
			os.system("cat sensor.dat gps.dat > misc.dat")
			self.f_name_tx = "/misc.dat"
			return True
	
	def get_command(self):
		fd = open(self.f_name_rx, 'rw')
		tmp = fd.readline().strip('\n').strip()
		fd.seek(0)
		fd.write('')
		fd.close()
		return tmp
	
	def log(self, string):
		fd = open("log.dat", "a")
		fd.write(str(time.ctime(time.time())) + "     " + string + '\n')
		fd.close()
	
	def init_vars(self):
		self.go_home()
		
		#file name of what is going to be sent to the ground
		self.f_name_tx = ''
		
		#file name of what has been sent to the air
		self.f_name_rx = '/uav/rx_data'
		
		#this tracks the number of erroneous tries on the data link before going home
		self.errors = 0
	
	def go_home(self):
		self.tx_freq = 440000000
		self.rx_freq = 440050000
		self.time_0 = 35
		self.hand_max = 5
	
	def set_params(self):
		self.trans.set_frequency(self.tx_freq, 'tx')
		self.trans.set_frequency(self.rx_freq, 'rx')
		self.trans.set_rx_path(self.f_name_rx)
	
	def init_files(self):
		#This method makes sure that all files needed for this
		#program are exist.
		if(not os.path.exists("pic.jpg")):
			os.system("touch pic.jpg")
		if(not os.path.exists("sensor.dat")):
			os.system("touch sensor.dat")
		if(not os.path.exists("misc.dat")):
			os.system("touch misc.dat")
		if(not os.path.exists("gps.dat")):
			os.system("touch gps.dat")
		if(not os.path.exists("log.dat")):
			os.system("touch log.dat")
		if(not os.path.exists("RC.dat")):
			os.system("touch RC.dat")
		if(not os.path.exists("rx_data")):
			os.system("touch rx_data")
	
	def check_saved_vars(self):
		path = os.getcwd() + "/saved_vars"
		if not os.path.exists("%s" % path):
			return
		fd = open(path, 'r')
		self.tx_freq = int(fd.readline().strip('\n').strip())
		self.rx_freq = int(fd.readline().strip('\n').strip())
		fd.close()
		os.system("rm %s" % path)
		return
	
	def __del__(self):
		self.log("Closeing")
		path = os.getcwd() + "/saved_vars"
		os.system("touch %s" % path)
		fd = open(path, 'w')
		fd.write("%d\n" % self.tx_freq)
		fd.write("%d\n" % self.rx_freq)
		fd.close()

if __name__ == '__main__':
	uav_controller().run()
	"""
	daemon = uav_controller('/uav/daemon_pids/uav_controller.pid')
	if len(sys.argv) == 2:
		if 'start' == sys.argv[1]:
			daemon.start()
		elif 'stop' == sys.argv[1]:
			daemon.stop()
		elif 'restart' == sys.argv[1]:
			daemon.restart()
		else:
			print "Unknown command"
			sys.exit(2)
		sys.exit(0)
	else:
		print "usage: %s start|stop|restart" % sys.argv[0]
		sys.exit(2)"""
