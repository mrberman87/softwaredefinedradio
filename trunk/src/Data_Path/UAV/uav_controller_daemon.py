#!/usr/bin/env python

import time
import os
import sys
import signal
import UAV
import Transceiver
from daemon import *

fromUAV,toTransceiver = os.pipe()
fromTransceiver,toUAV = os.pipe()

class controller(Daemon):
	def __init__(self):
		#set priority
		os.system("renice 0 %d" % os.getpid())
		#changing the system name of this program when it's running
		libc = ctypes.CDLL('libc.so.6')
		libc.prctl(15, 'UAV Controller', 0, 0, 0)
		#starting threads to reset the watchdog timers
		self.wd1 = wd_reset('/uav/daemon_pids/wd1_controller.wd', 5).start()
		self.wd2 = wd_reset('/uav/daemon_pids/wd2_controller.wd', 5).start()
		self.fft_fn = '/fft.png'
		self.mod_scheme = 'bpsk'
		self.fft= 'False'
		self.pid = os.fork()
		print 'pid : ', self.pid
		self.run()

	def forkit(self):
		self.pid = os.fork()
		self.run()

	def run(self):
		if self.pid == 0:
			try:
				self.t = Transceiver.Transceiver(self, self.pid, self.fft_fn, self.mod_scheme, self.fft, toUAV, fromUAV)
			except:
				print 'Unable to open USRP, closing process : ', str(self.pid)
				os.write(toUAV, 'closing')
				sys.exit(0)
		
		else:
			try:
				self.u = UAV.UAV(self, toTransceiver, fromTransceiver)
			except:
				print 'Exception in UAV.'
				os.write(toTransceiver, 'close:')
				time.sleep(1)
				os.kill(self.pid, signal.SIGTERM)
				sys.exit(0)

if __name__ == '__main__':
	#for running as a stand along within a shell
	#uav_controller().run()
	#this sets up this controller as a daemon to run in the background
	daemon = controller('/uav/daemon_pids/uav_controller.pid')
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
