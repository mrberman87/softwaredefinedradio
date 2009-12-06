import os
import signal
import time
import txrx_controller

class Transceiver():
	def __init__(self, controller, pid, fft_fn, mod_scheme, fft, toUAV, fromUAV):
		try:
			print 'Opening txrx_controller.'
			self.trans = txrx_controller.txrx_controller(fc=440e6, centoff=0, foffset_tx=100e3, foffset_rx=-50e3)
			print 'Opened controller.'
		except:
			print 'Could not open USRP, exiting...'
			#sys.exit(0)
		print 'Outside try block.'
		time.sleep(1)
		self.toUAV = toUAV
		self.fromUAV = fromUAV
		self.fft = fft
		self.fft_fn = fft_fn
		self.scheme = mod_scheme
		print 'Right before run_trans().'
		self.run_trans()


	def run_trans(self):
		print 'In definition run_trans.'
		if self.fft == 'True':
			print 'Transceiver: Transmitting FFT from previous command.'
			self.trans.transmit(self.fft_fn)
			controller.fft = 'False'
		while True:
			s = os.read(self.fromUAV,1024)
			s = s.split(':')
			print str(s)
			if s[0] == 'rx':
				print 'Transceiver: Waiting on receive'
				os.write(self.toUAV, str(self.trans.receive()))
			elif s[0] == 'close':
				print 'Transceiver: Closing queues for shutdown.'
				self.trans.close_queues()
			elif s[0] == 'set_frequency':
				time.sleep(1)
				print 'Transceiver: Changing Frequency.'
				self.trans.set_frequency(s[1])
			elif s[0] == 'set_timeout':
				print 'Transceiver: Changing timeout.'
				self.trans.set_frame_time_out(s[1])
			elif s[0] == ':':
				pass
			else:
				print 'Transceiver: Transmitting.'
				os.write(self.toUAV, str(self.trans.transmit(s[0])))
				print 'Transceiver: Done Transmitting.'
