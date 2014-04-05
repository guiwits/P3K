#!/usr/bin/python

import wx
import threading
import time
import wx.lib.newevent
import Queue
import AcquisitionCameraUI
import FlatMap
import MotionControl
import HwfpParametersUI
import PlotTool
import Status
import WFSCameraUI
import Telemetry
from socket import *

ABOUT_TEXT = """Palomar Adaptive Optics Graphical User Interface \n\nVersion ALPHA Something or other"""

class MyFrame1(wx.Frame):
    def __init__(self, *args, **kwds):
        kwds["style"] = wx.CAPTION|wx.CLOSE_BOX|wx.MINIMIZE_BOX|wx.SYSTEM_MENU
        wx.Frame.__init__(self, *args, **kwds)
        
	# Timer for data and time display
	self.timer1 = wx.Timer(self)
	self.timer2 = wx.Timer(self)
	
	# interval = 60000ms (60 seconds)
	# default is oneShot=False, timer keeps restarting
	# stop the timer action with self.timer.Stop()
	self.timer1.Start(1000, oneShot=False)
	self.timer2.Start(60000, oneShot=False)
	
	#
	# bind EVT_TIMER event to self.OnTimerX() action
	#
	self.Bind(wx.EVT_TIMER, self.OnTimer1, self.timer1)
	self.Bind(wx.EVT_TIMER, self.OnTimer2, self.timer2)

        # Menu Bar
        self.menubar = wx.MenuBar()
        fileMenu = wx.Menu()
        fileMenu.Append(wx.NewId(), "&Open", "Open a configuration file", wx.ITEM_NORMAL)
        fileMenu.Append(wx.NewId(), "&Save", "Save a configuration file", wx.ITEM_NORMAL)
        fileMenu.AppendSeparator()
        fileMenu.Append(wx.NewId(), "&Quit\tCtrl+Q", "Quit Palomar AO Control", wx.ITEM_NORMAL)
        self.menubar.Append(fileMenu, "&File")

        #editMenu = wx.Menu()
	plotMenu = wx.Menu()
	plotMenu.Append (wx.NewId(), "TTM Pos", "Plot TTM Positions", wx.ITEM_NORMAL)
	plotMenu.Append (wx.NewId(), "TTM Res", "Plot TTM Residuals", wx.ITEM_NORMAL)
	plotMenu.Append (wx.NewId(), "DM Pos", "Plot DM Positions", wx.ITEM_NORMAL)
	plotMenu.Append (wx.NewId(), "DM Res", "Plot DM Residuals", wx.ITEM_NORMAL)
	plotMenu.Append (wx.NewId(), "WFS Flux", "Plot WFS Flux", wx.ITEM_NORMAL)
	self.menubar.Append(plotMenu, "&Plot")
	helpMenu = wx.Menu()
        #self.menubar.Append(editMenu, "&Edit")
	#self.plotTTM = wx.MenuItem (plotMenu, wx.NewId(), "TTM Pos", "Plot TTM Positions", wx.ITEM_NORMAL)
	#plotMenu.AppendItem(self.plotTTM)
        self.About = wx.MenuItem(helpMenu, wx.NewId(), "About", "About Palomar 3000 User Interface", wx.ITEM_NORMAL)
        helpMenu.AppendItem(self.About)
        self.menubar.Append(helpMenu, "&Help")
        self.SetMenuBar(self.menubar)
        # Menu Bar end

        self.frame_2_statusbar = self.CreateStatusBar(1, 0)
        self.label_11 = wx.StaticText(self, -1, "     PALM 3000")
        self.text_ctrl_5 = wx.TextCtrl(self, -1, "")
        self.label_12 = wx.StaticText(self, -1, "Date:")
        self.text_ctrl_6 = wx.TextCtrl(self, -1, "")
        self.label_13 = wx.StaticText(self, -1, "Time:")
        self.text_ctrl_7 = wx.TextCtrl(self, -1, "")
        self.static_line_2 = wx.StaticLine(self, -1, style=wx.LI_VERTICAL)
        self.label_1 = wx.StaticText(self, -1, "P3K Loop Control", style=wx.ALIGN_CENTRE)
        self.button_1 = wx.ToggleButton(self, -1, "TTM", pos=(-1, -1), size=(80, 35))
        self.button_2 = wx.ToggleButton(self, -1, "HODM", pos=(-1, -1), size=(80, 35))
        self.button_3 = wx.ToggleButton(self, -1, "MODE", pos=(-1, -1), size=(80, 35))
        self.label_2 = wx.StaticText(self, -1, "  Automations Running:")
        self.text_ctrl_4 = wx.TextCtrl(self, -1, "")
        self.static_line_3 = wx.StaticLine(self, -1, style=wx.LI_VERTICAL)
        self.checkbox_1 = wx.CheckBox(self, -1, "")
        self.label_3 = wx.StaticText(self, -1, "Acquisition", style=wx.ALIGN_CENTRE)
        self.checkbox_2 = wx.CheckBox(self, -1, "")
        self.label_4 = wx.StaticText(self, -1, "WFS Camera", style=wx.ALIGN_CENTRE)
        self.checkbox_3 = wx.CheckBox(self, -1, "")
        self.label_5 = wx.StaticText(self, -1, "Flatmap", style=wx.ALIGN_CENTRE)
        self.checkbox_4 = wx.CheckBox(self, -1, "")
        self.label_6 = wx.StaticText(self, -1, "Status", style=wx.ALIGN_CENTRE)
        self.checkbox_5 = wx.CheckBox(self, -1, "")
        self.label_7 = wx.StaticText(self, -1, "Motors", style=wx.ALIGN_CENTRE)
        self.checkbox_6 = wx.CheckBox(self, -1, "")
        self.label_8 = wx.StaticText(self, -1, "HWFP Parameters", style=wx.ALIGN_CENTRE)
        self.checkbox_7 = wx.CheckBox(self, -1, "")
        self.label_9 = wx.StaticText(self, -1, "Telemetry", style=wx.ALIGN_CENTRE)
        self.checkbox_8 = wx.CheckBox(self, -1, "")
        self.label_10 = wx.StaticText(self, -1, "Plot Tool", style=wx.ALIGN_CENTRE)
	self.label_12.SetLabel (time.strftime("Date: %Y-%m-%d", time.gmtime()))
	self.label_13.SetLabel (time.strftime("Time: %H:%M:%S", time.gmtime()))

        self.__set_properties()
        self.__do_layout()

	### Var to see if PlotTools is running since it requires ###
	### hand holding of external processes			 ###
	self.plotToolsRunning = False

        self.Bind(wx.EVT_MENU, self.OnMenuExit, id=-1)
        self.Bind(wx.EVT_MENU, self.OnAbout, self.About)
	self.Bind (wx.EVT_CLOSE, self.OnQuit)
	self.Bind (wx.EVT_TOGGLEBUTTON, self.OnTTM, self.button_1)
	self.Bind (wx.EVT_TOGGLEBUTTON, self.OnLODM, self.button_2)
	self.Bind (wx.EVT_TOGGLEBUTTON, self.OnHODM, self.button_3)
        self.Bind(wx.EVT_CHECKBOX, self.GoAcqCam, self.checkbox_1)
        self.Bind(wx.EVT_CHECKBOX, self.GoWfsCam, self.checkbox_2)
        self.Bind(wx.EVT_CHECKBOX, self.GoFlatMap, self.checkbox_3)
        self.Bind(wx.EVT_CHECKBOX, self.GoStatus, self.checkbox_4)
        self.Bind(wx.EVT_CHECKBOX, self.GoMotors, self.checkbox_5)
        self.Bind(wx.EVT_CHECKBOX, self.GoHwfpParameters, self.checkbox_6)
        self.Bind(wx.EVT_CHECKBOX, self.GoTelemetry, self.checkbox_7)
        self.Bind(wx.EVT_CHECKBOX, self.GoPlotTools, self.checkbox_8)
        # end wxGlade

    def __set_properties(self):
        # begin wxGlade: MyFrame1.__set_properties
        self.SetTitle("Palomar Adaptive Optics Control")
        #self.SetBackgroundColour(wx.Colour(236, 233, 216))
        self.frame_2_statusbar.SetStatusWidths([-1])
        # statusbar fields
        frame_2_statusbar_fields = [""]
        for i in range(len(frame_2_statusbar_fields)):
            self.frame_2_statusbar.SetStatusText(frame_2_statusbar_fields[i], i)
        self.text_ctrl_5.Hide()
        self.text_ctrl_6.Hide()
        self.text_ctrl_7.Hide()
