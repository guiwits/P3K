import wx

ID_QUIT = 101
ID_REGDM = 102
ID_BCKGRND = 103
ID_SETTING = 104

class Settings (wx.Dialog):
	def __init__(self, parent, id, title):
		wx.Dialog.__init__(self, parent, id, title, size = (350,300))
		
		self.bkgnd = wx.StaticText(self, -1, "Flatmap Settings")
		self.iterations = wx.StaticText(self, -1, "Iterations:")
		self.curItVal = wx.StaticText(self, -1, "3")
		self.iterTxt = wx.TextCtrl(self, -1, "")
		#self.camGain = wx.StaticText(self, -1, "Camera Gain:")
		#self.curCamGain = wx.StaticText(self, -1, "1.0")
		#self.camGainTxt = wx.TextCtrl(self, -1, "")
		#self.text_ctrl_14 = wx.TextCtrl(self, -1, "")
		#self.backGrnd = wx.StaticText(self, -1, "Background ")
		#self.text_ctrl_15 = wx.TextCtrl(self, -1, "")
		#self.mvDist = wx.StaticText(self, -1, "Move Distance:")
		#self.curMvDist = wx.StaticText(self, -1, "60")
		#self.mvDistTxt = wx.TextCtrl(self, -1, "")
		#self.text_ctrl_8 = wx.TextCtrl(self, -1, "")
		#self.regDM = wx.StaticText(self, -1, "Register DM")
		#self.text_ctrl_9 = wx.TextCtrl(self, -1, "")
		#self.regMode = wx.StaticText(self, -1, "Register Mode:")
		#self.curRegMode = wx.StaticText(self, -1, "1")
		#self.regModeTxt = wx.TextCtrl(self, -1, "")
		#self.text_ctrl_6 = wx.TextCtrl(self, -1, "")
		#self.manPupShift = wx.StaticText(self, -1, "Pupil Shift")
		#self.text_ctrl_7 = wx.TextCtrl(self, -1, "")
		#self.text_ctrl_10 = wx.TextCtrl(self, -1, "")
		#self.northSB = wx.BitmapButton (self, wx.ID_ANY, wx.Bitmap ('stock_up.png'))
		#self.southSB = wx.BitmapButton (self, wx.ID_ANY, wx.Bitmap ('stock_down.png'))
		#self.westSB = wx.BitmapButton (self, wx.ID_ANY, wx.Bitmap ('stock_left.png'))
		#self.eastSB = wx.BitmapButton (self, wx.ID_ANY, wx.Bitmap ('stock_right.png'))
		#self.text_ctrl_11 = wx.TextCtrl(self, -1, "")
		#self.mvStep = wx.TextCtrl(self, -1, "")
		#self.text_ctrl_12 = wx.TextCtrl(self, -1, "")
		#self.text_ctrl_13 = wx.TextCtrl(self, -1, "")
		self.staticLine = wx.StaticLine (self, wx.ID_ANY, style = wx.LI_HORIZONTAL)
		self.staticLine2 = wx.StaticLine (self, wx.ID_ANY, style = wx.LI_HORIZONTAL)
		self.staticLine3 = wx.StaticLine (self, wx.ID_ANY, style = wx.LI_HORIZONTAL)
		self.applyB = wx.Button (self, wx.ID_ANY, "Apply")
		self.okB = wx.Button (self, wx.ID_ANY, "OK")
		self.cancelB = wx.Button (self, wx.ID_ANY, "Cancel")
		#l1font = wx.Font (10, wx.DEFAULT, wx.NORMAL, wx.NORMAL)
		#l2font = wx.Font (12, wx.DEFAULT, wx.NORMAL, wx.BOLD)
		self.text_ctrl_16 = wx.TextCtrl(self, -1, "")
		self.text_ctrl_17 = wx.TextCtrl(self, -1, "")
		#self.camInfo.SetFont (l2font)
		#self.camRate.SetFont (l1font)
		#self.camGain.SetFont (l1font)
		#self.backGrnd.SetFont (l2font)
		#self.regDM.SetFont (l2font)
		#self.manPupShift.SetFont (l2font)
		#self.mvDist.SetFont (l1font)
		#self.regMode.SetFont (l1font)
		self.curItVal.SetForegroundColour (wx.BLUE)
		#self.curCamGain.SetForegroundColour (wx.BLUE)
		#self.curMvDist.SetForegroundColour (wx.BLUE)
		#self.curRegMode.SetForegroundColour (wx.BLUE)
		self.__set_properties()
		self.__do_layout()
	
	def __set_properties(self):
       		# begin wxGlade: WFSCamSettings.__set_properties
        	self.SetTitle("Flatmap :: Settings")
        	#self.text_ctrl_14.Hide()
        	#self.text_ctrl_15.Hide()
        	#self.text_ctrl_8.Hide()
        	#self.text_ctrl_9.Hide()
        	#self.text_ctrl_6.Hide()
        	#self.text_ctrl_7.Hide()
        	#self.text_ctrl_10.Hide()
        	#self.text_ctrl_11.Hide()
        	#self.mvStep.SetMinSize((50, 25))
        	#self.text_ctrl_12.Hide()
        	#self.text_ctrl_13.Hide()
        	self.text_ctrl_16.Hide()
        	self.text_ctrl_17.Hide()
	
	def __do_layout(self):
       		# begin wxGlade: WFSCamSettings.__do_layout
       		sizer = wx.BoxSizer(wx.VERTICAL)
       		grid_sizer = wx.FlexGridSizer(5, 3, 1, 1)
       		grid_sizer.Add(self.text_ctrl_16, 0, 0, 0)
       		grid_sizer.Add(self.bkgnd, 0, wx.BOTTOM, border = 15)
       		grid_sizer.Add(self.text_ctrl_17, 0, 0, 0)
       		grid_sizer.Add(self.iterations, 0, wx.BOTTOM, 10)
       		grid_sizer.Add(self.curItVal, 0, 0, 0)
       		grid_sizer.Add(self.iterTxt, 0, wx.BOTTOM, 10)
       		#grid_sizer.Add(self.camGain, 0, 0, 0)
       		#grid_sizer.Add(self.curCamGain, 0, 0, 0)
       		#grid_sizer.Add(self.camGainTxt, 0, 0, 0)
       		#grid_sizer.Add(self.text_ctrl_14, 0, 0, 0)
       		#grid_sizer.Add(self.backGrnd, 0, wx.TOP|wx.ALIGN_CENTER_HORIZONTAL, 15)
       		#grid_sizer.Add(self.text_ctrl_15, 0, 0, 0)
       		#grid_sizer.Add(self.mvDist, 0, 0, 0)
       		#grid_sizer.Add(self.curMvDist, 0, 0, 0)
       		#grid_sizer.Add(self.mvDistTxt, 0, 0, 0)
       		#grid_sizer.Add(self.text_ctrl_8, 0, 0, 0)
       		#grid_sizer.Add(self.regDM, 0, wx.TOP|wx.ALIGN_CENTER_HORIZONTAL, 15)
       		#grid_sizer.Add(self.text_ctrl_9, 0, 0, 0)
       		#grid_sizer.Add(self.regMode, 0, 0, 0)
       		#grid_sizer.Add(self.curRegMode, 0, 0, 0)
       		#grid_sizer.Add(self.regModeTxt, 0, 0, 0)
       		#grid_sizer.Add(self.text_ctrl_6, 0, 0, 0)
       		#grid_sizer.Add(self.manPupShift, 0, wx.TOP|wx.ALIGN_CENTER_HORIZONTAL, 15)
       		#grid_sizer.Add(self.text_ctrl_7, 0, 0, 0)
       		#grid_sizer.Add(self.text_ctrl_10, 0, 0, 0)
       		#grid_sizer.Add(self.northSB, 0, wx.BOTTOM| wx.TOP | wx.ALIGN_CENTER_HORIZONTAL, 15)
       		#grid_sizer.Add(self.text_ctrl_11, 0, 0, 0)
       		#grid_sizer.Add(self.westSB, 0, wx.RIGHT | wx.ALIGN_RIGHT, 0)
       		#grid_sizer.Add(self.mvStep, 0, wx.ALIGN_CENTER_HORIZONTAL, 0)
       		#grid_sizer.Add(self.eastSB, 0, 0, 0)
       		#grid_sizer.Add(self.text_ctrl_12, 0, 0, 0)
       		#grid_sizer.Add(self.southSB, 0, wx.TOP|wx.ALIGN_CENTER_HORIZONTAL, 15)
       		#grid_sizer.Add(self.text_ctrl_13, 0, 0, 0)
		grid_sizer.Add (self.staticLine, 0, wx.EXPAND  | wx.TOP | wx.BOTTOM, 15)
		grid_sizer.Add (self.staticLine2, 0, wx.EXPAND | wx.TOP | wx.BOTTOM, 15)
		grid_sizer.Add (self.staticLine3, 0, wx.EXPAND | wx.TOP | wx.BOTTOM, 15)
		grid_sizer.Add (self.cancelB, 0, wx.RIGHT | wx.TOP | wx.BOTTOM, 15)
		grid_sizer.Add (self.applyB, 0, wx.ALL | wx.EXPAND, 15)
		grid_sizer.Add (self.okB, 0, wx.ALL | wx.EXPAND, 15)
		#grid_sizer.Add (self.bsizer1, 1, wx.ALL | wx.EXPAND, 5)
		
		#grid_sizer.Add (self.bsizer2, 3, wx.ALL | wx.EXPAND, 5)
       		sizer.Add(grid_sizer, 1, wx.ALL|wx.EXPAND, 10)
		self.Bind (wx.EVT_BUTTON, self.OnClose, self.okB)
		self.Bind (wx.EVT_BUTTON, self.OnApply, self.applyB)
		self.Bind (wx.EVT_BUTTON, self.OnCancel, self.cancelB)
       		self.SetSizer(sizer)
       		sizer.Fit(self)
		self.CentreOnParent()
       		self.Layout()
				   
	def GetRate ():
		return 500
		
	def OnClose (self, event): 
		self.Close ()
		
	def OnCancel (self, event):
		self.Close ()
		
	def OnApply (self, event):
		self.Close ()


