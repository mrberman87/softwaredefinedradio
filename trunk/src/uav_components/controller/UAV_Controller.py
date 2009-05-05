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
			self.timeout = False
			self.rx_pid = self.run_rx_module()
			self.to_pid = self.run_to_module()
			
			#waits until the "RECEIVE" file has been modified from receiving data
			while(time.localtime(os.path.getmtime(self.f_name_rx)) <=  self.last_mod):
				#This handles "Go Home" situation from timeout
				if(not self.pid_exists(self.to_pid)):
					print "test point"
					self.timeout = True
					self.go_home()
					self.kill_pid(self.rx_pid)
					self.update_rx_opts
					break
			
			#This handles getting all needed sensor data and/or changing
			#any and all settings for which file is to be transmitted
			#returns True if there is need to send something down
			if(self.timeout):
				#do nothing
				pass
			elif(self.exec_command()):
				#Timeout module may still be running, so make sure its dead
				self.kill_pid(self.to_pid)
				#This sends down all neccessary data depending on the given command
				self.run_tx_module()
	
	def run_rx_module(self):
		print "Running Rx Module..."
		return 1
		"""
		#modify file to be executed based on modulation scheme
		if(self.mod_sch == "bpsk"):
			self.rx_mod_name = "./bpsk_rx.py"
		elif(self.mod_sch == "qpsk"):
			self.rx_mod_name = "./qpsk_rx.py"
		elif(self.mod_sch == "8psk"):
			self.rx_mod_name = "./8psk_rx.py"
		self.update_rx_opts()
		return os.spawnv(os.P_NOWAIT, 'usr/bin/python', self.rx_opts)"""
	
	def run_to_module(self):
		return os.spawnl(os.P_NOWAIT, '/usr/bin/python', 'python', self.to_mod_name, "-t", "%d" % self.timeout_t)
	
	def run_tx_module(self):
		print "Running Tx Module..."
		return 2
		"""
		#modify file to be executed based on modulation scheme
		if(self.mod_sch == "bpsk"):
			self.tx_mod_name = "./bpsk_tx.py"
		elif(self.mod_sch == "qpsk"):
			self.tx_mod_name = "./qpsk_tx.py"
		elif(self.mod_sch == "8psk"):
			self.tx_mod_name = "./8psk_tx.py"
		self.update_tx_opts()
		return spawnv(os.P_WAIT, 'usr/bin/python', self.tx_opts)"""
	
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
		_file = open(self.f_name_rx, 'r')
		command = _file.readline().strip('\n')
		
		if(command == "settings"):
			print "setting the settings..."
			_file.close()
			self.last_mod = time.localtime()
			return False
			tmp_freq = int(_file.readline().strip('\n'))
			tmp_mod_sch = _file.readline().strip('\n')
			tmp_timeout_t = int(_file.readline().strip('\n'))
			if chk_settings(tmp_freq, tmp_mod_sch, tmp_timeout_t):
				self.last_mod = time.localtime()
				_file.close()
				self.err_data = 0
				return False
		elif(command == "picture"):
			print "taking picture..."
			_file.close()
			self.last_mod = time.localtime()
			return True
			os.system("uvccapture -q100 -o%s/pic.dat" % os.getcwd())
			self.f_name_tx = "pic.dat"
			_file.close()
			self.last_mod = time.localtime()
			self.err_data = 0
			return True
		elif(command == "fft"):
			print "getting fft data..."
			_file.close()
			self.last_mod = time.localtime()
			return True
			spawnl(os.P_WAIT, '/usr/bin/python', 'python', 'get_fft.py')
			self.f_name_tx = "fft.dat"
			_file.close()
			self.last_mod = time.localtime()
			self.err_data = 0
			return True
		elif(command == "sensors"):
			print "getting sensor data..."
			self.comb_misc_data()
			_file.close()
			self.last_mod = time.localtime()
			return True
			os.system("gpsd ... > gps.dat")
			temp_pid = spawnl(os.P_NOWAIT, '/usr/bin/python', 'python', 'get_temp.py')
			batt_pid = spawnl(os.P_NOWAIT, '/usr/bin/python', 'python', 'get_batt.py')
			while(pid_exists(temp_pid) or pid_exists(batt_pid) or pid_exists(gps_pid)):
				pass
			self.comb_misc_data()
			self.f_name_tx = "misc.dat"
			_file.close()
			self.last_mod = time.localtime()
			self.err_data = 0
			return True
		
		fd = open("misc.dat", 'w')
		fd.write("erroneous command")
		fd.close()
		self.f_name_tx = "misc.dat"
		_file.close()
		self.last_mod = time.localtime()
		self.err_data += 1
		if(self.err_data > 3):
			self.err_data = 0
			self.go_home()
		print "letting ground know of error getting command..."
		return True
	
	def chk_settings(self, f, m, t):
		if((f > 400000000 and f < 500000000) and (m = 'bpsk' or m = 'qpsk' or m = '8psk') and (t > 10 and t < 100)):
			return True
		return False
	
	def update_rx_opts(self):
		self.rx_opts = ['python', self.rx_mod_name, '-f']
		self.rx_opts.append(self.freq + self.freq_offset)
		self.rx_opts.append('--file')
		self.rx_opts.append(self.f_name_rx)
	
	def update_tx_opts(self):
		self.tx_opts = ['python', self.tx_mod_name, '-f']
		self.tx_opts.append(self.freq + self.freq_offset)
		self.tx_opts.append('--file')
		self.tx_opts.append(self.f_name_tx)
	
	def comb_misc_data(self):
		f_out = open("misc.dat", "w")
		f_1 = open("temp.dat", "r")
		f_2 = open("batt.dat", "r")
		f_3 = open("gps.dat", "r")
		
		f_out.write(f_1.readline())
		f_out.write(f_2.readline())
		f_out.write(f_3.readline())
		f_1.close()
		f_2.close()
		f_3.close()
		f_out.close
	
	def init_vars(self):
		#Initialize variables that define the "Go Home" state
		self.go_home()
		
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
		
		#Receive File
		self.f_name_rx = "RECEIVE"
		
		#Transmit File
		self.f_name_tx = "DATA"
		
		#Transceiver Variation
		self.freq_offset = 0
		
		#keep track of received erroneous data
		self.err_data = 0
		
		#RX, TX, and Time_Out pid's
		self.rx_pid = 0
		self.tx_pid = 0
		self.to_pid = 0
		
		#Receive File modification Time
		self.last_mod = time.localtime()
		
	def go_home(self):
		print "going home..."
		#Transceiver Frequency
		self.freq = 440000000
		
		#Modulation Scheme
		self.mod_sch = "dbpsk"
		
		#Set timeout
		self.timeout_t = 10
	
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
