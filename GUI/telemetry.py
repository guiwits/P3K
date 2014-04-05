import wx

class Telemetry (wx.Frame):
    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, id, title, size = (275, 220))

        vbox_top = wx.BoxSizer(wx.VERTICAL)
        panel = wx.Panel(self, -1)

        vbox = wx.BoxSizer(wx.VERTICAL)

	# panel 1

	panel1 = wx.Panel(panel, -1)
        grid1 = wx.GridSizer(1, 1)
	line = wx.StaticLine (panel1)
	grid1.Add (line, 0, wx.EXPAND)
        panel1.SetSizer(grid1)
        vbox.Add(panel1, 0, wx.ALL, 15)

        # panel 2

        panel2 = wx.Panel(panel, -1)
        hbox2 = wx.BoxSizer(wx.HORIZONTAL)

        sizer21 = wx.StaticBoxSizer(wx.StaticBox(panel2, -1, 'WFS Pixels'), orient=wx.VERTICAL)
        sizer21.Add(wx.RadioButton(panel2, -1, 'OFF             ', style=wx.RB_GROUP))
        sizer21.Add(wx.RadioButton(panel2, -1, 'ON            '))
        hbox2.Add(sizer21, 1, wx.RIGHT, 25)

        sizer22 = wx.StaticBoxSizer(wx.StaticBox(panel2, -1, 'DM Residuals'), orient=wx.VERTICAL)
        # we must define wx.RB_GROUP style, otherwise all 4 RadioButtons would be mutually exclusive
        sizer22.Add(wx.RadioButton(panel2, -1, 'OFF             ', style=wx.RB_GROUP))
        sizer22.Add(wx.RadioButton(panel2, -1, 'ON            '))
        hbox2.Add(sizer22, 1)

        panel2.SetSizer(hbox2)
        vbox.Add(panel2, 0, wx.BOTTOM, 9)

        # panel3

	panel3 = wx.Panel(panel, -1)
        hbox3 = wx.BoxSizer(wx.HORIZONTAL)

        sizer23 = wx.StaticBoxSizer(wx.StaticBox(panel3, -1, 'WFS Gains'), orient=wx.VERTICAL)
        sizer23.Add(wx.RadioButton(panel3, -1, 'OFF             ', style=wx.RB_GROUP))
        sizer23.Add(wx.RadioButton(panel3, -1, 'ON            '))
        hbox3.Add(sizer23, 1, wx.RIGHT, 25)

        sizer24 = wx.StaticBoxSizer(wx.StaticBox(panel3, -1, 'DM Gains'), orient=wx.VERTICAL)
        # we must define wx.RB_GROUP style, otherwise all 4 RadioButtons would be mutually exclusive
        sizer24.Add(wx.RadioButton(panel3, -1, 'OFF             ', style=wx.RB_GROUP))
        sizer24.Add(wx.RadioButton(panel3, -1, 'ON            '))
        hbox3.Add(sizer24, 1)

        panel3.SetSizer(hbox3)
        vbox.Add(panel3, 0, wx.BOTTOM, 9)


	# panel 4

        panel4 = wx.Panel(panel, -1)
        sizer4 = wx.BoxSizer(wx.HORIZONTAL)
	closeB = wx.Button (panel4, wx.ID_ANY, "Close", size = (50, -1))
        sizer4.Add((210, -1), 1, wx.EXPAND | wx.ALIGN_RIGHT)
        sizer4.Add(closeB, 0, wx.ALL, 0)

        panel4.SetSizer(sizer4)
        vbox.Add(panel4, 1, wx.BOTTOM, 9)

	self.Bind (wx.EVT_BUTTON, self.OnClose, closeB)
        vbox_top.Add(vbox, 1, wx.LEFT, 5)
        panel.SetSizer(vbox_top)
	#self.SetMinSize (self.GetBestSize())
	self.SetSize ((275,220))

        self.Centre()
        self.Show

    def OnClose (self, event):
	self.GetParent().CloseTelemetry()



if __name__ == "__main__":
	app = wx.App()
	Telemetry(None, -1, 'Telemetry Control')
	app.MainLoop()

