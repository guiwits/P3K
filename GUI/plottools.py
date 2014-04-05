#!/usr/bin/python

# plottools.py

import wx

class PlotTools (wx.Frame):
    def __init__(self, parent, id, title):
	wx.Frame.__init__(self, parent, id, title, size=(250, 180))

	menubar = wx.MenuBar()
	file = wx.Menu()
	edit = wx.Menu()
	help = wx.Menu()

	menubar.Append(file, '&File')
	menubar.Append(edit, '&Edit')
	menubar.Append(help, '&Help')
	self.SetMenuBar(menubar)

	wx.TextCtrl(self, -1)

	self.CentreOnScreen(10)
	self.Show()

if __name__ == '__main__':
    app = wx.App()
    PlotTools (None, -1, 'Plot Tools')
    app.MainLoop()


