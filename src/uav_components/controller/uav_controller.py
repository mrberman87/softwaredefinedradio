#!/usr/bin/env python

import os, ctypes, usb, time, subprocess
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
		#set_params will initialize self.trans, it is just being allocated here
		self.trans = None
		self.set_params()
		self.gps = GPS_getter()
		
		#initialize local variables specific to controlling the transceiver
		rx = True
		tx = True
		going_home = False
		
		#This is the main controller section of code
		while True:
			#this condition deals with receiving things from the ground
			if rx:
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
			
			#this condition deals with getting errors with receiving
			if self.errors > 3:
				self.log("Had more than 3 errors, going home!")
				self.send_error("going home")
				going_home = True
			
			#this condition deals with transmitting data back to the ground
			if tx:
				tmp = self.trans.transmit(self.f_name_tx)
				if tmp is True or tmp == 'Transmission Complete':
					rx = True
					if going_home:
						self.go_home()
						self.set_params()
						going_home = False
				elif tmp == 'Handshaking Maximum Reached' or tmp == 'Timeout' or tmp == 'Error':
					rx = False
	
	#this method sets up the transmittion of an erroneous message
	def send_error(self, msg):
		self.clear_file('/uav/misc.dat')
		fd = open('/uav/misc.dat', 'w')
		fd.write(msg)
		fd.close()
		self.f_name_tx = '/misc.dat'
	
	#this method takes the command from the ground, and executes what it needs to in order to fulfill the command
	def exec_command(self, command):
		#this changes the communication link's settings (ie - frequency, modulation scheme, etc.)
		if(command == "settings"):
			self.log("Changing Settings")
			fd = open(self.f_name_rx, 'r')
			for l in fd:
				if l.startswith("Tx_Freq:"):
					junk, tmp_tx_freq = l.split()
					self.tx_freq = int(tmp_tx_freq)
				if l.startswith("Rx_Freq:"):
					junk, tmp_rx_freq = l.split()
					self.rx_freq = int(tmp_rx_freq)
				if l.startswith("Timeout:"):
					junk, tmp_time_0 = l.split()
					self.time_0 = int(tmp_time_0)
				if l.startswith("Hand_Max:")
					junk, tmp_hand_max = l.split()
					self.hand_max = int(tmp_hand_max)
				if l.startswith("Version:"):
					junk, self.version = l.split()
			fd.close()
			self.set_params()
			self.log("Changing Settings: Tx Freq = %d, Rx Freq = %d, Timeout Time = %d, Handshaking Max = %d" % (self.tx_freq, self.rx_freq, self.time_0, self.hand_max))
			return False
		#this takes a picture
		elif(command == "picture"):
			self.log("Taking Picture")
			self.pic = subprocess.Popen('uvccapture -q100 -o/uav/pic.jpg', shell=True)
			os.waitpid(self.pic.pid, 0)
			time.sleep(2)
			self.f_name_tx = "/pic.jpg"
			return True
		#this gets an FFT of the air
		elif(command == "fft"):
			self.log("Getting FFT Data")
			del self.trans
			self.dev.reset()
			time.sleep(2)
			self.fft = subprocess.Popen('python get_fft.py', shell=True)
			os.waitpid(self.fft.pid, 0)
			self.set_params()
			self.f_name_tx = "/fft_image.jpeg"
			return True
		#this gets temprature and battery voltage as well as GPS location of the UAV
		elif(command == "sensors"):
			self.log("Getting Telemetry Data")
			self.tel = subprocess.Popen('python telemetry.py', shell=True)
			os.waitpid(self.tel.pid, 0)
			self.gps.get_gps('w')
			self.merg = subprocess.Popen('cat sensor.dat gps.dat > misc.dat', shell=True)
			os.waitpid(self.merg.pid, 0)
			self.f_name_tx = "/misc.dat"
			return True
		#this will execute a cli command, and send the result back to the gound
		elif(command == "command"):
			fd = open(self.f_name_rx, 'r')
			cli = fd.readline.strip('\n').strip()
			fd.close()
			self.log("Executing Command: %s" % cli)
			self.comm = subprocess.Popen('%s > misc.dat' % cli, shell=True)
			os.waitpid(self.comm.pid, 0)
			self.f_name_tx = "/misc.dat"
			return True
	
	#this parses out what the command to be executed from the ground is
	def get_command(self):
		fd = open(self.f_name_rx, 'rw')
		tmp = fd.readline().strip('\n').strip()
		fd.close()
		self.clear_file(self.f_name_rx)
		return tmp
	
	#this appends a log file with useful, timestamped information
	def log(self, string):
		fd = open("log.dat", "a")
		fd.write(str(time.ctime(time.time())) + "     " + string + '\n')
		fd.close()
	
	#this clears the contents of a given file
	def clear_file(self, path):
		p = subprocess.Popen('>%s' % path, shell=True)
		os.waitpid(p.pid, 0)
	
	#this checks if a given pid exists on the system
	#if it is a zombie, it will kill it
	def pid_exists(self, pid):
		try:
			fd = open('/proc/%d/status' % pid, 'r')
			for l in fd:
				if(l.startswith('State:')):
					junk, s, text = l.split( None, 2 )
			fd.close()
			if(s != "Z"):
				return True
			os.waitpid(pid, os.WNOHANG)
			return False
		except IOError, OSError:
			return False
	
	#this kills any process given its pid
	def kill_pid(self, pid):
		try:
			os.kill(pid, 9)
			return not self.pid_exists(pid)
		except OSError:
			return True
	
	#this initializes class level variables
	def init_vars(self):
		self.go_home()
		
		#file name of what is going to be sent to the ground
		self.f_name_tx = ''
		
		#file name of what has been sent to the air
		self.f_name_rx = '/uav/rx_data'
		
		#this tracks the number of erroneous tries on the data link before going home
		self.errors = 0
		
		#keeps track of the modulation scheme being used
		self.version = '8psk'
	
	#this sets the "go home" variables
	def go_home(self):
		self.tx_freq = 440000000
		self.rx_freq = 440050000
		self.time_0 = 35
		self.hand_max = 5
	
	#this sets parameters for the txrx_controller
	#calling this will also initialze the controller
	def set_params(self):
		del self.trans
		self.dev.reset()
		time.sleep(2)
		self.trans = txrx_controller(work_directory='/uav', version = self.version)
		time.sleep(2)
		#self.trans.set_frequency(self.tx_freq, 'tx')
		#self.trans.set_frequency(self.rx_freq, 'rx')
		#self.trans.set_rx_path(self.f_name_rx)
	
	#this initializes files that the UAV controller may need in its operation
	def init_files(self):
		#This method makes sure that all files needed for this
		#program are exist.
		if(not os.path.exists("pic.jpg")):
			subprocess.Popen('touch pic.jpg', shell=True)
		if(not os.path.exists("sensor.dat")):
			subprocess.Popen('touch sensor.dat', shell=True)
		if(not os.path.exists("misc.dat")):
			subprocess.Popen('touch misc.dat', shell=True)
		if(not os.path.exists("gps.dat")):
			subprocess.Popen('touch gps.dat', shell=True)
		if(not os.path.exists("log.dat")):
			subprocess.Popen('touch log.dat', shell=True)
		if(not os.path.exists("RC.dat")):
			subprocess.Popen('touch RC.dat', shell=True)
		if(not os.path.exists("rx_data")):
			subprocess.Popen('touch rx_data', shell=True)
	
	#this loads up variables that were saved from the previous run of this process
	def check_saved_vars(self):
		if not os.path.exists('/uav/saved_vars'):
			return
		fd = open('/uav/saved_vars', 'r')
		self.tx_freq = int(fd.readline().strip('\n').strip())
		self.rx_freq = int(fd.readline().strip('\n').strip())
		self.version = fd.readline().strip('\n').strip()
		fd.close()
		os.remove('/uav/saved_vars')
		return
	
	#this handles the book keeping of processes, and saving variables
	def __del__(self):
		self.log("Closeing")
		if self.pid_exists(self.pic.pid):
			self.kill_pid(self.pic.pid)
		if self.pid_exists(self.fft.pid):
			self.kill_pid(self.fft.pid)
		if self.pid_exists(self.tel.pid):
			self.kill_pid(self.tel.pid)
		if self.pid_exists(self.merg.pid):
			self.kill_pid(self.merg.pid)
		if self.pid_exists(self.comm.pid):
			self.kill_pid(self.comm.pid)
		
		"""p = subprocess.Popen('touch /uav/saved_vars', shell=True)
		os.waitpid(p.pid, 0)
		fd = open('/uav/saved_vars', 'w')
		fd.write("%d\n" % self.tx_freq)
		fd.write("%d\n" % self.rx_freq)
		fd.write("%s\n" % self.version)
		fd.close()"""

if __name__ == '__main__':
	uav_controller().run()
	"""
	#this sets up this controller as a daemon to run in the background
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
