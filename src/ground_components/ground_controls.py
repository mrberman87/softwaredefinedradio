#!/usr/bin/env python

"""
Each of these are going to kill the receiver, run the transmitter,
then restart the reciever, and return the new reciever's pid.
"""

import os
import abstractmodel
import sys
sys.path.append("GPS")
from GPS_packet import GPS_packet

class ground_controls(abstractmodel.AbstractModel):
	def __init__(self):
		self.gps = GPS_packet.GPS_packet("")	
	
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

