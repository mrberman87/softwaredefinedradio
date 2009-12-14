#!/usr/bin/env python

import os, time, ctypes
from daemon import *
from wd_reset import *

class watch_dog1(Daemon):
	def run(self):
		self.working_dir = os.getcwd()
		libc = ctypes.CDLL('libc.so.6')
		libc.prctl(15, 'Watch_Dog_1', 0, 0, 0)
		time.sleep(2)
		wd = wd_reset(self.working_dir + '/daemon_pids/wd1_wd2.wd', 5).start()
		while True:
			time.sleep(7)
			
			if self.pid_exists(self.working_dir + '/daemon_pids/uav_controller.pid'):
				os.system('python %s/uav_controller.py start'%self.working_dir)
			
			if not self.check_file(self.working_dir + '/daemon_pids/wd1_controller.wd'):
				os.system('python %s/uav_controller.py restart'%self.working_dir)
			
			if self.pid_exists(self.working_dir + '/daemon_pids/watch_dog_2.pid') is False:
				os.system('python %s/watch_dog2.py start'%self.working_dir)
			
			if self.check_file(self.working_dir + '/daemon_pids/wd2_wd1.wd') is False:
				os.system('python %s/watch_dog2.py restart'%self.working_dir)
	
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
	daemon = watch_dog1(pidfile=self.working_dir + '/daemon_pids/watch_dog_1.pid')
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
