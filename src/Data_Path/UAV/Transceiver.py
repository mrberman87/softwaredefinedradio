import os
import signal
import time
import txrx_controller

class Transceiver:
	def __init__(self, controller, pid, fft_fn, mod_scheme, fft, toUAV, fromUAV):
		try:
			tb = txrx_controller.txrx_controller(fc=440e6, centoff=0, foffset_tx=100e3, foffset_rx=-50e3)
			time.sleep(1.5)
		except:
			print 'Could not open USRP, exiting...'
			sys.exit(0)
		self.fft = fft
		self.fft_fn = fft_fn
		self.scheme = mod_scheme
		self.run_trans()


	def run_trans(self):
		print 'In definition run_trans.'
		if fft == True:
			print 'Transceiver: Transmitting FFT from previous command.'
			tb.transmit(self.fft_fn)
			controller.fft = False
		while True:
			s = os.read(fromUAV,1024)
			s = s.split(':')
			print str(s)
			if s[0] == 'rx':
				print 'Transceiver: Waiting on receive'
				os.write(toUAV, str(tb.receive()))
			elif s[0] == 'close':
				print 'Transceiver: Closing queues for shutdown.'
				tb.close_queues()
			elif s[0] == 'set_frequency':
				time.sleep(1)
				print 'Transceiver: Changing Frequency.'
				tb.set_frequency(s[1])
			elif s[0] == 'set_timeout':
				print 'Transceiver: Changing timeout.'
				tb.set_frame_time_out(s[1])
			elif s[0] == ':':
				pass
			else:
				print 'Transceiver: Transmitting.'
				os.write(toUAV, str(tb.transmit(s[0])))
				print 'Transceiver: Done Transmitting.'
