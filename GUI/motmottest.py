import wx
import pkg_resources
import numpy

from pygarrayimage.arrayimage import ArrayInterfaceImage
import motmot.wxglvideo.wxglvideo as vid

SIZE128X128 = 128, 128, 3

class WFSCamera (wx.Frame):
	def __init__(self, parent, id, title):
		wx.Frame.__init__(self, parent, id, title)
		panel = wx.Panel (self, -1)

		#--------Set up panels-----------#
		self.pnl1 = wx.Panel (self, wx.ID_ANY, size = (400,400))
		self.pnl1.SetBackgroundColour (wx.BLACK)
		pnl2 = wx.Panel (self, wx.ID_ANY)
		#--------------------------------#

		#--------Set up boxes -----------#
		vbox = wx.BoxSizer (wx.VERTICAL)
		#--------------------------------#

		#------ Create Controls ---------#
		self.camOn = wx.RadioButton (pnl2, wx.ID_ANY, 'On', pos = wx.Point (10, 10), style=wx.RB_GROUP)
		self.camOff = wx.RadioButton (pnl2, wx.ID_ANY, 'Off', pos = wx.Point (55, 10))
		self.camOff.SetValue (True)

		#------- Create Sizer -----------#
		sizer = wx.BoxSizer (wx.VERTICAL)
		sizer.Add (self.pnl1, -1, flag = wx.EXPAND | wx.ALL, border = 15)
		sizer.Add (pnl2, 0, flag = wx.EXPAND | wx.ALL, border = 15)
		#--------------------------------#

		self.Bind (wx.EVT_RADIOBUTTON, self.CameraOnOff, self.camOn)
		self.Bind (wx.EVT_RADIOBUTTON, self.CameraOnOff, self.camOff)

		self.SetSizer (sizer)
		self.SetMinSize (self.GetBestSize())
		self.Centre ()
		self.Show (True)

	def CameraOnOff (self, event):
		if self.camOn.GetValue() == True:
			print 'Turning WFS Camera on.'
			ID_TIMER = wx.NewId()
			self.timer = wx.Timer (self, ID_TIMER)
			wx.EVT_TIMER (self, ID_TIMER, self.OnTimer)
			self.update_interval = 10 #msec
			self.timer.Start (self.update_interval)
	
			self.pnl1.Hide()
                	try:    
                        	self.gl_canvas = vid.DynamicImageCanvas (self.pnl1, -1)
                	finally:
                        	self.pnl1.Show()

                	ni = numpy.random.uniform( 0, 255, SIZE128X128).astype(numpy.uint8)
                	pygim = ArrayInterfaceImage(ni,allow_copy=False)
                	self.gl_canvas.new_image(pygim)
		
		else:
			print 'Turning WFS Camera off.'
			self.timer.Stop ()
			print 'Timer Stopped.'
	
	def OnTimer (self, event):
		self.gl_canvas.set_fullcanvas (True)
		my_numpy_array = numpy.random.uniform( 0, 255, SIZE128X128).astype(numpy.uint8)
		self.gl_canvas.update_image(my_numpy_array)


if __name__ == "__main__":
    app = wx.App ()
    WFSCamera (None, -1, 'WFS Camera')
    app.MainLoop ()




