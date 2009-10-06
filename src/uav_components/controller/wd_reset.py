import threading, time

class wd_reset(threading.Thread):
	def __init__(self, path, time):
		threading.Thread.__init__(self)
		self.path = path
		self.time = int(time)
	
	def run(self):
		while True:
			fd = open(self.path, 'w')
			fd.write('1')
			fd.close()
			time.sleep(self.time)
