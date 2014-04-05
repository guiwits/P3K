#!/usr/bin/python

# acqcam.py

import wx

class AcqCam (wx.Frame):
    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, id, title, size=(350, 300))
        panel = wx.Panel(self, -1)

        pnl1 = wx.Panel(self, -1)
        pnl1.SetBackgroundColour(wx.BLACK)
        pnl2 = wx.Panel(self, -1 )

        menubar = wx.MenuBar()
        file = wx.Menu()
        view = wx.Menu()
        help = wx.Menu()
        
        file.Append(101, '&Quit', 'Quit application')

        menubar.Append(file, '&File')
        menubar.Append(view, '&View')
        menubar.Append(help, '&Help')

        self.SetMenuBar(menubar)

        pause = wx.BitmapButton(pnl2, -1, wx.Bitmap('stock_media-pause.png'))
        play  = wx.BitmapButton(pnl2, -1, wx.Bitmap('stock_media-play.png'))
        stop  = wx.BitmapButton(pnl2, -1, wx.Bitmap('stock_media-stop.png'))
	close = wx.BitmapButton(pnl2, -1, wx.Bitmap('Button-Close.png'))

        vbox = wx.BoxSizer(wx.VERTICAL)
        hbox1 = wx.BoxSizer(wx.HORIZONTAL)

        hbox1.Add(pause, border=5)
        hbox1.Add(play, flag=wx.CENTER, border=5)
        hbox1.Add(stop, flag=wx.CENTER, border=5)
        hbox1.Add(close, flag=wx.EXPAND | wx.RIGHT) 
        hbox1.Add((-1, -1), 1)
	
        vbox.Add(hbox1, flag=wx.EXPAND | wx.BOTTOM, border=0)
        pnl2.SetSizer(vbox)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(pnl1, 1, flag=wx.EXPAND | wx.ALL, border = 10)
        sizer.Add(pnl2, flag=wx.EXPAND | wx.BOTTOM | wx.TOP, border=10)

	self.Bind (wx.EVT_MENU, self.OnClose, id=101)
        self.SetMinSize((650, 600))
        self.CreateStatusBar()
        self.SetSizer(sizer)

        self.CentreOnScreen(10)
        self.Show()
	
    def OnClose (self, event):
 	self.GetParent().CloseAcqCam () 	

if __name__ == '__main__': 
	app = wx.App()
	AcqCam (None, -1, 'Acquisition Camera Viewer')
	app.MainLoop()

