#!/usr/bin/env python

from dummy_controller import txrx_controller
import time
import os
import signal
import sys
import wx
import threading

fromClient,toServer = os.pipe()
fromServer,toClient = os.pipe()

pid = os.fork()

if pid == 0:
	tb = txrx_controller(fc=440e6, centoff=11.19e3, foffset_tx=0, foffset_rx=50e3, version='bpsk')
	time.sleep(1)
	while True:
		s = os.read(fromClient,1024)
		if s == 'rx':
			os.write(toClient, str(tb.receive()))
		elif s == 'close':
			#tb.close_queues()
			pass
		else:
			os.write(toClient, str(tb.transmit(s)))
		
else:
	class MyApp(wx.App):
		def __init__(self, redirect=False, filename=None):
			wx.App.__init__(self, redirect, filename)

			self.frame = wx.Frame(None, wx.ID_ANY, size=(100,200))
			self.panel = wx.Panel(self.frame, wx.ID_ANY)

			self.button_press = buttons(self)
			self.button_press.start()

			b1 = wx.Button(self.panel, -1, 'Picture', (0,0))
			self.Bind(wx.EVT_BUTTON, self.button_press.OnButton1, b1)
			b2 = wx.Button(self.panel, -1, 'Spectrum', (0,35))
			self.Bind(wx.EVT_BUTTON, self.button_press.OnButton2, b2)
			b3 = wx.Button(self.panel, -1, 'Keep Alive', (0,70))
			self.Bind(wx.EVT_BUTTON, self.button_press.OnButton3, b3)
			b4 = wx.Button(self.panel, -1, 'Close', (0,105))
			self.Bind(wx.EVT_BUTTON, self.button_press.OnButton4, b4)
			
			self.frame.Show()

	class buttons(threading.Thread):
		def __init__(self, GUI):
			threading.Thread.__init__(self)
			self.GUI = GUI

		def OnButton1(self, evt):
			os.write(toServer, 'Image')
			temp = os.read(fromServer,1024)
			print str(temp)
			if temp == 'True':
				os.write(toServer, 'rx')
				temp = os.read(fromServer,1024)
			
		def OnButton2(self, evt):
			os.write(toServer, 'FFT')
			temp = os.read(fromServer,1024)
			print str(temp)
			if temp == 'True':
				os.write(toServer, 'rx')
				temp = os.read(fromServer,1024)

		def OnButton3(self, evt):
			os.write(toServer, 'ka')
			temp = os.read(fromServer,1024)
			print str(temp)
			#if temp == 'ka':
			#	print 'Link Alive'
			#else:
			#	print 'Keep Alive Failed.

		def OnButton4(self, evt):
			#os.write(toServer, 'close')
			#time.sleep(1)
			os.kill(pid, signal.SIGTERM)
			sys.exit(0)	
			

	

	time.sleep(1)	
	app = MyApp()
	app.MainLoop()

