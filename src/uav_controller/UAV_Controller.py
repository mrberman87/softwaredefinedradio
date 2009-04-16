#!/usr/bin/env python

import os, time

class UAV_Controller:
	def __init__(self):
		#set priority
		os.system("renice 0 %d" % os.getpid())
		self.init_vars()
		self.init_files()
		
		#This is the main controller section of code
		while True:
			self.rx_pid = self.run_rx_module()
			self.to_pid = self.run_to_module()
			while(time.localtime(os.path.getmtime(self.f_name_rx)) <=  self.last_mod):
				#This handles "Go Home" situation from timeout
				if(not self.pid_exists(self.to_pid)):
					print "test point"
					self.timeout = True
					self.go_home()
					#self.kill_pid(self.rx_pid)
					self.update_rx_opts
					self.rx_pid = self.run_rx_module()
					self.to_pid = self.run_to_module()
					break
			
			#This handles getting all needed sensor data and/or changing
			#any and all settings for which file is to be transmitted
			#returns True if there is need to send something down
			if(self.exec_command()):
				#This sends down all neccessary data depending on the given command
				self.run_tx_module()
	
	def run_rx_module(self):
		print "Running Rx Module..."
		return 1
		"""
		self.update_rx_opts()
		return os.spawnv(os.P_NOWAIT, 'usr/bin/python', self.rx_opts)"""
	
	def run_to_module(self):
		return os.spawnl(os.P_NOWAIT, '/usr/bin/python', 'python', self.to_mod_name, "-t", "%d" % self.timeout_t)
	
	def run_tx_module(self):
		print "Running Tx Module..."
		return 2
		"""
		self.update_tx_opts()
		return spawnv(os.P_WAIT, 'usr/bin/python', self.tx_opts)"""
	
	def pid_exists(self, pid):
		try:
			fd = open('/proc/%d/status' % pid, 'r')
			for l in fd:
				if(l.startswith('State:')):
					junk, s, text = l.split( None, 2 )
			fd.close()
			if(s == "R" or s == "S" or s == "D"):
				return True
			os.waitpid(pid, os.WNOHANG)
			return False
		except IOError, OSError:
			return False
		
	def go_home(self):
		print "going home..."
		self.init_vars()
	
	def kill_pid(self, pid):
		os.kill(pid, 9)
		return not pid_exists(pid)
	
	def exec_command(self):
		"""
		Commands to be run are as follows:
			"picture" -> sends down an image
			"fft" -> sends down an FFT
			"misc data" -> sends down GPS, Temp. and Batt level
			"settings" + '\n' + "<frequency>" + '\n' + "<modulation scheme>"
					+ '\n' + "<timeout time>"
				-> This will change the frequency and modulation
				   scheme as defined in the sent message.
				   If a setting is not clear, or cannot be acheived,
				   then that setting will not be modified
			If the sent file's first line doesnt contain one of these
			commands, then the UAV will default to executing the 
			"misc_data" command.
		"""
		_file = open(self.f_name_rx, 'rw')
		command = _file.readline().strip('\n')
		
		if(command == "settings"):
			print "setting the settings..."
			_file.seek(0)
			_file.write("")
			_file.close()
			self.last_mod = time.localtime()
			return False
			self.freq = int(_file.readline().strip('\n'))
			self.mod_sch = _file.readline().strip('\n')
			self.timeout_t = int(_file.readline().strip('\n'))
			_file.seek(0)
			_file.write("")
			_file.close()
			self.last_mod = time.localtime()
			return False
		elif(command == "picture"):
			print "taking picture..."
			_file.seek(0)
			_file.write("")
			_file.close()
			self.last_mod = time.localtime()
			return True
			os.system("uvccapture -v -q100 -o%s/pic.dat" % os.getcwd())
			self.f_name_tx = "pic.dat"
			_file.seek(0)
			_file.write("")
			_file.close()
			self.last_mod = time.localtime()
			return True
		elif(command == "fft"):
			print "getting fft data..."
			_file.seek(0)
			_file.write("")
			_file.close()
			self.last_mod = time.localtime()
			return True
			spawnl(os.P_WAIT, "get_fft.py")
			self.f_name_tx = "fft.dat"
			_file.seek(0)
			_file.write("")
			_file.close()
			self.last_mod = time.localtime()
			return True
		elif(command == "sensors"):
			print "getting sensor data..."
			_file.seek(0)
			_file.write("")
			_file.close()
			self.last_mod = time.localtime()
			return True
			temp_pid = spawnl(os.P_NOWAIT, "get_temp.py")
			batt_pid = spawnl(os.P_NOWAIT, "get_batt.py")
			gps_pid = spawnl(os.P_NOWAIT, "get_gps.py")
			while(pid_exists(temp_pid) or pid_exists(batt_pid) or pid_exists(gps_pid)):
				pass
			self.comb_misc_data()
			self.f_name_tx = "misc.dat"
			_file.seek(0)
			_file.write("")
			_file.close()
			self.last_mod = time.localtime()
			return True
		
		fd = open("misc.dat", 'w')
		fd.write("erroneous command")
		fd.close()
		self.f_name_tx = "misc.dat"
		_file.seek(0)
		_file.write("")
		_file.close()
		self.last_mod = time.localtime()
		print "letting ground know of error getting command..."
		return True
	
	def update_rx_opts(self):
		self.rx_opts = ['python', self.rx_mod_name, '-f']
		self.rx_opts.append(self.freq + self.freq_offset)
		self.rx_opts.append('-m')
		self.rx_opts.append(self.mod_sch)
		self.rx_opts.append('--file')
		self.rx_opts.append(self.f_name_rx)
	
	def update_tx_opts(self):
		self.tx_opts = ['python', self.tx_mod_name, '-f']
		self.tx_opts.append(self.freq + self.freq_offset)
		self.tx_opts.append('-m')
		self.tx_opts.append(self.mod_sch)
		self.tx_opts.append('--file')
		self.tx_opts.append(self.f_name_tx)
	
	def comb_misc_data(self):
		f_out = open("misc.dat", "w")
		f_1 = open("temp.dat", "r")
		f_2 = open("batt.dat", "r")
		f_3 = open("gps.dat", "r")
		
		for line in f_1.readline():
			f_out.write(line+'\n')
		f_out.write('\n')
		f_1.close()
		
		for line in f_2.readline():
			f_out.write(line+'\n')
		f_out.write('\n')
		f_2.close()
		
		for line in f_3.readline():
			f_out.write(line+'\n')
		f_out.write('\n')
		f_3.close()
		f_out.close()
	
	def init_vars(self):
		#RX Module Name
		self.rx_mod_name = "./rx_file.py"
		
		#RX Parser options
		self.rx_opts = ""
				
		#TX Module Name
		self.tx_mod_name = "./tx_file.py"
		
		#TX Parser options
		self.tx_opts = ""
		
		#Timeout Module Name
		self.to_mod_name = "./timeout_process.py"
		
		#RX, TX, and Time_Out pid's
		self.rx_pid = 0
		self.tx_pid = 0
		self.to_pid = 0
		
		#Timeout Time (in seconds, can take parts of seconds)
		self.timeout_t = 15
		
		#Receive File
		self.f_name_rx = "RECEIVE"
		
		#Transmit File
		self.f_name_tx = "DATA"
		
		#Transceiver Frequency
		self.freq = 440000000
		
		#Transceiver Variation
		self.freq_offset = 0
		
		#Modulation Scheme
		self.mod_sch = "bpsk"
		
		#Receive File modification Time
		self.last_mod = time.localtime()
		
	def init_files(self):
		#This method makes sure that all files needed for this
		#program are exist.
		if(not os.path.exists("fft.dat")):
			os.system("touch fft.dat")
		if(not os.path.exists("pic.dat")):
			os.system("touch pic.dat")
		if(not os.path.exists("temp.dat")):
			os.system("touch temp.dat")
		if(not os.path.exists("batt.dat")):
			os.system("touch batt.dat")
		if(not os.path.exists("gps.dat")):
			os.system("touch gps.dat")
		if(not os.path.exists("misc.dat")):
			os.system("touch misc.dat")
		if(not os.path.exists("RECEIVE")):
			os.system("touch RECEIVE")

#This is the executable sections of code
if __name__ == '__main__':
	UAV_Controller()
