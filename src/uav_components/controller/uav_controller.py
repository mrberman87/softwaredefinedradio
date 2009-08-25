#!/usr/bin/env python

import os, time, ctypes
from controls import *
from deamon import *
from txrx_controller import *

class uav_controller(Deamon):
	def run(self):
		#set priority
		os.system("renice 0 %d" % os.getpid())
		libc = ctypes.CDLL('libc.so.6')
		libc.prctl(15, 'UAV Controller', 0, 0, 0)
		self.trans = txrx_controller()
		self.controls = controls()
		tmp = False
		
		#This is the main controller section of code
		while True:
			while tmp is False:
				
			
			if controls.exec_command(self.command):
				self.trans.transmit(controls.f_name_tx)
				self.trans.receive()

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
