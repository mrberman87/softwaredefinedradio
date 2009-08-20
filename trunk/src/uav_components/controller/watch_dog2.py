#!/usr/bin/env python

import os, time, ctypes
from deamon import *

class watch_dog2(Deamon):
	def run(self):
		libc = ctypes.CDLL('libc.so.6')
		libc.prctl(15, 'Watch_Dog_2', 0, 0, 0)
		while True:
			time.sleep(10)
			
			if not os.path.exists('/tmp/uav_controller.pid'):
				os.system('python /home/michael/softwaredefinedradio/src/uav_controller/controller/uav_controller.py start')
			
			if not os.path.exists('/tmp/watch_dog_1.pid'):
				os.system('python /home/michael/softwaredefinedradio/src/uav_controller/controller/watch_dog1.py start')


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
