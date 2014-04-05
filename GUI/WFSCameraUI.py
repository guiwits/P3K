import wx
import pkg_resources
import numpy
import threading
import os
import struct
import time
import socket

ID_QUIT    = 101
ID_REGDM   = 102
ID_BCKGRND = 103
ID_SETTING = 104

HOST = "198.202.125.206"    # p3k-telem@cit
HWFP128SUBPORT = 10103
HWFP64SUBPORT = 10103
MSGLEN128 = 32768
MSGLEN64 = 4096
SCALE = 0


class Settings (wx.Dialog):
	def __init__(self, parent, id, title):
		wx.Dialog.__init__(self, parent, id, title, size = (350,300))
		
		self.camInfo = wx.StaticText(self, -1, "WFS Camera Settings")
		self.camRate = wx.StaticText(self, -1, "Camera Rate:")
		self.curCamRate = wx.StaticText(self, -1, "500")
		self.camRateTxt = wx.TextCtrl(self, -1, "")
		self.camGain = wx.StaticText(self, -1, "Camera Gain:")
		self.curCamGain = wx.StaticText(self, -1, "1.0")
		self.camGainTxt = wx.TextCtrl(self, -1, "")
		self.text_ctrl_14 = wx.TextCtrl(self, -1, "")
		self.backGrnd = wx.StaticText(self, -1, "Background ")
		self.text_ctrl_15 = wx.TextCtrl(self, -1, "")
		self.mvDist = wx.StaticText(self, -1, "Move Distance:")
		self.curMvDist = wx.StaticText(self, -1, "60")
		self.mvDistTxt = wx.TextCtrl(self, -1, "")
		self.text_ctrl_8 = wx.TextCtrl(self, -1, "")
		self.regDM = wx.StaticText(self, -1, "Register DM")
		self.text_ctrl_9 = wx.TextCtrl(self, -1, "")
		self.regMode = wx.StaticText(self, -1, "Register Mode:")
		self.curRegMode = wx.StaticText(self, -1, "1")
		self.regModeTxt = wx.TextCtrl(self, -1, "")
		self.text_ctrl_6 = wx.TextCtrl(self, -1, "")
		self.manPupShift = wx.StaticText(self, -1, "Pupil Shift")
		self.text_ctrl_7 = wx.TextCtrl(self, -1, "")
		self.text_ctrl_10 = wx.TextCtrl(self, -1, "")
		self.northSB = wx.BitmapButton (self, wx.ID_ANY, wx.Bitmap ('icons/stock_up.png'), 
						pos = wx.Point (10,5))
		self.southSB = wx.BitmapButton (self, wx.ID_ANY, wx.Bitmap ('icons/stock_down.png'))
		self.westSB = wx.BitmapButton (self, wx.ID_ANY, wx.Bitmap ('icons/stock_left.png'), 
						pos = wx.Point (100,100))
		self.eastSB = wx.BitmapButton (self, wx.ID_ANY, wx.Bitmap ('icons/stock_right.png'))
		self.text_ctrl_11 = wx.TextCtrl(self, -1, "")
		self.mvStep = wx.TextCtrl(self, -1, "")
		self.text_ctrl_12 = wx.TextCtrl(self, -1, "")
		self.text_ctrl_13 = wx.TextCtrl(self, -1, "")
		self.staticLine = wx.StaticLine (self, wx.ID_ANY, style = wx.LI_HORIZONTAL)
		self.staticLine2 = wx.StaticLine (self, wx.ID_ANY, style = wx.LI_HORIZONTAL)
		self.staticLine3 = wx.StaticLine (self, wx.ID_ANY, style = wx.LI_HORIZONTAL)
		self.applyB = wx.Button (self, wx.ID_ANY, "Apply")
		self.closeB = wx.Button (self, wx.ID_ANY, "Close")
		self.cancelB = wx.Button (self, wx.ID_ANY, "Cancel")
		l1font = wx.Font (10, wx.DEFAULT, wx.NORMAL, wx.NORMAL)
		l2font = wx.Font (12, wx.DEFAULT, wx.NORMAL, wx.BOLD)
		self.text_ctrl_16 = wx.TextCtrl(self, -1, "")
		self.text_ctrl_17 = wx.TextCtrl(self, -1, "")
		self.camInfo.SetFont (l2font)
		self.camRate.SetFont (l1font)
		self.camGain.SetFont (l1font)
		self.backGrnd.SetFont (l2font)
		self.regDM.SetFont (l2font)
		self.manPupShift.SetFont (l2font)
		self.mvDist.SetFont (l1font)
		self.regMode.SetFont (l1font)
		self.curCamRate.SetForegroundColour (wx.BLUE)
		self.curCamGain.SetForegroundColour (wx.BLUE)
		self.curMvDist.SetForegroundColour (wx.BLUE)
		self.curRegMode.SetForegroundColour (wx.BLUE)
		self.__set_properties()
		self.__do_layout()
	
	def __set_properties(self):
       		# begin wxGlade: WFSCamSettings.__set_properties
        	self.SetTitle("WFS Camera - Settings")
        	self.text_ctrl_14.Hide()
        	self.text_ctrl_15.Hide()
        	self.text_ctrl_8.Hide()
        	self.text_ctrl_9.Hide()
        	self.text_ctrl_6.Hide()
        	self.text_ctrl_7.Hide()
        	self.text_ctrl_10.Hide()
        	self.text_ctrl_11.Hide()
        	self.mvStep.SetMinSize((50, 25))
        	self.text_ctrl_12.Hide()
        	self.text_ctrl_13.Hide()
        	self.text_ctrl_16.Hide()
        	self.text_ctrl_17.Hide()
	
	def __do_layout(self):
       		# begin wxGlade: WFSCamSettings.__do_layout
       		sizer = wx.BoxSizer(wx.VERTICAL)
       		grid_sizer = wx.FlexGridSizer(14, 3, 1, 1)
       		grid_sizer.Add(self.text_ctrl_16, 0, 0, 0)
       		grid_sizer.Add(self.camInfo, 0, wx.BOTTOM, border = 15)
       		grid_sizer.Add(self.text_ctrl_17, 0, 0, 0)
       		grid_sizer.Add(self.camRate, 0, wx.BOTTOM, 10)
       		grid_sizer.Add(self.curCamRate, 0, 0, 0)
       		grid_sizer.Add(self.camRateTxt, 0, wx.BOTTOM, 10)
       		grid_sizer.Add(self.camGain, 0, 0, 0)
       		grid_sizer.Add(self.curCamGain, 0, 0, 0)
       		grid_sizer.Add(self.camGainTxt, 0, 0, 0)
       		grid_sizer.Add(self.text_ctrl_14, 0, 0, 0)
       		grid_sizer.Add(self.backGrnd, 0, wx.TOP|wx.ALIGN_CENTER_HORIZONTAL, 15)
       		grid_sizer.Add(self.text_ctrl_15, 0, 0, 0)
       		grid_sizer.Add(self.mvDist, 0, 0, 0)
       		grid_sizer.Add(self.curMvDist, 0, 0, 0)
       		grid_sizer.Add(self.mvDistTxt, 0, 0, 0)
       		grid_sizer.Add(self.text_ctrl_8, 0, 0, 0)
       		grid_sizer.Add(self.regDM, 0, wx.TOP|wx.ALIGN_CENTER_HORIZONTAL, 15)
       		grid_sizer.Add(self.text_ctrl_9, 0, 0, 0)
       		grid_sizer.Add(self.regMode, 0, 0, 0)
       		grid_sizer.Add(self.curRegMode, 0, 0, 0)
       		grid_sizer.Add(self.regModeTxt, 0, 0, 0)
       		grid_sizer.Add(self.text_ctrl_6, 0, 0, 0)
       		grid_sizer.Add(self.manPupShift, 0, wx.TOP|wx.ALIGN_CENTER_HORIZONTAL, 15)
       		grid_sizer.Add(self.text_ctrl_7, 0, 0, 0)
       		grid_sizer.Add(self.text_ctrl_10, 0, 0, 0)
       		grid_sizer.Add(self.northSB, 0, wx.BOTTOM| wx.TOP | wx.ALIGN_CENTER_HORIZONTAL, 15)
       		grid_sizer.Add(self.text_ctrl_11, 0, 0, 0)
       		grid_sizer.Add(self.westSB, 0, wx.RIGHT | wx.ALIGN_RIGHT, -60)
       		grid_sizer.Add(self.mvStep, 0, wx.ALIGN_CENTER_HORIZONTAL, 0)
       		grid_sizer.Add(self.eastSB, 0, wx.LEFT | wx.ALIGN_LEFT, -60)
       		grid_sizer.Add(self.text_ctrl_12, 0, 0, 0)
       		grid_sizer.Add(self.southSB, 0, wx.TOP|wx.ALIGN_CENTER_HORIZONTAL, 15)
       		grid_sizer.Add(self.text_ctrl_13, 0, 0, 0)
		grid_sizer.Add (self.staticLine, 0, wx.EXPAND  | wx.TOP | wx.BOTTOM, 15)
		grid_sizer.Add (self.staticLine2, 0, wx.EXPAND | wx.TOP | wx.BOTTOM, 15)
		grid_sizer.Add (self.staticLine3, 0, wx.EXPAND | wx.TOP | wx.BOTTOM, 15)
		grid_sizer.Add (self.applyB, 0, wx.ALL | wx.EXPAND, 15)
		grid_sizer.Add (self.cancelB, 0, wx.RIGHT | wx.TOP | wx.BOTTOM, 15)
		grid_sizer.Add (self.closeB, 0, wx.ALL | wx.EXPAND, 15)
		#grid_sizer.Add (self.bsizer1, 1, wx.ALL | wx.EXPAND, 5)
		
		#grid_sizer.Add (self.bsizer2, 3, wx.ALL | wx.EXPAND, 5)
       		sizer.Add(grid_sizer, 1, wx.ALL|wx.EXPAND, 10)
		self.Bind (wx.EVT_BUTTON, self.OnClose, self.closeB)
		self.Bind (wx.EVT_BUTTON, self.OnApply, self.applyB)
		self.Bind (wx.EVT_BUTTON, self.OnCancel, self.cancelB)
       		self.SetSizer(sizer)
       		sizer.Fit(self)
		self.CentreOnParent()
       		self.Layout()

	def OnClose (self, event): 
		self.Close ()
		
	def OnCancel (self, event):
		print "Cancel pressed. Closing without sending data to AOCA."
		self.Close ()
		
	def OnApply (self, event):
		print "Sending new data to AOCA for processing."
		self.Close ()

