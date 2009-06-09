#!usr/lib/python

#Ground_Station.py

import wx



class View(wx.Frame):
	def __init__(self,parent):
		wx.Frame.__init__(self,parent, -1, 'Ground Control',size=(1000,700))
		
		
		
		hbox_top=wx.BoxSizer(wx.HORIZONTAL)
		panel= wx.Panel(self,-1)
		panel.SetBackgroundColour("#000000")
		
		panel1= wx.Panel(panel,-1)
		panel1.SetBackgroundColour("#BFBFBF")
		panel2= wx.Panel(panel,-1)
		panel2.SetBackgroundColour("#BFBFBF")
		hbox_top.Add(panel1,1,wx.EXPAND|wx.ALL, 10)
		hbox_top.Add(panel2,1,wx.EXPAND|wx.ALL,10)
		
		#panel1
		vbox =wx.BoxSizer(wx.VERTICAL)
		panel1_1 =wx.Panel(panel,-1)
		panel1_1.SetBackgroundColour("#BFBFBF")
		panel1_2 = wx.Panel(panel,-1)
		panel1_2.SetBackgroundColour("#BFBFBF")
		panel1_3 = wx.Panel(panel,-1)
		panel1_3.SetBackgroundColour("#BFBFBF")
		vbox.Add(panel1_1,1,wx.EXPAND|wx.LEFT|wx.TOP|wx.BOTTOM, 20)
		vbox.Add(panel1_2,1,wx.EXPAND|wx.LEFT|wx.BOTTOM, 20)
		vbox.Add(panel1_3,1,wx.EXPAND|wx.LEFT, 20)
		panel1.SetSizer(vbox)
		
		#panel2
		sizer2 = wx.StaticBoxSizer(wx.StaticBox(panel2, -1, 'Image Viewer'), orient=wx.VERTICAL)
		panel2.SetSizer(sizer2)
		
		#panel1_1
		hbox1 =wx.BoxSizer(wx.HORIZONTAL)
		sizer3=  wx.StaticBoxSizer(wx.StaticBox(panel1_1, -1, 'UAV Commands'),orient=wx.HORIZONTAL)
		sizer4=  wx.StaticBoxSizer(wx.StaticBox(panel1_1, -1, 'Data Viewer'),orient=wx.HORIZONTAL)
		uav_grid= wx.GridSizer(3,2,2,2)
		uav_grid.Add(wx.Button(panel1_1, -1, 'Get Image'))
		uav_grid.Add(wx.Button(panel1_1, -1, 'Get GPS'))
		uav_grid.Add(wx.Button(panel1_1, -1, 'Get FFT'))
		uav_grid.Add(wx.Button(panel1_1, -1, 'Get Batt.'))
		uav_grid.Add(wx.Button(panel1_1, -1, 'Get Temp.'))
		uav_grid.Add(wx.Button(panel1_1, -1, 'Get All'))
		sizer3.Add(uav_grid,1,wx.EXPAND)
		sizer4.Add(wx.TextCtrl(panel1_1, -1, style=wx.TE_MULTILINE),1,wx.EXPAND)
		hbox1.Add(sizer3,1,wx.EXPAND)
		hbox1.Add(sizer4,1,wx.EXPAND)
		panel1_1.SetSizer(hbox1)
		
		#panel1_2
		hbox2 =wx.BoxSizer(wx.HORIZONTAL)
		sizer5=  wx.StaticBoxSizer(wx.StaticBox(panel1_2, -1, 'Parameter Update'),orient=wx.HORIZONTAL)
		sizer6=  wx.StaticBoxSizer(wx.StaticBox(panel1_2, -1, 'Command Queue'),orient=wx.HORIZONTAL)
		param_grid= wx.GridSizer(3,2,2,2)
		param_grid.Add(wx.StaticText(panel1_2,-1,'New Frequency'),wx.RIGHT,20)
		param_grid.Add(wx.TextCtrl(panel1_2,-1),wx.EXPAND|wx.ALL,20)
		param_grid.Add(wx.StaticText(panel1_2,-1,'New Modulation'),wx.RIGHT,20)
		param_grid.Add(wx.Choice(panel1_2,-1,choices=['BPSK','QPSK','8PSK']),wx.EXPAND|wx.ALL,20)
		param_grid.Add(wx.StaticText(panel1_2,-1,'New Timeout'),wx.RIGHT,20)
		param_grid.Add(wx.TextCtrl(panel1_2,-1),wx.EXPAND|wx.ALL,20)
		sizer5.Add(param_grid,1,wx.EXPAND)
		sizer6.Add(wx.TextCtrl(panel1_2, -1, style=wx.TE_MULTILINE),1,wx.EXPAND)
		hbox2.Add(sizer5,1,wx.EXPAND)
		hbox2.Add(sizer6,1,wx.EXPAND)
		panel1_2.SetSizer(hbox2)
		
		#panel1_3
		
		panel.SetSizer(hbox_top)
class Controller:
	def __init__(self, app):
		self.view = View(None)
		self.view.Show(True)
	
if __name__ =="__main__":
	app= wx.App()
	Controller(app)
	app.MainLoop()
	
	
