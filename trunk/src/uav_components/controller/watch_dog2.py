#!/usr/bin/env python

import os, time, ctypes
from deamon import *

class watch_dog2(Deamon):
	def run(self):
		libc = ctypes.CDLL('libc.so.6')
		libc.prctl(15, 'Watch_Dog_2', 0, 0, 0)
		while True:
			time.sleep(11)
			
			if self.pid_exists('/uav/daemon_pids/uav_controller.pid'):
				os.system('python /uav/uav_controller.py start')
			
			if self.pid_exists('/uav/daemon_pids/watch_dog_1.pid'):
				os.system('python /uav/watch_dog2.py start')
	
	def pid_exists(self, path):
		if not os.path.exists(path):
			return False
		try:
			fd = open(path, 'r')
			pid = fd.readline().strip('\n').strip()
			fd.close()
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

if __name__ == '__main__':
	daemon = uav_controller('/uav/daemon_pids/watch_dog_2.pid')
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
