import os
import pprint
import random
import sys
import wx
import os
import struct
import time
import socket
import threading

# The recommended way to use wx with mpl is with the WXAgg backend. 
import matplotlib
matplotlib.use ('WXAgg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import \
    FigureCanvasWxAgg as FigCanvas, \
    NavigationToolbar2WxAgg as NavigationToolbar
import numpy as np
import pylab

HOST = "198.202.125.206"	# p3k-telem.palomar.caltech.edu
TTMPOSPORT = 10110
MSGLEN = 8

class TtmPosDataThread (threading.Thread):
    def __init__ (self, window):
        threading.Thread.__init__(self)
        self.window = window
        self.finished = threading.Event()

    def stop (self):
        self.finished.set()
        time.sleep (1)
        self.socketobj.close()

    def run (self):
        print "Starting ttm positions thread."
        self.socketobj = socket.socket (socket.AF_INET, socket.SOCK_STREAM)
        self.socketobj.setsockopt (socket.SOL_TCP, socket.TCP_NODELAY, 1)

	try:
	    self.socketobj.connect ((HOST, TTMPOSPORT))
	except socket.gaierror, e:
	    print "Address-related error connecting to server: %s" % e
	except socket.error, e:
	    print "Connection error: %s" % e

	while 1:
	    chunk = ''
		msg = ''
		while len (msg) < MSGLEN:
			try:
				chunk = self.socketobj.recv (MSGLEN - len (msg))
			except socket.error, e:
				print "Error recieving data: %s" % e
	
			if chunk == '':
				raise RuntimeError, "socket connection broken."
			
			msg = msg + chunk
				
		data = np.fromstring (msg, dtype=np.int16)
		wx.CallAfter (self.window.UpdateTTMData, data)
			
		if self.finished.isSet():
			print "Closing TTM Positions display thread socket ..."
			self.socketobj.close()
			break

class GraphFrame(wx.Frame):
    """ The main frame of the application
    """
    title = 'P3K: Tip & Tilt Positions'
    
    def __init__(self):
        wx.Frame.__init__(self, None, -1, self.title)
        
        self.paused = False
        
        self.create_menu()
        self.create_status_bar()
        self.create_main_panel()
        
        #--- Set up start timer for data capture ---#
        self.startTimer = wx.Timer (self)
        self.startTimer.Start (100, oneShot=True)
        self.Bind (wx.EVT_TIMER, self.StartData, self.startTimer)
	   #-------------------------------------------#

    def create_menu (self):
        self.menubar = wx.MenuBar()
        
        menu_file = wx.Menu()
        m_expt = menu_file.Append(-1, "&Save plot\tCtrl-S", "Save plot to file")
        self.Bind(wx.EVT_MENU, self.on_save_plot, m_expt)
        menu_file.AppendSeparator()
        m_exit = menu_file.Append(-1, "E&xit\tCtrl-X", "Exit")
        self.Bind (wx.EVT_MENU, self.OnQuit, m_exit)
                
        self.menubar.Append(menu_file, "&File")
        self.SetMenuBar(self.menubar)

    def StartData (self, event):
        self.thread = TtmPosDataThread (self)
        self.thread.start()

    def create_main_panel(self):
        self.panel = wx.Panel(self)

        self.init_plot()
        self.canvas = FigCanvas (self.panel, -1, self.fig)

        self.pause_button = wx.Button (self.panel, -1, "Pause")
        self.Bind (wx.EVT_BUTTON, self.on_pause_button, self.pause_button)
        self.Bind (wx.EVT_UPDATE_UI, self.on_update_pause_button, self.pause_button)
        
        self.cb_grid = wx.CheckBox (self.panel, -1, "Show Grid", style=wx.ALIGN_RIGHT)
        self.Bind (wx.EVT_CHECKBOX, self.on_cb_grid, self.cb_grid)
        self.cb_grid.SetValue (True)
        
        self.cb_xlab = wx.CheckBox (self.panel, -1, "Show X labels", style=wx.ALIGN_RIGHT)
        self.Bind (wx.EVT_CHECKBOX, self.on_cb_xlab, self.cb_xlab)        
        self.cb_xlab.SetValue (True)
        
        self.hbox1 = wx.BoxSizer (wx.HORIZONTAL)
        self.hbox1.Add(self.pause_button, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox1.AddSpacer(20)
        self.hbox1.Add(self.cb_grid, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox1.AddSpacer(10)
        self.hbox1.Add(self.cb_xlab, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        
        self.vbox = wx.BoxSizer(wx.VERTICAL)
        self.vbox.Add(self.canvas, 1, flag=wx.LEFT | wx.TOP | wx.GROW)        
        self.vbox.Add(self.hbox1, 0, flag=wx.ALIGN_LEFT | wx.TOP)
        
        self.panel.SetSizer(self.vbox)
        self.vbox.Fit(self)
        self.SetMinSize ((700, 250))
    
    def create_status_bar(self):
        self.statusbar = self.CreateStatusBar()

    def init_plot (self):
        self.dpi = 100
        self.fig = Figure ((3.0, 3.0), dpi=self.dpi)
        self.ttmdata = ((0.0, 0.0))
        self.timeList = []          ### list to create X label array
        self.timeListCount = 1      ### only want to keep the list len (10) 
        self.initialTime = round (time.time())
        self.timeList.append (self.initialTime)

        self.axes = self.fig.add_subplot (111)
        self.axes.set_axis_bgcolor ('black')
        self.axes.set_title ('P3K Tip & Tilt positions', size=12)
        
        pylab.setp (self.axes.get_xticklabels(), fontsize=8)
        pylab.setp (self.axes.get_yticklabels(), fontsize=8)

        # plot the data as a line series, and save the reference 
        # to the plotted line series
        self.plot_data = self.axes.plot (self.ttmdata, linewidth=1, color=(1, 1, 0),) [0]


    def UpdateTTMData (self, data):
        fmt = '<ff'
        s = struct.unpack (fmt, data)
        time = round (time.time())
        print s                 ### Erase once programs works as designed
        self.draw_plot (s, time)

    def draw_plot (self, data, time):
        self.data = data
        self.currentTime = time
        
        xmax = self.currentTime - self.initialTime
        xmin = self.initialTime

        ymin = -2.5
        ymax = 2.5

        self.axes.set_xbound(lower=xmin, upper=xmax)
        self.axes.set_ybound(lower=ymin, upper=ymax)
        
        if self.timeListCount < 10:
            self.timeList.append (xmax)
            self.timeListCount += 1
        else:
            firstVal = self.timeList.pop () ### List getting too long so remove element 0
            self.timeList.append (xmax)
            
        xData = np.array (self.TimeList)
        yData = np.array ([(self.data[0], xmax), (self.data[1], xmax)])
        
        # anecdote: axes.grid assumes b=True if any other flag is
        # given even if b is set to False.
        # so just passing the flag into the first statement won't
        # work.
        #
        if self.cb_grid.IsChecked():
            self.axes.grid (True, color='gray')
        else:
            self.axes.grid (False)

        # Using setp here is convenient, because get_xticklabels
        # returns a list over which one needs to explicitly 
        # iterate, and setp already handles this.
        #  
        pylab.setp (self.axes.get_xticklabels(), visible=self.cb_xlab.IsChecked())
        
        # X data is the time (in seconds) since the plots were started
        # Y data is ttm_a and ttm_b
        self.plot_data.set_xdata (len (xData))
        self.plot_data.set_ydata (yData)

        # Call to re-draw the canvas -- expensive call
        self.canvas.draw ()
    
    def addToTimeArray (self, data):
        self.timeData 
	
    def on_pause_button(self, event):
        self.paused = not self.paused
    
    def on_update_pause_button(self, event):
        label = "Resume" if self.paused else "Pause"
        self.pause_button.SetLabel(label)
    
    def on_cb_grid(self, event):
        self.draw_plot()
    
    def on_cb_xlab(self, event):
        self.draw_plot()
    
    def on_save_plot(self, event):
        file_choices = "PNG (*.png)|*.png"
        
        dlg = wx.FileDialog(
            self,
            message="Save plot as...",
            defaultDir=os.getcwd(),
            defaultFile="plot.png",
            wildcard=file_choices,
            style=wx.SAVE)
        
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            self.canvas.print_figure(path, dpi=self.dpi)
            self.flash_status_message("Saved to %s" % path)
    
    #def on_redraw_timer(self, event):
        # if paused do not add data, but still redraw the plot
        # (to respond to scale modifications, grid change, etc.)
        #
        #if not self.paused:
        #    self.data.append(self.datagen.next())
        
        #self.draw_plot()
    
    def OnQuit (self, event):
	if str (self.GetParent()) == "None": 
		self.thread.stop()
		self.Close()
		pass
	else:
		self.thread.stop()
		self.GetParent().CloseTtmPos ()
		self.Close()
		pass

    def OnClose (self, event):
	if str (self.GetParent()) == "None":
		self.thread.stop()
		time.sleep (.5)
		self.Destroy()
		pass
        else:
		self.thread.stop()
		self.GetParent().CloseTtmPos ()
		time.sleep (.5)
		self.Destroy()
		pass

if __name__ == '__main__':
    app = wx.PySimpleApp()
    app.frame = GraphFrame()
    app.frame.Show()
    app.MainLoop()