class HwfpThread (threading.Thread):
	def __init__(self, window):
		threading.Thread.__init__(self)
		self.window = window
		self.finished = threading.Event()
		
	def stop (self):
		self.finished.set()

	def run (self):
		print "Starting display thread..."
		self.socketobj = socket.socket (socket.AF_INET, socket.SOCK_STREAM) 
		self.socketobj.setsockopt (socket.SOL_TCP, socket.TCP_NODELAY, 1)
		try:
			self.socketobj.connect ((HOST, HWFP128SUBPORT))
		except socket.gaierror, e:
			print "Address-related error connecting to server: %s" % e
                        self.camOff.SetValue (True)
		except socket.error, e:
                        print "Connection error: %s" %e
                        self.camOff.SetValue (True)

		while 1:
			chunk = ''
			msg = ''
			while len (msg) < MSGLEN128:
				try:
					chunk = self.socketobj.recv (MSGLEN128 - len (msg))
				except socket.error, e:
					print "Error recieving data: %s" % e
	
				if chunk == '':
					raise RuntimeError, "socket connection broken."
				
				msg = msg + chunk

			data = numpy.fromstring (msg, dtype = numpy.uint16)
			ndimage = data.reshape ((128, 128))

			rgb = numpy.zeros ((128, 128, 3), dtype = numpy.uint16)
			#rgb[:,:,0] = rgb[:,:,1] = rgb[:,:,2] = ndimage

			#wfsImage = wx.BitmapFromBuffer (rgb.shape[0], rgb.shape[1], rgb)

			#tempImg = wx.ImageFromBitmap (wfsImage)

			#if self.imgSize.GetValue() == 1:
				# do nothing
			#	pass
			#if self.imgSize.GetValue() == 2:
			#	tempImg.Rescale (256, 256)
			#if self.imgSize.GetValue() == 3:
			#	tempImg.Rescale (384, 384)
			#if self.imgSize.GetValue() == 4:
			#	tempImg.Rescale (512, 512)

			#self.image = wx.BitmapFromImage (tempImg)
			#wx.CallAfter (self.window.UpdateDisplay, self.image)
			wx.CallAfter (self.window.UpdateDisplay, data)

			if self.finished.isSet():
				print "Closing display thread socket ..."
				self.socketobj.close()
				break

		print "P3K HWFS Camera Viewing Thread: Exiting ..."

