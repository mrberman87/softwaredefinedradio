#!/usr/bin/env python

import os, time, ctypes
from daemon import *
from wd_reset import *

class watch_dog2(Daemon):
	def run(self):
		libc = ctypes.CDLL('libc.so.6')
		libc.prctl(15, 'Watch_Dog_2', 0, 0, 0)
		time.sleep(2)
		wd = wd_reset('/uav/daemon_pids/wd2_wd1.wd', 5).start()
		while True:
			time.sleep(7)
			
			if self.pid_exists('/uav/daemon_pids/uav_controller.pid'):
				os.system('python /uav/uav_controller.py start')
			
			if not self.check_file('/uav/daemon_pids/wd2_controller.wd'):
				os.system('python /uav/uav_controller.py restart')
			
			if self.pid_exists('/uav/daemon_pids/watch_dog_1.pid') is False:
				os.system('python /uav/watch_dog1.py start')
			
			if self.check_file('/uav/daemon_pids/wd1_wd2.wd') is False:
				os.system('python /uav/watch_dog1.py restart')
	
	def pid_exists(self, path):
		if not os.path.exists(path):
			return False
		try:
			fd = open(path, 'r')
			pid = fd.readline().strip('\n').strip()
			fd.close()
			if os.path.exists('/proc/%s/status' % pid):
				return True
			return False
		except IOError, OSError:
			return False
	
	def check_file(self, path):
		try:
			fd1 = open(path, 'r')
			check = fd1.readline().strip('\n').strip()
			fd1.close()
			fd = open(path, 'w')
			fd.write('0')
			fd.close()
			if check == '1':
				return True
			return False
		except IOError:
			return False

if __name__ == '__main__':
	daemon = watch_dog2(pidfile='/uav/daemon_pids/watch_dog_2.pid')
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
