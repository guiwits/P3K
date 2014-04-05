import wx

class Status (wx.Frame):
    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, id, title, size=(390, 350))
        panel = wx.Panel(self, -1)

        font = wx.SystemSettings_GetFont(wx.SYS_SYSTEM_FONT)
        font.SetPointSize(9)

        vbox = wx.BoxSizer(wx.VERTICAL)

        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        stfont = wx.SystemSettings_GetFont(wx.SYS_SYSTEM_FONT)
	stfont.SetPointSize (12)
        st1 = wx.StaticText(panel, -1, 'Palomar 3000 Status:')
        st1.SetFont(stfont)
        hbox1.Add(st1, 0, wx.EXPAND | wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 10)
        vbox.Add(hbox1, 0, wx.EXPAND, 10)

        vbox.Add((-1, 10))

        #hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        #st2 = wx.StaticText(panel, -1, 'Data:')
        #st2.SetFont(font)
        #hbox2.Add(st2, 0)
        #vbox.Add(hbox2, 0, wx.LEFT | wx.TOP, 10)

        #vbox.Add((-1, 10))

        hbox3 = wx.BoxSizer(wx.HORIZONTAL)
        tc2 = wx.TextCtrl(panel, -1, style=wx.TE_MULTILINE)
        hbox3.Add(tc2, 1, wx.EXPAND)
        vbox.Add(hbox3, 1, wx.LEFT | wx.RIGHT | wx.EXPAND, 10)

        vbox.Add((-1, 25))

        #hbox4 = wx.BoxSizer(wx.HORIZONTAL)
        #cb1 = wx.CheckBox(panel, -1, 'Case Sensitive')
        #cb1.SetFont(font)
        #hbox4.Add(cb1)
        #cb2 = wx.CheckBox(panel, -1, 'Nested Classes')
        #cb2.SetFont(font)
        #hbox4.Add(cb2, 0, wx.LEFT, 10)
        #cb3 = wx.CheckBox(panel, -1, 'Non-Project classes')
        #cb3.SetFont(font)
        #hbox4.Add(cb3, 0, wx.LEFT, 10)
        #vbox.Add(hbox4, 0, wx.LEFT, 10)

        #vbox.Add((-1, 25))

	hbox5 = wx.BoxSizer(wx.HORIZONTAL)
        #btn1 = wx.Button(panel, -1, 'Ok', size=(70, 30))
        #hbox5.Add(btn1, 0)
        btn2 = wx.Button(panel, -1, 'Close', size=(70, 30))
        hbox5.Add(btn2, 0, wx.LEFT | wx.BOTTOM , 5)
        vbox.Add(hbox5, 0, wx.ALIGN_RIGHT | wx.RIGHT, 10)

	self.Bind (wx.EVT_BUTTON, self.OnClose, btn2)
        panel.SetSizer(vbox)
        self.Centre()
        self.Show(True)

    def OnClose (self,event):
	self.GetParent().CloseStatus()

if __name__ == "__main__":
    app = wx.App ()
    Status (None, -1, 'Palomar 3000 Status')
    app.MainLoop ()