class FlatMap (wx.Frame):
	def __init__(self, parent, id, title):
		wx.Frame.__init__(self, parent, id, title, size=(400, 340))
		panel = wx.Panel (self, -1)

		font = wx.SystemSettings_GetFont (wx.SYS_SYSTEM_FONT)
		font.SetPointSize (9)

		#--------Set up panels-----------#
		pnl1 = wx.Panel (self, wx.ID_ANY, size = (400,400))
		pnl1.SetBackgroundColour (wx.BLACK)
		pnl2 = wx.Panel (self, wx.ID_ANY)
		#--------------------------------#

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
		rmsstr = "RMS  = "
		rmsvstr = "03.04"
		rmslbl = wx.StaticText (pnl2, wx.ID_ANY, rmsstr, pos = wx.Point (10,0))
		rmsvalue = wx.StaticText (pnl2, wx.ID_ANY, rmsvstr, pos = wx.Point (75,0))
		font = wx.Font (12, wx.DECORATIVE, wx.NORMAL, wx.BOLD)
		rmslbl.SetFont (font)
		rmsvalue.SetForegroundColour (wx.BLUE)
		hbox1.Add (rmslbl, 0, wx.ALL | wx.EXPAND, 15)
		hbox1.Add (rmsvalue, 0, wx.ALL | wx.EXPAND | wx.ALIGN_CENTER_HORIZONTAL, 15)
		flatmapB = wx.ToggleButton (pnl2, wx.ID_ANY, label = 'Flatmap', pos = wx.Point (10,30), size = (90, 30))
		settingsB = wx.Button (pnl2, wx.ID_ANY, label = 'Settings', pos = wx.Point (110, 30), size = (90,30))
		closeB = wx.Button (pnl2, wx.ID_ANY, label = 'Close', pos = wx.Point (400, 30), size = (75, 30))
		hbox2.Add (flatmapB, 0, wx.LEFT | wx.ALL | wx.ALIGN_CENTER_HORIZONTAL | wx.EXPAND, 15)
		hbox2.Add (settingsB, 0, wx.LEFT | wx.EXPAND | wx.ALIGN_CENTER_HORIZONTAL, 15)	
		hbox2.Add (closeB, 0, wx.RIGHT | wx.ALIGN_CENTER_HORIZONTAL)
		vbox.Add (hbox1, flag = wx.LEFT | wx.EXPAND | wx.ALL, border = 25)
		vbox.Add (hbox2, flag = wx.LEFT | wx.EXPAND | wx.ALL, border = 25)
		#--------------------------------#

		#------- Create Sizer -----------#
		sizer = wx.BoxSizer (wx.VERTICAL)
		sizer.Add (pnl1, 0, flag = wx.EXPAND | wx.ALL, border = 15)
		sizer.Add (pnl2, 0, flag = wx.EXPAND | wx.ALL, border = 15)
		#--------------------------------#


		self.Bind (wx.EVT_BUTTON, self.OnSettingClick, settingsB)
		self.Bind (wx.EVT_MENU, self.OnSettingClick, id = ID_SETTING)
		self.Bind (wx.EVT_MENU, self.OnQuit, id = ID_REGDM)
		self.Bind (wx.EVT_MENU, self.OnQuit, id = ID_BCKGRND)
		self.Bind (wx.EVT_MENU, self.OnQuit, id = ID_QUIT)
		self.Bind (wx.EVT_BUTTON, self.OnQuit, closeB)
		self.SetMenuBar (menubar)
		self.SetSizer (sizer)
		self.SetMinSize (self.GetBestSize())
		#self.SetMinSize ((400, 400))
		self.Centre ()
		self.Show (True)

	def OnQuit (self, event):
		self.GetParent().CloseFlatMap ()
	
	def OnSettingClick (self, event):
		chgsetting = Settings (None, -1, "WFS Camera :: Settings")
		chgsetting.ShowModal() 
		chgsetting.Destroy()
		
#create an empty dictionary
backgroundD = {}
# populate dictionary with units and conversion factors relative to sqmeter = 1.0
# this minimizes the total number of conversion factors
backgroundD['sqmeter']	    	= 1.0
backgroundD['sqmillimeter']   	= 1000000.0
backgroundD['sqcentimeter']   	= 10000.0
backgroundD['sqkilometer']  	= 0.000001
backgroundD['hectare']	    	= 0.0001
backgroundD['sqinch']	    	= 1550.003
backgroundD['sqfoot']	    	= 10.76391
backgroundD['sqyard']	    	= 1.19599
backgroundD['acre']		= 0.0002471054
backgroundD['sqmile']	        = 0.0000003861022

# create a sorted list for the combo boxes
backgroundList = sorted (backgroundD.keys())

if __name__ == "__main__":
    app = wx.App ()
    FlatMap (None, -1, 'Flat Map')
    app.MainLoop ()




