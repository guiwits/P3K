import wx
import threading
import os

fifoname = '/tmp/motorfifo'

class WorkerThread (threading.Thread):
    def __init__(self, window):
        threading.Thread.__init__(self)
        self.window = window

        self.pipein = open (fifoname, 'r')

        if self.pipein == IOError:
            print "Error opening the named pipe\n"
            self.line = "Error"
        else:
            self.line = self.pipein.read (7)

    def stop (self):
        self.timeToQuit.set()

    def run (self):
        while 1:
            #self.line = self.pipein.read (7)
            self.line = self.pipein.readline()[:-1]
	    #print self.line
            wx.CallAfter (self.window.UpdatePosition, self.line)

class MotionControl (wx.Frame):
    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, id, title, size=(250, 175))
        panel = wx.Panel(self, -1)

        font = wx.SystemSettings_GetFont(wx.SYS_SYSTEM_FONT)

        vbox = wx.BoxSizer(wx.VERTICAL)

        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        st1 = wx.StaticText(panel, -1, 'Motor Name:     ')
        st1.SetFont(font)
        hbox1.Add(st1, 0, wx.RIGHT, 8)
        self.tc = wx.TextCtrl(panel, -1)
        hbox1.Add(self.tc, 1)
        vbox.Add(hbox1, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 10)

        vbox.Add((-1, 10))

        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        st2 = wx.StaticText(panel, -1, 'Motor Position: ')
        st2.SetFont(font)
        hbox2.Add(st2, 0, wx.RIGHT, 8)
        self.tc2 = wx.TextCtrl(panel, -1)
        hbox2.Add(self.tc2, 1)
        vbox.Add(hbox2, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 10)

        vbox.Add((-1, 10))

        hbox5 = wx.BoxSizer(wx.HORIZONTAL)
        btn1 = wx.Button(panel, -1, 'Start', size=(70, 30))
        hbox5.Add(btn1, 0)
        btn2 = wx.Button(panel, -1, 'Close', size=(70, 30))
        hbox5.Add(btn2, 0, wx.LEFT | wx.BOTTOM , 5)
        vbox.Add(hbox5, 0, wx.ALIGN_RIGHT | wx.RIGHT, 10)

        #self.tc.SetValue ("zeppo x axis 1")
        self.Bind (wx.EVT_BUTTON, self.OnCloseButton, id=btn2.GetId())
        self.Bind (wx.EVT_BUTTON, self.OnStartButton, id=btn1.GetId())

        panel.SetSizer(vbox)
        self.Centre()
        self.Show(True)

    def OnStartButton (self, event):
        thread = WorkerThread (self)
        thread.start()

    def OnCloseButton (self, event):
	print "parent is", self.GetParent()
        if str(self.GetParent()) == "None":
            print "Window has no parent. Closing..."
            self.Close()
            pass
        else:
            print "Window has a parent. Calling parent close function ..."
            self.GetParent().CloseMotors()
            pass


    def UpdatePosition (self, msg):
        self.tc.SetValue ("zeppo x axis 1")
	print msg
        self.tc2.SetValue (msg)

if __name__ == "__main__":
	app = wx.App()
	MotionControl(None, -1, 'P3K Motion Controller')
	app.MainLoop()