#        self.button_1.SetBackgroundColour(wx.Colour(236, 233, 216))
        self.text_ctrl_4.SetMinSize((238, 45))
        self.text_ctrl_4.Enable(False)
# end wxGlade

    def __do_layout(self):
        # begin wxGlade: MyFrame1.__do_layout
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_2 = wx.FlexGridSizer(1, 5, 0, 0)
        grid_sizer_6 = wx.FlexGridSizer(8, 2, 0, 0)
        grid_sizer_4 = wx.GridSizer(4, 1, 0, 0)
        grid_sizer_5 = wx.FlexGridSizer(1, 3, 0, 0)
        grid_sizer_3 = wx.FlexGridSizer(6, 1, 0, 0)
        grid_sizer_3.Add(self.label_11, 0, wx.TOP, 15)
        grid_sizer_3.Add(self.text_ctrl_5, 0, 0, 0)
        grid_sizer_3.Add(self.label_12, 0, wx.TOP|wx.BOTTOM, 35)
        grid_sizer_3.Add(self.text_ctrl_6, 0, 0, 0)
        grid_sizer_3.Add(self.label_13, 0, wx.BOTTOM, 0)
        grid_sizer_3.Add(self.text_ctrl_7, 0, 0, 0)
        grid_sizer_2.Add(grid_sizer_3, 1, wx.LEFT|wx.EXPAND, 15)
        grid_sizer_2.Add(self.static_line_2, 2, wx.ALL|wx.EXPAND, 10)
        grid_sizer_4.Add(self.label_1, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_5.Add(self.button_1, 0, wx.LEFT|wx.RIGHT, 3)
        grid_sizer_5.Add(self.button_2, 0, wx.LEFT|wx.RIGHT, 3)
        grid_sizer_5.Add(self.button_3, 0, wx.LEFT|wx.RIGHT, 3)
        grid_sizer_4.Add(grid_sizer_5, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_4.Add(self.label_2, 0, wx.TOP|wx.ALIGN_BOTTOM, 15)
        grid_sizer_4.Add(self.text_ctrl_4, 0, wx.BOTTOM|wx.EXPAND, 2)
        grid_sizer_2.Add(grid_sizer_4, 1, wx.BOTTOM|wx.EXPAND, 10)
        grid_sizer_2.Add(self.static_line_3, 2, wx.ALL|wx.EXPAND, 10)
        grid_sizer_6.Add(self.checkbox_1, 0, wx.ALL, 2)
        grid_sizer_6.Add(self.label_3, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_6.Add(self.checkbox_2, 0, wx.ALL, 2)
        grid_sizer_6.Add(self.label_4, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_6.Add(self.checkbox_3, 0, wx.ALL, 2)
        grid_sizer_6.Add(self.label_5, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_6.Add(self.checkbox_4, 0, wx.ALL, 2)
        grid_sizer_6.Add(self.label_6, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_6.Add(self.checkbox_5, 0, wx.ALL, 2)
        grid_sizer_6.Add(self.label_7, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_6.Add(self.checkbox_6, 0, wx.ALL, 2)
        grid_sizer_6.Add(self.label_8, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_6.Add(self.checkbox_7, 0, wx.ALL, 2)
        grid_sizer_6.Add(self.label_9, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_6.Add(self.checkbox_8, 0, wx.ALL, 2)
        grid_sizer_6.Add(self.label_10, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_2.Add(grid_sizer_6, 1, wx.RIGHT|wx.TOP|wx.EXPAND, 9)
        sizer_1.Add(grid_sizer_2, 1, wx.TOP|wx.EXPAND, 0)
        self.SetSizer(sizer_1)
        sizer_1.Fit(self)
        self.Layout()
        # end wxGlade


	# 1 second timer
    def OnTimer1 (self, event):
	#self.label_13.SetLabel (time.strftime("Time: %H:%M:%S", time.localtime()))
	self.label_13.SetLabel (time.strftime("Time: %H:%M:%S", time.gmtime()))

	# 60 second timer
    def OnTimer2 (self, event):
	print "Date: ", time.gmtime()
	self.label_12.SetLabel (time.strftime("Date: %Y-%m-%d", time.gmtime()))
	
    def OnMenuExit(self, event): # wxGlade: MyFrame1.<event_handler>
 	print "Shutting down P3K Control GUI"
	if self.plotToolsRunning == True:
	    self.ClosePlotTools()
        self.Close()

    def OnQuit (self, event):
	print "Exiting P3K Control GUI"
	if self.plotToolsRunning == True:
	    self.ClosePlotTools()
	time.sleep (1)
	self.Destroy()

    def OnAbout(self, event): # wxGlade: MyFrame1.<event_handler>
        self.MessageDialog (ABOUT_TEXT, "About P3K User Interface")
	pass

    def OnTTM (self, event):
	host = '137.78.170.27'  # p3k1.jpl.nasa.gov
	port = 2157
	buffer = 1024
	addr = (host, port)
	ttmsock = socket (AF_INET, SOCK_STREAM, 0)
	ttmsock.connect (addr)
	if self.button_1.GetValue() == True:
	    	ttmOn = ['TTM ON\r']
		for line in ttmOn:
		    ttmsock.send (line)
		    recvdata = ttmsock.recv (512)
		if recvdata.find ('ERR:') == 0:
		    print "ERR recieved:", repr (recvdata)
		    ttmsock.close()
		else:
		    print "Recieved data: ", repr (recvdata)
		    print "Turning the TTM on"
		    ttmsock.close()
		    self.button_1.SetBackgroundColour(wx.Colour(0,255, 0))
		    self.button_1.ClearBackground()
		    self.button_1.Refresh()
	else:
	    	ttmOff = ['TTM OFF\r']
		for line in ttmOff:
		    ttmsock.send (line)
		    recvdata = ttmsock.recv (512)
                if recvdata.find ('ERR:') == 0:
                    print "ERR recieved:", repr (recvdata)
                    ttmsock.close()
                else:
		    print "Recieved data: ", repr (recvdata)
		    print "Turning the TTM off"
		    ttmsock.close()
		    #self.button_1.SetBackgroundColour(wx.Colour(236,233,216))
		    self.button_1.SetBackgroundColour(wx.NullColor)
		    self.button_1.ClearBackground()
		    self.button_1.Refresh()

    def OnLODM (self, event):
	host = '137.78.170.27'  # p3k1.jpl.nasa.gov
	port = 2157
	buffer = 1024
	addr = (host, port)
	losock = socket (AF_INET, SOCK_STREAM, 0)
	losock.connect (addr)
        if self.button_2.GetValue() == True:
	    	lodmOn = ['LODM ON\r']
		for line in lodmOn:
		    losock.send (line)
		    recvdata = losock.recv (512)
		if recvdata.find ('ERR:') == 0:
		    print "ERR recieved:", repr (recvdata)
		    losock.close()
		else:
		    print "Recieved data: ", repr (recvdata)
		    print "Turning the LODM on"
		    losock.close()
		    print "Turning the LODM on"
                    self.button_2.SetBackgroundColour(wx.Colour(0,255, 0))
                    self.button_2.ClearBackground()
                    self.button_2.Refresh()
        else:
	    	lodmOff = ['LODM OFF\r']
		for line in lodmOff:
		    losock.send (line)
		    recvdata = losock.recv (512)
                if recvdata.find ('ERR:') == 0:
                    print "ERR recieved:", repr (recvdata)
                    losock.close()
                else:
		    print "Recieved data: ", repr (recvdata)
		    print "Turning the LODM off"
		    losock.close()
                    #self.button_2.SetBackgroundColour(wx.Colour(236,233,216))
                    self.button_2.SetBackgroundColour(wx.NullColor)
                    self.button_2.ClearBackground()
                    self.button_2.Refresh()

    def OnHODM (self, event):
	host = '137.78.170.27'  # p3k1.jpl.nasa.gov
	port = 2157
	buffer = 1024
	addr = (host, port)
	hosock = socket (AF_INET, SOCK_STREAM, 0)
	hosock.connect (addr)
        if self.button_3.GetValue() == True:
	    	hodmOn = ['HODM ON\r']
		for line in hodmOn:
		    hosock.send (line)
		    recvdata = hosock.recv (512)
		if recvdata.find ('ERR:') == 0:
		    print "ERR recieved:", repr (recvdata)
		    hosock.close()
		else:
		    print "Recieved data: ", repr (recvdata)
		    print "Turning the HODM on"
		    hosock.close()
		    print "Turning the HODM on"
                    self.button_3.SetBackgroundColour(wx.Colour(0,255, 0))
                    self.button_3.ClearBackground()
                    self.button_3.Refresh()
        else:
	    	hodmOff = ['HODM OFF\r']
		for line in hodmOff:
		    hosock.send (line)
		    recvdata = hosock.recv (512)
                if recvdata.find ('ERR:') == 0:
                    print "ERR recieved:", repr (recvdata)
                    hosock.close()
                else:
		    print "Recieved data: ", repr (recvdata)
		    print "Turning the HODM off"
		    hosock.close()
                    #self.button_3.SetBackgroundColour(wx.Colour(236,233,216))
                    self.button_3.SetBackgroundColour(wx.NullColor)
                    self.button_3.ClearBackground()
                    self.button_3.Refresh()

    def GoAcqCam (self, event): # wxGlade: MyFrame1.<event_handler>
	if self.checkbox_1.IsChecked() == True:
        	print "Starting AcqCam..."
		self.acqcam = AcquisitionCameraUI.AcamGui (self, 120, 'Palomar 3000 Acquisition Camera')
		self.acqcam.Show (True)
	else:
		self.CloseAcqCam ()
	        self.checkbox_1.SetValue (False)

    def CloseAcqCam (self):
	print "Closing AcqCam..."
	self.acqcam.Destroy()
	self.checkbox_1.SetValue (False)
	
    def GoWfsCam (self, event): # wxGlade: MyFrame1.<event_handler>
	if self.checkbox_2.IsChecked() == True:
        	print "Starting WFS Cam..."
		self.wfs = WFSCameraUI.WFSCamera (self, 125, 'WFS Camera')
		self.wfs.Show (True)
	else:
		self.CloseWfsCam ()

    def CloseWfsCam (self):
	print "Closing WFS Camera..."
	self.wfs.Show (False)
	self.checkbox_2.SetValue (False)
	
    def GoFlatMap (self, event): # wxGlade: MyFrame1.<event_handler>
	if self.checkbox_3.IsChecked() == True:
        	print "Starting Flatmap..."
		self.fm = FlatMap.FlatMap (self, 130, 'Flat Map')
		self.fm.Show (True)
	else:
		self.CloseFlatMap ()

    def CloseFlatMap (self):
	print "Closing Flat Map ..."
	self.fm.Destroy ()
	self.checkbox_3.SetValue (False)
	
    def GoStatus (self, event): # wxGlade: MyFrame1.<event_handler>
	if self.checkbox_4.IsChecked() == True:
        	print "Starting Status..."
		self.stat = Status.Status (self, 135, 'Palomar 3000 Status')
		self.stat.Show (True)
	else:
		self.CloseStatus ()

    def CloseStatus (self):
	print "Closing status..."
	self.stat.Destroy ()
	self.checkbox_4.SetValue (False)
	
    def GoMotors (self, event): # wxGlade: MyFrame1.<event_handler>
	if self.checkbox_5.IsChecked() == True:
        	print "Starting Motors..."
		self.motors = MotionControl.MotionControl (self, 140, 'P3K Motion Control')
		self.motors.Show (True)
	else:
		self.CloseMotionControl ()

    def CloseMotionControl (self):
	print "Closing Motion Control..."
	self.motors.Destroy ()
	self.checkbox_5.SetValue (False)
	
    def GoHwfpParameters(self, event): # wxGlade: MyFrame1.<event_handler>
	if self.checkbox_6.IsChecked() == True:
        	print "Starting Parameters..."
		self.param = HwfpParametersUI.HWFPParameters (self, 145, 'P3K HWFP Parameter Settings')
		self.param.Show (True)
	else:
		self.CloseHwfpParameters ()
    def CloseHwfpParameters (self):
	print "Closing Parameters..."
	self.param.Destroy ()
	self.checkbox_6.SetValue (False)
	
    def GoTelemetry (self, event): # wxGlade: MyFrame1.<event_handler>
	if self.checkbox_7.IsChecked() == True:
        	print "Starting Telemetry..."
		self.telem = Telemetry.Telemetry (self, 150, 'Telemetry')
		self.telem.Show (True)
	else:
		self.CloseTelemetry ()

    def CloseTelemetry (self):
	print "Closing Telemetry..."
	self.telem.Destroy ()
	self.checkbox_7.SetValue (False)

    def GoPlotTools (self, event): # wxGlade: MyFrame1.<event_handler>
	self.plotToolsRunning = True
	if self.checkbox_8.IsChecked() == True:
        	print "Starting Plot Tools..."
		self.pt = PlotTool.PlotTool (self, 155, 'Plot Tools')
		self.pt.Show (True)
	else:
		self.ClosePlotTools ()

    def ClosePlotTools (self):
	print "Closing Plot Tools..."
	self.pt.ClosePlotTools ()
	time.sleep (1)
	self.plotToolsRunning = False 
	self.pt.Destroy ()
	self.checkbox_8.SetValue (False)

    def MessageDialog(self, text, title):
        messageDialog = wx.MessageDialog(self, text, title, wx.OK | wx.ICON_INFORMATION)
        messageDialog.ShowModal()
        messageDialog.Destroy()

# end of class MyFrame1


class MyApp(wx.App):
    def OnInit(self):
        wx.InitAllImageHandlers()
        frame_2 = MyFrame1(None, -1, "")
        self.SetTopWindow(frame_2)
        frame_2.Show()
        return 1

# end of class MyApp

if __name__ == "__main__":
    app = MyApp(0)
    app.MainLoop()
