import wx

labels = "Positions Residuals RMS Positions Residuals RMS Positions Residuals RMS Flux Rate Frame".split()

class PlotTool (wx.Frame):
	def __init__(self, parent, id, title):
		wx.Frame.__init__(self, parent, id, title, size = (460, 190))
		self.panel = wx.Panel(self, -1)
	
		### Menubar ###
		menubar = wx.MenuBar ()
		ID_QUIT = wx.NewId()
        	file = wx.Menu ()
        	file.AppendSeparator ()
        	file.Append (ID_QUIT, "&Quit", "Terminate the program")

        	plot = wx.Menu ()
        	plot.Append (-1, "TTM Posistions", "Plot TTM Posistions")
        	plot.Append (-1, "TTM Residuals", "Plot TTM Residuals")
        	plot.Append (-1, "LODM Positions", "Plot LODM Positions")
        	plot.Append (-1, "DM Residuals", "Plot DM Residuals")
        	plot.Append (-1, "WFS Flux", "Plot WFS Flux")

        	menubar.Append (file, '&File')
        	menubar.Append (plot, '&Plot')
		
		### Statusbar ###
		self.CreateStatusBar()

		### Static Boxes ###	
		self.box1 = self.MakeStaticBoxSizer ("TTM Plots",   labels[0:3])
		self.box2 = self.MakeStaticBoxSizer ("HODM Plots",  labels[3:6])
		self.box3 = self.MakeStaticBoxSizer ("LODM Plots",  labels[6:9])
		self.box4 = self.MakeStaticBoxSizer ("WFS Plots",   labels[9:12])

		sizer = wx.BoxSizer (wx.HORIZONTAL)
		sizer.Add (self.box1, 0, wx.ALL, 10)
		sizer.Add (self.box2, 0, wx.ALL, 10)
		sizer.Add (self.box3, 0, wx.ALL, 10)
		sizer.Add (self.box4, 0, wx.ALL, 10)

		self.panel.SetSizer (sizer)
		
		self.Bind (wx.EVT_MENU, self.OnQuit, id = ID_QUIT)
		self.SetMenuBar (menubar)
		self.Centre()
		self.Show (True)

	def MakeStaticBoxSizer (self, boxlabel, itemlabels):
		box = wx.StaticBox (self.panel, -1, boxlabel)
		sizer = wx.StaticBoxSizer (box, wx.VERTICAL)
		
		for label in itemlabels:
			bw = BlockWindow (self.panel, label = label)
			if bw.id == 100:
				bw.button.Bind (wx.EVT_TOGGLEBUTTON, self.TTMPos, id = 100)
			elif bw.id == 101:
				bw.button.Bind (wx.EVT_TOGGLEBUTTON, self.TTMRes, id = 101)
			elif bw.id == 102:
				bw.button.Bind (wx.EVT_TOGGLEBUTTON, self.TTMRMS, id = 102)
			elif bw.id == 103:
				bw.button.Bind (wx.EVT_TOGGLEBUTTON, self.HODMPos, id = 103)
			elif bw.id == 104:
				bw.button.Bind (wx.EVT_TOGGLEBUTTON, self.HODMRes, id = 104)
			elif bw.id == 105:
				bw.button.Bind (wx.EVT_TOGGLEBUTTON, self.HODMRMS, id = 105)
			elif bw.id == 106:
				bw.button.Bind (wx.EVT_TOGGLEBUTTON, self.LODMPos, id = 106)
			elif bw.id == 107:
				bw.button.Bind (wx.EVT_TOGGLEBUTTON, self.LODMRes, id = 107)
			elif bw.id == 108:
				bw.button.Bind (wx.EVT_TOGGLEBUTTON, self.LODMRMS, id = 108)
			elif bw.id == 109:
				bw.button.Bind (wx.EVT_TOGGLEBUTTON, self.WFSFlux, id = 109)
			elif bw.id == 110:
				bw.button.Bind (wx.EVT_TOGGLEBUTTON, self.WFSRate, id = 110)
			elif bw.id == 111:
				bw.button.Bind (wx.EVT_TOGGLEBUTTON, self.WFSFrame, id = 111)
			else:	
				pass
			sizer.Add (bw, 0, wx.ALL, 2)
	
		return sizer

	def TTMPos (self, event):
		print "TTM Position Button Pressed"
	
	def TTMRes (self, event):
		print "TTM Residual Button Pressed"
	
	def TTMRMS (self, event):
		print "TTM RMS Button Pressed"
	
	def HODMPos (self, event):
		print "HODM Position Button Pressed"
	
	def HODMRes (self, event):
		print "HODM Residual Button Pressed"
	
	def HODMRMS (self, event):
		print "HODM RMS Button Pressed"

	def LODMPos (self, event):
		print "LODM Position Button Pressed"
	
	def LODMRes (self, event):
		print "LODM Residual Button Pressed"
	
	def LODMRMS (self, event):
		print "LODM RMS Button Pressed"
	
	def WFSFlux (self, event):
		print "WFS Flux Button Pressed"

	def WFSRate (self, event):
		print "WFS Rate Button Pressed"

	def WFSFrame (self, event):
		print "WFS Frame Button Pressed"
	
	def OnQuit (self, event):
		print "parent is", self.GetParent()
		if str(self.GetParent()) == "None":
			print "Window has no parent. Closing..."
			self.Close()
		else:
			print "Window has a parent. Calling parent function ..."
			self.GetParent().ClosePlotTools()
	
	
class BlockWindow (wx.Panel):
        def __init__ (self, parent, ID = -1, label = "", pos = wx.DefaultPosition, size=(100,25)):
                wx.Panel.__init__(self, parent, ID, pos, size, wx.NO_BORDER, label)
		self.id = wx.NewId()
                self.label = label
		self.button = wx.ToggleButton (self, self.id, self.label)
		print self.id
                ##self.SetBackgroundColour("white")
                #self.SetMinSize (size)
                #self.Bind (wx.EVT_PAINT, self.OnPaint)

###        def OnPaint (self, event):
###            sz = self.GetClientSize ()
###            dc = wx.PaintDC (self)
###            w,h = dc.GetTextExtent (self.label)
###            dc.SetFont (self.GetFont())
###            dc.DrawText (self.label, (sz.width-w)/2, (sz.height-h)/2)


if __name__ == "__main__":
	app = wx.App()
	PlotTool (None, -1, 'Plot Tool')
	app.MainLoop()
