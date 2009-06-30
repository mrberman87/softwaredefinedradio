#!/usr/bin/env python

#Ground_Station.py

import wx

class View(wx.Frame):
	def __init__(self,parent):
		wx.Frame.__init__(self,parent, -1, 'Ground Control',size=(1000,700))
		
		#main panel, where everything else lays on
		panel = wx.Panel(self,-1) 
		panel.SetBackgroundColour("Green")
		
		#left panel (command and data viewers go here)
		leftPanel = self.makeLeftPanel(parent = panel)
		
		#right panel (image view goes here)
		rightPanel = self.makeRightPanel(parent = panel)
		
		#add left and right panel to a sizer and put sizer on main panel
		hbox_top=wx.BoxSizer(wx.HORIZONTAL)
		hbox_top.Add(leftPanel,1,wx.EXPAND|wx.ALL, 10)
		hbox_top.Add(rightPanel,1,wx.EXPAND|wx.ALL,10)
		panel.SetSizer(hbox_top)


	def buildOneButton(self, parent, label, handler):
		button = wx.Button(parent, -1, label)
		self.Bind(wx.EVT_BUTTON, handler, button)
		return button
		
		
	def makeParamGrid(self,parent):
		param_grid= wx.GridSizer(3,2,2,2)
		param_grid.Add(wx.StaticText(parent,-1,'New Frequency'),wx.RIGHT,20)
		param_grid.Add(wx.TextCtrl(parent,-1),wx.EXPAND|wx.ALL,20)
		param_grid.Add(wx.StaticText(parent,-1,'New Modulation'),wx.RIGHT,20)
		param_grid.Add(wx.Choice(parent,-1,choices=['BPSK','QPSK','8PSK']),wx.EXPAND|wx.ALL,20)
		param_grid.Add(wx.StaticText(parent,-1,'New Timeout'),wx.RIGHT,20)
		param_grid.Add(wx.TextCtrl(parent,-1),wx.EXPAND|wx.ALL,20)
		return param_grid
		
		
	def makeUAVGrid(self, parent):
		'''Contains buttons for some UAV controls'''
		uav_grid= wx.GridSizer(3,2,2,2)
		uav_grid.Add(self.buildOneButton(parent,'Get Image',self.onImageButtonClicked))
		uav_grid.Add(wx.Button(parent, -1, 'Get GPS'))
		uav_grid.Add(wx.Button(parent, -1, 'Get FFT'))
		uav_grid.Add(wx.Button(parent, -1, 'Get Batt.'))
		uav_grid.Add(wx.Button(parent, -1, 'Get Temp.'))
		uav_grid.Add(wx.Button(parent, -1, 'Get All'))
		return uav_grid
		
		
	def makeParamDataPanel(self,parent):
		param_data_panel = wx.Panel(parent,-1)
		param_data_panel.SetBackgroundColour("Purple")
		param_sizer = wx.StaticBoxSizer(wx.StaticBox(param_data_panel, -1, 'Parameter Update'),orient=wx.HORIZONTAL)
		param_grid = self.makeParamGrid(parent = param_data_panel)
		param_sizer.Add(param_grid,1,wx.EXPAND)

		cmd_queue_sizer =  wx.StaticBoxSizer(wx.StaticBox(param_data_panel, -1, 'Command Queue'),orient=wx.HORIZONTAL)
		cmd_queue_sizer.Add(wx.TextCtrl(param_data_panel, -1, style=wx.TE_MULTILINE),1,wx.EXPAND)

		hbox2 =wx.BoxSizer(wx.HORIZONTAL)
		hbox2.Add(param_sizer,1,wx.EXPAND)
		hbox2.Add(cmd_queue_sizer,1,wx.EXPAND)
		
		param_data_panel.SetSizer(hbox2)
		return param_data_panel
		
		
		
	def makeCmdPanel(self,parent):
		cmd_panel =wx.Panel(parent,-1)
		cmd_panel.SetBackgroundColour("Orange")
		uav_grid = self.makeUAVGrid(cmd_panel)
		
		uav_sizer =  wx.StaticBoxSizer(wx.StaticBox(cmd_panel, -1, 'UAV Commands'),orient=wx.HORIZONTAL)
		uav_sizer.Add(uav_grid,1,wx.EXPAND)
		
		data_view_sizer =  wx.StaticBoxSizer(wx.StaticBox(cmd_panel, -1, 'Data Viewer'),orient=wx.HORIZONTAL)
		data_view_sizer.Add(wx.TextCtrl(cmd_panel, -1, style=wx.TE_MULTILINE),1,wx.EXPAND)

		hbox1 = wx.BoxSizer(wx.HORIZONTAL)
		hbox1.Add(uav_sizer,1,wx.EXPAND)
		hbox1.Add(data_view_sizer,1,wx.EXPAND)
		cmd_panel.SetSizer(hbox1)
		return cmd_panel
	
	
	def makeFFTPanel(self, parent):
		fft_panel = wx.Panel(parent,-1)
		fft_panel.SetBackgroundColour("Yellow")
		return fft_panel
		
	
	def makeRightPanel(self, parent):
	 	'''right panel holds the image'''
		rightPanel = wx.Panel(parent,-1)
		rightPanel.SetBackgroundColour("Blue")
		sizer2 = wx.StaticBoxSizer(wx.StaticBox(rightPanel, -1, 'Image Viewer'), orient=wx.VERTICAL)
		rightPanel.SetSizer(sizer2)
		return rightPanel


	def makeLeftPanel(self, parent):
		leftPanel = wx.Panel(parent,-1)
		leftPanel.SetBackgroundColour("Red")		
		cmd_panel = self.makeCmdPanel(parent = parent)
		param_data_panel = self.makeParamDataPanel(parent = parent)
		fft_panel = self.makeFFTPanel(parent = parent)

		vbox = wx.BoxSizer(wx.VERTICAL)
		vbox.Add(cmd_panel,1,wx.EXPAND|wx.LEFT|wx.TOP|wx.BOTTOM, 20)
		vbox.Add(param_data_panel,1,wx.EXPAND|wx.LEFT|wx.BOTTOM, 20)
		vbox.Add(fft_panel,1,wx.EXPAND|wx.LEFT, 20)
		
		leftPanel.SetSizer(vbox)
		return leftPanel
		
	def onImageButtonClicked(self):
		pass	
		
		
class Controller(wx.App):
	def __init__(self):
		wx.App.__init__(self)
		self.view = View(None)
		self.view.Show(True)
	
if __name__ =="__main__":
	app = Controller()
	app.MainLoop()
	
	
