import wx
import pkg_resources
import numpy
import threading
import os
import struct
import time
import socket

import matplotlib
import matplotlib.cm as cm
matplotlib.interactive (False)
matplotlib.use ('WXAgg')

from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg
from matplotlib.backends.backend_wx import NavigationToolbar2Wx
from matplotlib.figure import Figure
from matplotlib.pyplot import setp

ID_QUIT    = 101
ID_REGDM   = 102
ID_BCKGRND = 103
ID_SETTING = 104

HOST = "198.202.125.206"    # p3k-telem@palomar
LODMPOSPORT = 10108
MSGLEN = 882		    # 21^2 * 2 bytes

class LodmPosThread (threading.Thread):
	def __init__(self, window):
		threading.Thread.__init__(self)
		self.window = window
		self.finished = threading.Event()
		
	def stop (self):
		self.finished.set()
		self.socketobj.close()
		

	def run (self):
		self.socketobj = socket.socket (socket.AF_INET, socket.SOCK_STREAM) 
		self.socketobj.setsockopt (socket.SOL_TCP, socket.TCP_NODELAY, 1)

		try:
			self.socketobj.connect ((HOST, LODMPOSPORT))
		except socket.gaierror, e:
			print "Address-related error connecting to server: %s" % e
		except socket.error, e:
                        print "Connection error: %s" %e
		
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

			data = numpy.fromstring (msg, dtype = numpy.int16)
			# d1 = 21x21 array that needs to be flipped up-down #
			d1 = data.reshape ((21, 21))
			# d2 = 21x21 array that is flipped correctly #
			d2 = numpy.flipud (d1)
			wx.CallAfter (self.window.UpdateDisplay, d2)

			if self.finished.isSet():
				print "Closing LODM Positions display thread socket ..."
				self.socketobj.close()
				break

class HwfpLodmPos (wx.Frame):
	def __init__(self, parent, id, title):
		wx.Frame.__init__(self, parent, id, title)
		panel = wx.Panel (self, -1)

		self.canvasInit = 0
		self.scaleMin = 0
                self.scaleMax = 0
		font = wx.SystemSettings_GetFont (wx.SYS_SYSTEM_FONT)
		font.SetPointSize (9)

		#--- Set up timer to start data capture ---#
		self.timer1 = wx.Timer (self)
		self.timer1.Start (100, oneShot = True)
		#------------------------------------------#

		#--------Set up panels-----------#
		self.figure = Figure ()
		self.canvas = FigureCanvasWxAgg (self, wx.ID_ANY, self.figure)
		self.subplot = self.figure.add_subplot (1, 1, 1)
		#--------------------------------#

		#------- Create Sizer -----------#
		sizer = wx.BoxSizer (wx.VERTICAL)
		sizer.Add (self.canvas, 1, flag = wx.EXPAND | wx.ALL, border = 5)
		#--------------------------------#

		#-----------  Binds  ------------#
		self.Bind (wx.EVT_CLOSE, self.OnClose)
		self.Bind (wx.EVT_TIMER, self.CameraOnOff, self.timer1)
		#--------------------------------#

		self.SetSizer (sizer)
		self.SetMinSize (self.GetBestSize())
		self.Centre ()
		self.Show (True)

	def CameraOnOff (self, event):
		self.thread = LodmPosThread (self)
		self.thread.start()

	def UpdateDisplay (self, data):
		self.data = data

		### Set up the initial canvas and image ###
		if self.canvasInit == 0:
		    self.PlotInit (data)
		    self.canvasInit = 1
		    self.scaleMin = self.data.min()
                    self.scaleMax = self.data.max()

		self.im.set_array (data)
		self.cb.set_array (data)

		if -30 < (self.scaleMax - self.data.max()) < 70:
                    #print "Max data within boundaries."
                    pass
                else:
                    self.scaleMax = self.data.max()
                    self.im.autoscale()
                    self.im.changed

                if -70 < (self.scaleMin - self.data.min()) < 30:
                    #print "Min data within boundaries."
                    pass
                else:
                    self.scaleMin = self.data.min()
                    self.im.autoscale()
                    self.im.changed
		
		self.canvas.draw ()

	def PlotInit (self, data):
		self.im = self.subplot.imshow (data)
		self.cb = self.figure.colorbar (self.im)
	
	def OnEraseBackground (self, event):		### supposed to help with redraw flicker
		pass

	def OnSave (self, event):
		pass

	def OnQuit (self, event):
		if str (self.GetParent()) == "None": 
			self.thread.stop()
			self.Close()
			pass
		else:
			self.thread.stop()
			self.GetParent().CloseLodmPos ()
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
		self.GetParent().CloseLodmPos ()
		time.sleep (.5)
		self.Destroy()
		pass
	
if __name__ == "__main__":
    app = wx.App ()
    HwfpLodmPos (None, -1, 'Low Order Wavefront Positions')
    app.MainLoop ()
    


