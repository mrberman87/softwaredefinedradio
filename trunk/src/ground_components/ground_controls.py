#!/usr/bin/env python

"""
ground_controls.py is the Model in the MVC architecture. It stores the application
specific (in this case a ground station) data and logic. The data stored includes
GPS data, modulation scheme, image, and other telemetry data. This provides 
various functions to request data from the UAV.
"""
import os
import abstractmodel
import sys
sys.path.append("GPS") #includes GPS/ directory to use GPS_packet.py
from GPS_packet import GPS_packet

class ground_controls(abstractmodel.AbstractModel):
	def __init__(self):
		abstractmodel.AbstractModel.__init__(self)
		self.gps = GPS_packet("GPSD,P=0 0,A=0,V=0,E=0")
		self.temp = 0
		self.batt = 0
		self.freq = 0
		self.modulation = None
		self.timeout = 10 #(in seconds)
		self.sigPower = 0
		self.imageClickedTimes = 0 #test var to test relaying information to view
	
	def countImageClicks(self):
		self.imageClickedTimes = self.imageClickedTimes + 1
		self.update()
	
	def changeModScheme(self, mod):
		self.modulation = mod
		self.update()

	"""
	Each of these functions are going to kill the receiver, run the transmitter,
	then restart the reciever, and return the new reciever's pid.
	"""
	
	def get_pic(self, freq, mod_sch, rx_pid):
		tx_file(rx_pid, "picture")
		run_tx(freq, mod_sch)
		return run_rx()
	
	def get_fft(self, freq, mod_sch, rx_pid):
		tx_file(rx_pid, "fft")
		run_tx(freq, mod_sch)
		return run_rx()
	
	def get_sensors(self, freq, mod_sch, rx_pid):
		tx_file(rx_pid, "sensors")
		run_tx(freq, mod_sch)
		return run_rx()
	
	def set_vars(self, freq, mod_sch, rx_pid, new_freq, new_mod_sch, new_timeout):
		tx_file(rx_pid, "settings\n%s\n%s\n%s" % new_freq, new_mod_sch, new_timeout)
		run_tx(freq, mod_sch)
		return run_rx()
	
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
	
	def tx_file(self, rx_pid, command):
		kill_pid(rx_pid)
		try:
			_file = open("transmit.txt", "w")
		except IOError:
			os.system("touch transmit.txt")
			_file = open("transmit.txt", "w")
		_file.write("%s" % command)
		_file.close()
	
	def run_tx(self, freq, mod_sch):
		if(mod_sch == "bpsk"):
			os.spawnl(os.P_WAIT, '/usr/bin/python', 'python', "./bpsk_tx.py", "-f", "%d" % freq)
		elif(mod_sch == "qpsk"):
			os.spawnl(os.P_WAIT, '/usr/bin/python', 'python', "./qpsk_tx.py", "-f", "%d" % freq)
		elif(mod_sch == "8psk"):
			os.spawnl(os.P_WAIT, '/usr/bin/python', 'python', "./8psk_tx.py", "-f", "%d" % freq)
	
	def run_rx(self):
		if(mod_sch == "bpsk"):
			return os.spawnl(os.P_NOWAIT, '/usr/bin/python', 'python', "./bpsk_rx.py", "-f", "%d" % freq)
		elif(mod_sch == "qpsk"):
			return os.spawnl(os.P_NOWAIT, '/usr/bin/python', 'python', "./qpsk_rx.py", "-f", "%d" % freq)
		elif(mod_sch == "8psk"):
			return os.spawnl(os.P_NOWAIT, '/usr/bin/python', 'python', "./8psk_rx.py", "-f", "%d" % freq)

