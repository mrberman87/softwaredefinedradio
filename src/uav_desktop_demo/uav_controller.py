#!/usr/bin/env python

import os, ctypes, usb, time, subprocess
from daemon import *
from txrx_controller import *
#from GPS_getter import *
from wd_reset import *

#class uav_controller(Daemon):
class uav_controller():
	def run(self):
		#set priority
		os.system("renice 0 %d" % os.getpid())
		#changing the system name of this program when it's running
		libc = ctypes.CDLL('libc.so.6')
		libc.prctl(15, 'UAV Controller', 0, 0, 0)
		#intializing the system
		self.init_vars()
		os.chdir(self.working_dir)
		self.init_files()
		self.log("Starting Up: pid = %d" % os.getpid())
		#setting up the usb controller
		try:
			self.dev = usb.core.find(idVendor=65534, idProduct=2)
			time.sleep(1)
			self.dev.set_configuration()
			time.sleep(1)
			self.dev.reset()
		except:
			pass
		#starting threads to reset the watchdog timers
		#self.wd1 = wd_reset(self.working_dir + '/daemon_pids/wd1_controller.wd', 5).start()
		#self.wd2 = wd_reset(self.working_dir + '/daemon_pids/wd2_controller.wd', 5).start()
		#set_params will initialize self.trans, it is just being allocated here
		self.trans = None
		#the next line is to set the link to 8psk outright for testing
		self.version = 'bpsk'
		self.set_params()
		#self.gps = GPS_getter()
	       
		#initialize local variables specific to controlling the transceiver
		rx = True
		tx = True
		
		try:
			#This is the main controller section of code
			while True:
				#this condition deals with receiving things from the ground
				print "Ready to GO!!!"
				if rx:
					#this is reached when a transmission is completed normally, and the other
					#side gets all of the data
					tmp = self.trans.receive()
					if tmp is True or tmp == 'Transmission Complete':
						tx = self.exec_command(self.get_command())
						self.clear_file(self.working_dir + self.f_name_rx)
						self.home = 0
					#this is reached when there is an error and either a timeout is reached, or
					#the transmission cannot complete with the given number of hand shakes
					elif tmp == 'Handshaking Maximum Reached' or tmp == 'Timeout':
						tx = False
						self.home = self.home + 1
						self.log(tmp)
					#this is reached when there is a general error from the ground
					elif tmp == 'Error':
						tx = False
						self.home = self.home + 1
						self.log(tmp)
	
				if self.home >= 2:
					tx = False
					self.go_home()
					self.set_params(self.trans.scheme!=self.version)
					self.log("Going Home...")
	
				#this condition deals with transmitting data back to the ground
				if tx:
					print "Transmitting: " + self.f_name_tx
					tmp = self.trans.transmit(self.f_name_tx)
					#this section is reached when the transmission completes as normal
					if tmp is True or tmp == 'Transmission Complete':
						rx = True
						self.home = 0
					#this section is reached when there is a problem sending the information to the other
					#side of the link
					elif tmp == 'Handshaking Maximum Reached' or tmp == 'Timeout' or tmp == 'Error':
						rx = False
						self.home = self.home + 1
						self.log(tmp)
		except:
			sys.exit(0)
       
	#this method sets up the transmittion of an erroneous message
	def send_error(self, msg):
		self.f_name_tx = '/misc.dat'
		path = self.f_name_tx
		self.clear_file(path)
		fd = open(path, 'w')
		fd.write(msg)
		fd.close()
       
	#this method takes the command from the ground, and executes what it needs to in order to fulfill the command
	def exec_command(self, command):
		print "Got Command: " + command
		#this changes the communication link's settings (ie - frequency, modulation scheme, etc.)
		if(command == "Settings"):
			to_log = "Changing Settings:"
			tmp_freq = None
			tmp_time_0 = None
			tmp_version = None
			fd = open(self.working_dir + self.f_name_rx, 'r')
			#this for loop goes through the file and pulls out only what is sent to be changed
			for l in fd:
				if l.startswith("Freq:"):
					junk, tmp_freq = l.split()
					if tmp_freq != None:
						self.freq = int(tmp_freq)
						to_log = to_log + " Freq = %d" % self.freq
				if l.startswith("Timeout:"):
					junk, tmp_time_0 = l.split()
					if tmp_time_0 != None:
						self.time_0 = int(tmp_time_0)
						to_log = to_log + " Timeout = %d" % self.time_0
				if l.startswith("Version:"):
					junk, tmp_version = l.split()
					if tmp_version != None:
						self.version = tmp_version.lower()
						to_log = to_log + " Modulation Scheme = %s" % self.version
			fd.close()
			self.set_params(tmp_version != None)
			self.log(to_log)
			return False
		#this takes a picture
		elif(command == "Image"):
			self.log("Taking Picture")
			self.f_name_tx = "/pic.jpg"
			self.pic = subprocess.Popen('uvccapture -q100 -o%s' % (self.working_dir + self.f_name_tx), shell=True)
			self.pic.wait()
			return True
		#this gets an FFT of the air
		elif(command == "FFT"):
			self.log("Getting FFT Data")
			self.dev.reset()
			self.f_name_tx = "/fft.png"
			time_not = time.time()
			self.fft = subprocess.Popen('python get_fft.py %s %s %d %s' % (self.working_dir+'/real',
				self.working_dir+'/imaginary', self.freq, self.working_dir + self.f_name_tx), shell=True)
			self.fft.wait()
			self.set_params()
			return True
		#this gets temprature and battery voltage as well as GPS location of the UAV
		elif(command == "Telemetry"):
			self.log("Getting Telemetry Data")
			self.f_name_tx = "/misc.dat"
			self.clear_file(self.working_dir + self.f_name_tx)
			time.sleep(1.5)
			self.temp = subprocess.Popen('python temp.py %s' % self.working_dir, shell=True)
			self.temp.wait()
			time.sleep(1.5)
			self.batt = subprocess.Popen('python batt.py %s' % self.working_dir, shell=True)
			self.batt.wait()
			return True
		elif(command == "GPS"):
			self.f_name_tx = "GPSD,P=34.240 -118.529,A=258.600,V=0,E=0.00 ? ?"
			return True
			self.log("Getting GPS Data")
			self.f_name_tx = "/misc.dat"
			self.gps.get_gps('w', self.working_dir + self.f_name_tx)
			return True
		#this will execute a cli command, and send the result back to the gound
		elif(command == "command"):
			fd = open(self.working_dir + self.f_name_rx, 'r')
			cli = fd.readline()  #the command is on the second line
			cli = fd.readline().strip('\n').strip()
			fd.close()
			self.log("Executing Command: %s" % cli)
			self.f_name_tx = "/misc.dat"
			self.comm = subprocess.Popen('%s > %S' % (cli, self.working_dir + self.f_name_tx), shell=True)
			self.comm.wait()
			return True
       
	#this parses out what the command to be executed from the ground is
	def get_command(self):
		fd = open(self.working_dir + self.f_name_rx, 'r')
		tmp = fd.readline().strip('\n').strip()
		fd.close()
		return tmp
       
	#this appends a log file with useful, timestamped information
	def log(self, string):
		print string
		fd = open("log.dat", "a")
		fd.write(str(time.ctime(time.time())) + "     " + string + '\n')
		fd.close()
       
	#this clears the contents of a given file
	def clear_file(self, path):
		fd = open (path, 'w')
		fd.write("")
		fd.close()
       
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
		#sets where the working direcotry is even if os.getcwd() is not here
		self.working_dir = os.getcwd()
		#file name of what has been sent to the air
		self.f_name_rx = '/rx_data'
		#this tracks the number of erroneous tries on the data link before going home
		self.errors = 0
       
	#this sets the "go home" variables
	def go_home(self):
		self.freq = 440e6
		self.time_0 = 45
		self.version = 'bpsk'
		self.home = 0
       
	#this sets parameters for the txrx_controller
	#calling this will also initialze the controller
	def set_params(self, new_mod = True):
		if new_mod:
			del self.trans
			self.dev.reset()
			self.trans = txrx_controller(frame_time_out = self.time_0,
				work_directory=self.working_dir, fc = self.freq, centoff=0,
				foffset_tx=100e3, foffset_rx=-50e3, rx_file=self.f_name_rx,
				version = self.version)
		else:
			self.trans.set_frame_time_out(self.time_0)
			self.trans.set_frequency(self.freq)
	
	#this initializes files that the UAV controller may need in its operation
	def init_files(self):
		#This method makes sure that all files needed for this
		#program are exist.
		if(not os.path.exists("pic.jpg")):
			subprocess.Popen('touch pic.jpg', shell=True)
		if(not os.path.exists("fft.png")):
			subprocess.Popen('touch fft.png', shell=True)
		if(not os.path.exists("misc.dat")):
			subprocess.Popen('touch misc.dat', shell=True)
		if(not os.path.exists("log.dat")):
			subprocess.Popen('touch log.dat', shell=True)
		if(not os.path.exists("imaginary")):
			subprocess.Popen('touch imaginary', shell=True)
		if(not os.path.exists("real")):
			subprocess.Popen('touch real', shell=True)
		if(not os.path.exists("rx_data")):
			subprocess.Popen('touch rx_data', shell=True)
		if(not os.path.exists("log.dat")):
			subprocess.Popen('touch log.dat', shell=True)

if __name__ == '__main__':
	#for running as a stand along within a shell
	uav_controller().run()
	#this sets up this controller as a daemon to run in the background
	
	'''daemon = uav_controller(self.working_dir + '/daemon_pids/uav_controller.pid')
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
		sys.exit(2)'''
