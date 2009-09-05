#!/usr/bin/env python

import os, time, ctypes
from deamon import *
from txrx_controller import *
from GPS_getter import *

class uav_controller(Deamon):
	def run(self):
		#set priority
		os.system("renice 0 %d" % os.getpid())
		libc = ctypes.CDLL('libc.so.6')
		libc.prctl(15, 'UAV Controller', 0, 0, 0)
		self.log("Starting Up: pid = %d" % os.getpid())
		self.init_vars()
		self.init_files()
		self.trans = txrx_controller(self.tx_freq, self.rx_freq, self.time_0, self.hand_max)
		self.gps = GPS_getter()
		
		#This is the main controller section of code
		while True:
			
				
	
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
			self.set_params()
			self.log("Changing Settings: Tx Freq = %d, Rx Freq = %d, Timeout Time = %d, Handshaking Max = %d" % (self.tx_freq, self.rx_freq, self.time_0, self.hand_max))
			self.f_name_tx = "/uav/%s" % self.f_name_rx
		elif(command == "picture"):
			self.log("Taking Picture")
			os.system("uvccapture -q100 -o/uav/pic.jpg")
			self.f_name_tx = "/uav/pic.jpg"
		elif(command == "fft"):
			self.log("Getting FFT Data")
			spawnl(os.P_WAIT, '/usr/bin/python', 'python', 'get_fft.py')
			self.f_name_tx = "/uav/fft_image.jpeg"
		elif(command == "sensors"):
			self.log("Getting Telemetry Data")
			temp_pid = os.spawnl(os.P_NOWAIT, '/usr/bin/python', 'python', 'get_temp.py')
			batt_pid = os.spawnl(os.P_NOWAIT, '/usr/bin/python', 'python', 'get_batt.py')
			self.gps.get_gps('w')
			while(self.pid_exists(temp_pid) or self.pid_exists(batt_pid)):
				pass
			os.system("cat batt.dat temp.dat gps.dat > misc.dat")
			self.f_name_tx = "/uav/misc.dat"
	
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
	
	def kill_pid(self, pid):
		try:
			os.kill(pid, 9)
			return not self.pid_exists(pid)
		except OSError:
			return True
	
	def log(self, string):
		fd = open("log.dat", "a")
		fd.write(str(time.ctime(time.time())) + "     " + string + '\n')
		fd.close()
	
	def init_vars(self):
		self.go_home()
		
		#file name of what is going to be sent to the ground
		self.f_name_tx = ''
		
		#file name of what has been sent to the air
		self.f_name_rx = ''
	
	def go_home(self):
		self.tx_freq = 440000000
		self.rx_freq = 440050000
		self.time_0 = 35
		self.hand_max = 5
	
	def set_params(self):
		
	
	def init_files(self):
		#This method makes sure that all files needed for this
		#program are exist.
		if(not os.path.exists("pic.jpg")):
			os.system("touch pic.jpg")
		if(not os.path.exists("temp.dat")):
			os.system("touch temp.dat")
		if(not os.path.exists("batt.dat")):
			os.system("touch batt.dat")
		if(not os.path.exists("misc.dat")):
			os.system("touch misc.dat")
		if(not os.path.exists("gps.dat")):
			os.system("touch gps.dat")
		if(not os.path.exists("log.dat")):
			os.system("touch log.dat")
		if(not os.path.exists("RC.dat")):
			os.system("touch RC.dat")

if __name__ == '__main__':
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
		sys.exit(2)
