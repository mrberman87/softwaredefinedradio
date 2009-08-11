#!/usr/bin/env python

#Ground_Station.py

import wx
import ground_controls

class View(wx.Frame):
	def __init__(self,parent,controller):
		wx.Frame.__init__(self,parent, -1, 'Ground Control',size=(1000,700))
		
		self.controller = controller
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
		"""Creates a button, binds it to the given event handler, and returns
		the button"""
		button = wx.Button(parent, -1, label)
		self.Bind(wx.EVT_BUTTON, handler, button)
		return button
		
		
	def makeParamGrid(self,parent):
		"""parameter grid provides controls to the user to change
		Frequency, Modulation scheme, and timeout length"""
		param_grid= wx.GridSizer(3,2,2,2)
		param_grid.Add(wx.StaticText(parent,-1,'New Frequency'),wx.RIGHT,20)
		param_grid.Add(wx.TextCtrl(parent,-1),wx.EXPAND|wx.ALL,20)
		param_grid.Add(wx.StaticText(parent,-1,'New Modulation'),wx.RIGHT,20)
		self.modChoices = wx.Choice(parent,-1,choices=['BPSK','QPSK','8PSK'])
		self.Bind(wx.EVT_CHOICE, self.controller.onModSelect, self.modChoices)
		param_grid.Add(self.modChoices, wx.EXPAND|wx.ALL,20)
		param_grid.Add(wx.StaticText(parent,-1,'New Timeout'),wx.RIGHT,20)
		param_grid.Add(wx.TextCtrl(parent,-1),wx.EXPAND|wx.ALL,20)
		return param_grid
		
		
	def makeUAVGrid(self, parent):
		'''Contains buttons for the UAV Interrogation controls. builds and
		binds the buttons to the parent given, then returns the gridsizer 
		with buttons.'''
		uav_grid= wx.GridSizer(3,2,2,2)
		uav_grid.Add(self.buildOneButton(parent, 'Get Image', self.controller.onImageClicked))
		uav_grid.Add(self.buildOneButton(parent, 'Get GPS', self.controller.onGPSClicked))
		uav_grid.Add(self.buildOneButton(parent, 'Get FFT', self.controller.onFFTClicked))
		uav_grid.Add(self.buildOneButton(parent, 'Get Batt.', self.controller.onBattClicked))
		uav_grid.Add(self.buildOneButton(parent, 'Get Temp.', self.controller.onTempClicked))
		uav_grid.Add(self.buildOneButton(parent, 'Get All', self.controller.onAllClicked))
		return uav_grid
		
		
	def makeParamDataPanel(self,parent):
		"""Provides user with controls and views to the paramaters being
		used to communicate with the UAV as well as the Commands waiting
		to be executed."""
		param_data_panel = wx.Panel(parent,-1)
		param_data_panel.SetBackgroundColour("Purple")
		param_border = wx.StaticBox(param_data_panel, -1, 'Parameter Update')
		param_sizer = wx.StaticBoxSizer(param_border,orient=wx.HORIZONTAL)
		param_grid = self.makeParamGrid(parent = param_data_panel)
		param_sizer.Add(param_grid,1,wx.EXPAND)

		cmd_border= wx.StaticBox(param_data_panel, -1, 'Command Queue')
		cmd_queue_sizer = wx.StaticBoxSizer(cmd_border,orient=wx.HORIZONTAL)
		p_txt = wx.TextCtrl(param_data_panel, -1, style=wx.TE_MULTILINE)
		cmd_queue_sizer.Add(p_txt,1,wx.EXPAND)

		hbox2 =wx.BoxSizer(wx.HORIZONTAL)
		hbox2.Add(param_sizer,1,wx.EXPAND)
		hbox2.Add(cmd_queue_sizer,1,wx.EXPAND)
		
		param_data_panel.SetSizer(hbox2)
		return param_data_panel
		
		
		
	def makeCmdPanel(self,parent):
		"""CmdPanel in the upper left corner that has buttons for UAV
		controls as well as the Raw Data Viewer"""
		cmd_panel =wx.Panel(parent,-1)
		cmd_panel.SetBackgroundColour("Orange")
		uav_grid = self.makeUAVGrid(cmd_panel)
		
		uav_border = wx.StaticBox(cmd_panel, -1, 'UAV Commands')
		uav_sizer =  wx.StaticBoxSizer(uav_border,orient=wx.HORIZONTAL)
		uav_sizer.Add(uav_grid,1,wx.EXPAND)
		
		dv_border = wx.StaticBox(cmd_panel, -1, 'Data Viewer')
		data_view_sizer =  wx.StaticBoxSizer(dv_border, orient=wx.HORIZONTAL)
		dv_txt = wx.TextCtrl(cmd_panel, -1, style=wx.TE_MULTILINE)
		data_view_sizer.Add(dv_txt,1,wx.EXPAND)

		hbox1 = wx.BoxSizer(wx.HORIZONTAL)
		hbox1.Add(uav_sizer,1,wx.EXPAND)
		hbox1.Add(data_view_sizer,1,wx.EXPAND)
		cmd_panel.SetSizer(hbox1)
		return cmd_panel
	
	
	def makeFFTPanel(self, parent):
		"""panel where FFT will reside"""
		fft_panel = wx.Panel(parent,-1)
		fft_panel.SetBackgroundColour("Yellow")
		return fft_panel
		
	
	def makeRightPanel(self, parent):
	 	"""right panel holds the image, and current data viewer"""
		rightPanel = wx.Panel(parent,-1)
		rightPanel.SetBackgroundColour("Blue")
		img_border = wx.StaticBox(rightPanel, -1, 'Image Viewer')
		sizer2 = wx.StaticBoxSizer(img_border, orient=wx.VERTICAL)
		
		
		"""Make current data grid sizer and add to this panel"""
		cdv_border = wx.StaticBox(rightPanel, -1, 'Current Data Viewer')
		sizer2a = wx.StaticBoxSizer(cdv_border, orient=wx.VERTICAL)
		data_grid= wx.GridSizer(5,4,2,2)
		
		txtLabels = ['LAT', 'LONG', 'ALT', 'TEMP', 'BATT',
					'SIG POWER','FREQ','MOD', 'TIMEOUT', 'GND SPEED']
		txtBoxNames = ['lat', 'long','alt','temp','batt',
						'sigPower','freq','mod','timeout', 'gndSpeed']
						
		"""add text boxes and labels to data grid. Text boxes can be
		referenced by name. ex: latTextBox would be the name to reference
		for controlling the latitude TextCntrl"""

		for i in range(len(txtLabels)):
			label = txtLabels[i]
			boxName = txtBoxNames[i] + "TextBox"
			data_grid.Add(wx.StaticText(rightPanel,-1,label),wx.RIGHT,20)
			myTxtCtrl = wx.TextCtrl(rightPanel,-1, name = boxName)		
			data_grid.Add(myTxtCtrl,wx.EXPAND|wx.ALL,20)
		
		sizer2a.Add(data_grid,1,wx.EXPAND)
		
		vbox1 = wx.BoxSizer(wx.VERTICAL)
		vbox1.Add(sizer2,1,wx.EXPAND)
		vbox1.Add(sizer2a,1,wx.EXPAND)
		rightPanel.SetSizer(vbox1)
		return rightPanel


	def makeLeftPanel(self, parent):
		"""Left panel contains all the control elements in the GUI."""
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
		

		
		
