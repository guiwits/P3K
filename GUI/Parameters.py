#!/usr/bin/python

# parameters.py

import wx

class Parameters (wx.Frame):
    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, id, title, size=(350, 300))
        panel = wx.Panel(self, -1)

        menubar = wx.MenuBar()
        file = wx.Menu()
        view = wx.Menu()
        help = wx.Menu()
        
        file.Append(101, '&Quit', 'Quit application')

        menubar.Append(file, '&File')
        menubar.Append(view, '&View')
        menubar.Append(help, '&Help')

        self.SetMenuBar(menubar)

	sizer = wx.BoxSizer(wx.VERTICAL)

        self.SetMinSize((350, 300))
        self.CreateStatusBar()
        self.SetSizer(sizer)

        self.CentreOnScreen(10)
        self.Show()

if __name__ == '__main__': 
	app = wx.App()
	Parameters (None, -1, 'P3K Parameter Settings')
	app.MainLoop()

