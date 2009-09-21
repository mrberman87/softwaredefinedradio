import threading, time

class wd_reset(threading.Thread):
	def __init__(self, path):
		threading.Thread.__init__(self)
		self.path = path
	
	def run(self):
		while True:
			fd = open(self.path, 'w')
			fd.write('1')
			fd.close()
			time.sleep(5)