class Controller(wx.App):
	def __init__(self):
		wx.App.__init__(self,redirect=False)
		
		
	"""on____ methods are event handlers, which are called whenever a button
	is clicked in the GUI."""
		
	def OnInit(self):
		"""Controller instance creates a View (GUI) and model
		(ground_controls) and acts as a mediator between them"""
		
		self.view = View(parent = None, controller = self)
		self.view.Show(True)
		self.model = ground_controls.ground_controls()
		
		#add listeners to model that are responsible for updating the view
		self.model.addListener(self.imageListener)
		self.model.addListener(self.modSchemeListener)
		return True
		
	def onModSelect(self, event):
		newMod = self.view.modChoices.GetStringSelection()
		self.model.changeModScheme(newMod)
		self.model.update()
		pass
	
	def onImageClicked(self, event):
		print "image Clicked"
		self.model.countImageClicks()
		
	def onGPSClicked(self, event):
		pass
	
	def onSettingsChange(self, event):
		pass
	
	def onTimeOut(self, event):
		pass
	
	def onFFTClicked(self, event):
		pass
	
	def onBattClicked(self, event):
		pass
	
	def onTempClicked(self, event):
		pass
	
	def onAllClicked(self, event):
		pass
		
	"""______Listener methods update data in the view. They are all ran 
	whenever the model (ground_controls.py) calls the it's update() method.
	The model should call update whenever data in the model has changed."""

	def imageListener(self):
		pass
				
	def frequencyListener(self):
		pass
		
	def modSchemeListener(self):
		"""Set the text box for modulation scheme to the same value as the
		model."""
		modTextBox = self.view.FindWindowByName("modTextBox")
		modTextBox.SetValue(self.model.modulation)
		
if __name__ =="__main__":
	app = Controller()
	app.MainLoop()
	
	