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
		self.trans = txrx_controller(frame_time_out=self.time_0, hand_shaking_max=self.hand_max)
		self.gps = GPS_getter()
		time.sleep(2)
		self.trans.set_frequency(self.tx_freq, 'tx')
		self.trans.set_frequency(self.rx_freq, 'rx')
		self.trans.set_rx_file_path(self.f_name_rx)
		
		#handles if controller restarts with a command still to be sent down
		#tells the ground there was an error
		tmp = self.get_command()
		if not tmp == '':
			self.trans.transmit('Error')
		rx = True
		tx = True
		
		#This is the main controller section of code
		while True:
			if rx:
				tmp = self.trans.receive()
				if tmp is True or tmp == 'Transmission Complete':
					tx = self.exec_command(self.get_command())
				elif tmp == 'Handshaking Maximum Reached' or tmp == 'Timeout':
					self.send_error(tmp)
					tx = True
			
			if tx:
				tmp = self.trans.transmit(self.f_name_tx)
				if tmp is True or tmp == 'Transmission Complete':
					rx = True
				elif tmp == 'Handshaking Maximum Reached' or tmp == 'Timeout' or tmp == 'Error':
					rx = False
	
	def send_error(self, msg):
		fd = open('/uav/misc.dat', 'w')
		fd.write(msg)
		fd.close()
		self.f_name_tx = '/uav/misc.dat'
	
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
			return False
		elif(command == "picture"):
			self.log("Taking Picture")
			os.system("uvccapture -q100 -o/uav/pic.jpg")
			self.f_name_tx = "/uav/pic.jpg"
			return True
		elif(command == "fft"):
			self.log("Getting FFT Data")
			spawnl(os.P_WAIT, '/usr/bin/python', 'python', 'get_fft.py')
			self.f_name_tx = "/uav/fft_image.jpeg"
			return True
		elif(command == "sensors"):
			self.log("Getting Telemetry Data")
			temp_pid = os.spawnl(os.P_NOWAIT, '/usr/bin/python', 'python', 'get_temp.py')
			batt_pid = os.spawnl(os.P_NOWAIT, '/usr/bin/python', 'python', 'get_batt.py')
			self.gps.get_gps('w')
			while(self.pid_exists(temp_pid) or self.pid_exists(batt_pid)):
				pass
			os.system("cat batt.dat temp.dat gps.dat > misc.dat")
			self.f_name_tx = "/uav/misc.dat"
			return True
	
	def get_command(self):
		fd = open(self.f_name_rx, 'rw')
		tmp = fd.readline().strip('\n').strip()
		fd.seek(0)
		fd.write('')
		fd.close()
		return tmp
	
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
		self.f_name_rx = '/uav/rx_file'
	
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
