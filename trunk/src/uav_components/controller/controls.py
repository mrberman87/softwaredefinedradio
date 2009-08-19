#!/usr/bin/env python

import os, time

class controls:
	def __init__(self):
		self.log("Starting Up: pid = %d" % os.getpid())
		self.init_vars()
		self.init_files()
	
	def check_rx_file(self, f_name):
		fd = open(f_name, "r")
		if len(fd.readline()) > 0:
			return True
		return False
	
	def run_to_module(self):
		return os.spawnl(os.P_NOWAIT, '/usr/bin/python', 'python', self.to_mod_name, "-t", "%d" % self.timeout_t)
	
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
	
	def exec_command(self):
		"""
		Commands to be run are as follows:
			"picture" -> sends down an image
			"fft" -> sends down an FFT
			"misc data" -> sends down GPS, Temp. and Batt level
			"settings" + '\n' + "<frequency>" + '\n' + "<modulation scheme>"
					+ '\n' + "<timeout time>"
				-> This will change the frequency, modulation
				   scheme and timeout time as defined in the sent
				   message.  If a setting is not clear, or cannot be
				   acheived, then that setting will not be modified
			If the sent file's first line doesnt contain one of these
			commands, then the UAV will default to executing the 
			"misc_data" command.
		"""
		_file = open(self.f_name_rx, 'rw')
		command = _file.readline().strip('\n').strip()
		_file.seek(0)
		_file.write("")
		_file.close()
		self.last_mod = time.localtime(os.path.getmtime(self.f_name_rx))
		
		print "Received Command: " + command + '\n'
		
		if(command == "settings"):
			self.log("Changing Settings")
			print "changing settings...\n"
			self.last_mod = time.localtime()
			return False
			_file = open(self.f_name_rx, 'r')
			_file.readline()
			tmp_freq = int(_file.readline().strip('\n').strip())
			tmp_timeout_t = int(_file.readline().strip('\n').strip())
			_file.close()
			self.last_mod = time.localtime(os.path.getmtime(self.f_name_rx))
			if chk_settings(tmp_freq, tmp_mod_sch, tmp_timeout_t):
				self.err_data = 0
				self.log("Changing Settings: Freq = %d, Mod Scheme = %s, Timeout Time = %d" % (tmp_freq, tmp_mod_sch, tmp_timeout_t))
				return False
		elif(command == "picture"):
			self.log("Taking Picture")
			print "taking picture...\n"
			self.last_mod = time.localtime()
			return True
			os.system("uvccapture -q100 -o%s%s" % (os.getcwd(), "/pic.jpg"))
			self.f_name_tx = "pic.jpg"
			self.err_data = 0
			return True
		elif(command == "fft"):
			self.log("Getting FFT Data")
			print "getting fft data...\n"
			self.last_mod = time.localtime()
			return True
			spawnl(os.P_WAIT, '/usr/bin/python', 'python', 'get_fft.py')
			self.f_name_tx = "fft.dat"
			self.err_data = 0
			return True
		elif(command == "sensors"):
			self.log("Getting Telemetry Data")
			os.system("cat batt.dat temp.dat gps.dat > misc.dat")
			print "getting telemetery data...\n"
			self.last_mod = time.localtime()
			return True
			gps_pid = spawnl(os.P_NOWAIT, '/usr/bin/python', 'python', 'get_gps.py')
			temp_pid = spawnl(os.P_NOWAIT, '/usr/bin/python', 'python', 'get_temp.py')
			batt_pid = spawnl(os.P_NOWAIT, '/usr/bin/python', 'python', 'get_batt.py')
			while(pid_exists(temp_pid) or pid_exists(batt_pid) or pid_exists(gps_pid)):
				pass
			os.system("cat batt.dat temp.dat gps.dat > misc.dat")
			self.f_name_tx = "misc.dat"
			self.err_data = 0
			return True
		
		self.log("Received Erroneous Command!!! => (" + command + ")")
		fd = open("misc.dat", 'w')
		fd.write("erroneous command")
		fd.close()
		self.f_name_tx = "misc.dat"
		self.err_data += 1
		if(self.err_data > 3):
			self.err_data = 0
			self.go_home()
		print "letting ground know of error getting command...\n"
		return True
	
	def chk_settings(self, f, m, t):
		if((f > 400000000 and f < 500000000) and (t > 10 and t < 100)):
			return True
		return False
	
	def log(self, string):
		fd = open("log.dat", "a")
		fd.write(str(time.ctime(time.time())) + "     " + string + '\n')
		fd.close()
	
	def update_rx_opts(self):
		self.rx_opts = ['python', self.rx_mod_name,]
		self.rx_opts.append("--freq=%d" % (self.freq + self.freq_offset))
		self.rx_opts.append('--file=%s' % self.f_name_rx)
	
	def update_tx_opts(self):
		self.tx_opts = ['python', self.tx_mod_name, '--freq']
		self.tx_opts.append(self.freq + self.freq_offset)
		self.tx_opts.append('--file')
		self.tx_opts.append(self.f_name_tx)
	
	def init_vars(self):
		#Initialize variables that define the "Go Home" state
		self.go_home()
		
		#Timeout Module Name
		self.to_mod_name = "./timeout_process.py"
		
		#Transceiver Variation
		self.freq_offset = 0
		
		#keep track of received erroneous data
		self.err_data = 0
		
		#Receive File modification Time
		self.last_mod = time.localtime(os.path.getmtime(self.f_name_rx))
		
	def go_home(self):
		print "going home...\n"
		#Transceiver Frequency
		self.freq = 440000000
		
		#Set timeout
		self.timeout_t = 60000
	
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
	
	def __del__(self):
		self.log("Closeing...")
		self.kill_pid(self.to_pid)