class WFSCamera (wx.Frame):
	def __init__(self, parent, id, title):
		wx.Frame.__init__(self, parent, id, title)
		panel = wx.Panel (self, -1)

		font = wx.SystemSettings_GetFont (wx.SYS_SYSTEM_FONT)
		font.SetPointSize (9)

		#--------Set up panels-----------#
		self.pnl1 = wx.Panel (self, wx.ID_ANY, size = (512, 512))
		self.pnl1.SetBackgroundColour (wx.BLACK)
		pnl2 = wx.Panel (self, wx.ID_ANY)
		#--------------------------------#

		#-----	 1 off timer for auto on  -----#
		self.timer1 = wx.Timer (self)
		self.timer1.Start (100, oneShot = True)
		#--------------------------------------#

		#-----	 Menubar	  -----#
		menubar = wx.MenuBar ()
		file = wx.Menu ()
		file.AppendSeparator ()
		file.Append (ID_QUIT, "&Quit", "Terminate the program")

		wfsc = wx.Menu ()
		wfsc.Append (ID_REGDM, "&Register DM", "Register DM")
		wfsc.Append (ID_BCKGRND, "&Background", "Take background data")
		wfsc.Append (ID_SETTING, "Se&ttings", "Open the settings panel")

		menubar.Append (file, '&File')
		menubar.Append (wfsc, '&Control')
		#--------------------------------#

		#----------Statusbar-------------#
		self.CreateStatusBar ()
		#--------------------------------#

		#--------Set up boxes -----------#
		hbox1 = wx.GridSizer (wx.HORIZONTAL)
		hbox2 = wx.GridSizer (wx.HORIZONTAL)
		vbox = wx.BoxSizer (wx.VERTICAL)
		#--------------------------------#

		#------ Create Controls ---------#
		modestr = "Mode: "
		#font = wx.Font (10, wx.DECORATIVE, wx.NORMAL, wx.BOLD)
		font = wx.Font (10, wx.DECORATIVE, wx.NORMAL, wx.NORMAL)
		self.camOn = wx.RadioButton (pnl2, wx.ID_ANY, 'On', pos = wx.Point (10, 20), style=wx.RB_GROUP)
		self.camOff = wx.RadioButton (pnl2, wx.ID_ANY, 'Off', pos = wx.Point (55, 20))
		camOnOffSizer = wx.StaticBoxSizer (wx.StaticBox (pnl2, -1, 'Camera', (5, 5), size=(100, 40)), orient = wx.HORIZONTAL)
		camOnOffSizer.Add (self.camOn)
		camOnOffSizer.Add (self.camOff)
		self.camOff.SetValue (True)

		scaleStr = "Scale: "
		scale = wx.StaticText (pnl2, wx.ID_ANY, scaleStr, pos = wx.Point (255, 20), size = (90, 30))
		scale.SetFont (font)
		self.imgSize = wx.SpinCtrl (pnl2, wx.ID_ANY, '', (300, 15), (40, -1))
		self.imgSize.SetRange (1, 4)
		self.imgSize.SetValue (4)

		self.bkgdOn = wx.RadioButton (pnl2, wx.ID_ANY, 'On', style = wx.RB_GROUP, pos = wx.Point (130, 20))
		self.bkgdOff = wx.RadioButton (pnl2, wx.ID_ANY, 'Off', pos = wx.Point (175, 20))
		bkgdOnOffSizer = wx.StaticBoxSizer (wx.StaticBox (pnl2, -1, 'Background', (125, 5), size=(100, 40)), orient = wx.HORIZONTAL)
		bkgdOnOffSizer.Add (self.bkgdOn)
		bkgdOnOffSizer.Add (self.bkgdOff)
		self.bkgdOff.SetValue (True)

		#hbox1.Add (camOn, 0, wx.ALL | wx.EXPAND | wx.ALIGN_CENTER_HORIZONTAL, 15)
		#hbox1.Add (camOff, 0, wx.ALL | wx.EXPAND | wx.ALIGN_CENTER_HORIZONTAL, 15)
		hbox1.Add (camOnOffSizer, 0, wx.LEFT | wx.EXPAND, 15)
		hbox1.Add (bkgdOnOffSizer, 0, wx.LEFT | wx.EXPAND, 55)
		regdm = wx.ToggleButton (pnl2, wx.ID_ANY, label = 'Register DM', pos = wx.Point (7,70), size = (99, 30))
		settingsB = wx.Button (pnl2, wx.ID_ANY, label = 'Settings', pos = wx.Point (125, 70), size = (99,30))
		mode = wx.StaticText (pnl2, wx.ID_ANY, modestr, pos = wx.Point (360, 20), size = (90, 30))
		mode.SetFont (font)
		modeTextField = wx.TextCtrl (pnl2, wx.ID_ANY, pos = wx.Point (410, 15), size = (99, 30))

		#frameCounterStr = "Frame Count: "
		#frameCounterStaticText = wx.StaticText (pnl2, wx.ID_ANY, frameCounterStr, pos = wx.Point (240, 70), 
			#		size = (90, 30))
		#frameCounterStaticText.SetFont (font)
		#frameCountTextField = wx.TextCtrl (pnl2, wx.ID_ANY, pos = wx.Point (270, 70), size = (50, 30))

		closeB = wx.Button (pnl2, wx.ID_ANY, label = 'Close', pos = wx.Point (410, 70), size = (99, 30))
		hbox2.Add (regdm, 0, wx.LEFT | wx.ALL | wx.ALIGN_CENTER_HORIZONTAL | wx.EXPAND, 15)
		hbox2.Add (settingsB, 0, wx.LEFT | wx.EXPAND | wx.ALIGN_CENTER_HORIZONTAL, 15)	
		hbox2.Add (mode, 0, wx.LEFT | wx.EXPAND | wx.ALIGN_CENTER_HORIZONTAL, 15)	
		hbox2.Add (modeTextField, 0, wx.LEFT | wx.EXPAND | wx.ALIGN_CENTER_HORIZONTAL, 15)	
		hbox2.Add (closeB, 0, wx.RIGHT | wx.ALIGN_CENTER_HORIZONTAL)
		vbox.Add (hbox1, flag = wx.LEFT | wx.EXPAND | wx.ALL, border = 25)
		vbox.Add (hbox2, flag = wx.LEFT | wx.EXPAND | wx.ALL, border = 25)
		#--------------------------------#

		#------- Create Sizer -----------#
		sizer = wx.BoxSizer (wx.VERTICAL)
		sizer.Add (self.pnl1, 1, flag = wx.EXPAND | wx.ALL, border = 15)
		sizer.Add (pnl2, 0, flag = wx.EXPAND | wx.ALL, border = 15)
		#--------------------------------#

		#---- Set camera radio button on ----#
		self.camOn.SetValue(True)
		#------------------------------------#


		#-----------  Binds  ------------#
		self.Bind (wx.EVT_BUTTON, self.OnSettingClick, settingsB)
		self.Bind (wx.EVT_SPINCTRL, self.OnScaleChange, self.imgSize)
		self.Bind (wx.EVT_MENU, self.OnSettingClick, id = ID_SETTING)
		self.Bind (wx.EVT_MENU, self.OnQuit, id = ID_REGDM)
		self.Bind (wx.EVT_MENU, self.OnQuit, id = ID_BCKGRND)
		self.Bind (wx.EVT_MENU, self.OnQuit, id = ID_QUIT)
		self.Bind (wx.EVT_BUTTON, self.OnQuit, closeB)
		self.Bind (wx.EVT_RADIOBUTTON, self.CameraOnOff, self.camOn)
		self.Bind (wx.EVT_RADIOBUTTON, self.CameraOnOff, self.camOff)
		self.Bind (wx.EVT_RADIOBUTTON, self.BackgroundOnOff, self.bkgdOn)
		self.Bind (wx.EVT_RADIOBUTTON, self.BackgroundOnOff, self.bkgdOff)
		self.Bind (wx.EVT_TIMER, self.CameraOnOff, self.timer1)
		#--------- Set up PaintDC for global access --------#

		self.SetMenuBar (menubar)
		self.SetSizer (sizer)
		self.SetMinSize (self.GetBestSize())
		self.Centre ()
		self.Show (True)

	def OnScaleChange (self, event):
		self.pnl1.SetBackgroundColour (wx.BLACK)
                self.pnl1.Refresh ()

	def CameraOnOff (self, event):
		if self.camOn.GetValue() == True:
			print 'Turning WFS Camera on.'
			self.dc = wx.PaintDC (self.pnl1)
			self.thread = HwfpThread (self)
			self.thread.start()
		else:
			print 'Turning WFS Camera off.'
			self.thread.stop()
			#self.socketobj.close()
			#self.dc.Clear()
			#self.pnl1.SetBackgroundColour (wx.BLACK)
			#self.pnl1.Refresh ()

	def UpdateDisplay (self, data):
		self.data = data
		ndimage = data.reshape ((128, 128))
		ndimg_8bit = (ndimage / (16384/255)).astype (numpy.uint8) 	# rescale the image

		rgb = numpy.zeros ((128, 128, 3), dtype = numpy.uint8)
		rgb[:,:,0] = rgb[:,:,1] = rgb[:,:,2] = ndimg_8bit

		wfsImage = wx.BitmapFromBuffer (rgb.shape[0], rgb.shape[1], rgb)
		
		tempImg = wx.ImageFromBitmap (wfsImage)

		if self.imgSize.GetValue() == 1:
			#do nothing
			pass
		if self.imgSize.GetValue() == 2:
			tempImg.Rescale (256, 256)
		if self.imgSize.GetValue() == 3:
			tempImg.Rescale (384, 384)
		if self.imgSize.GetValue() == 4:
			tempImg.Rescale (512, 512)

		self.image = wx.BitmapFromImage (tempImg)
		self.dc.DrawBitmap (self.image, 0, 0, True)

	def BackgroundOnOff (self, event):
		if self.bkgdOn.GetValue() == True:
			print 'Turning background on.'
		else:
			print 'Turning background off.'

	def OnQuit (self, event):
		if str (self.GetParent()) == "None": 
			self.camOff.SetValue (True)
			self.thread.stop()
			self.Destroy()
			pass
		else:
			self.camOff.SetValue (True)
			self.thread.stop()
			self.GetParent().CloseWfsCam ()
			self.Close()
			pass
	
	def OnSettingClick (self, event):
		self.camOff.SetValue (True)
		print "stopping thread..."
		self.thread.stop()
		chgsetting = Settings (None, -1, "HWFP Camera :: Settings")
		chgsetting.ShowModal() 
		chgsetting.Destroy()
		
if __name__ == "__main__":
    app = wx.App ()
    WFSCamera (None, -1, 'HWFP Camera')
    app.MainLoop ()




