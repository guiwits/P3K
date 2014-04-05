import wx
import os
import subprocess
import signal
import sys
import time
import threading
import HodmResUI
import HodmPosUI

labels = "Positions Residuals RMS Positions Residuals RMS Positions Residuals RMS Flux Rate Frame".split()
ids = "1001 1002 1003 1004 1005 1006 1007 1008 1009 1010 1011 1012".split()

class HodmPosThread (threading.Thread):

    def __init__ (self, hodm_pos_proc, CloseHODMPos):
        threading.Thread.__init__(self)
        self.hodm_pos_proc = hodm_pos_proc
	self.CloseHODMPos = CloseHODMPos
	self.hodm_pos_alive = False

    def stop (self):
	self.hodm_pos_alive = False

    def run (self):
	self.hodm_pos_alive = True
	while self.hodm_pos_alive:
	    if self.hodm_pos_proc.poll() == None:
		#print "pos ..."
	        time.sleep (.5)
	    elif self.hodm_pos_alive == False:
		print "no hodm pos plot alive. exiting ..."
		break
	    else:
		wx.CallAfter (self.CloseHODMPos)
		self.hodm_pos_alive = False
		break

    	print "Exiting HODM Pos Thread ..."

class HodmResThread (threading.Thread):
    def __init__ (self, hodm_res_proc, CloseHODMRes):
        threading.Thread.__init__(self)
        self.hodm_res_proc = hodm_res_proc
	self.CloseHODMRes = CloseHODMRes
	self.alive = False

    def stop (self):
	self.alive = False

    def run (self):
	self.alive = True
	while self.alive:
	    if self.hodm_res_proc.poll() == None:
		#print "res ..."
	        time.sleep (.5)
	    elif self.alive == False:
		print "no hodm res plot alive. exiting ..."
		break
	    else:
		wx.CallAfter (self.CloseHODMRes)
		self.alive = False
		break
	
    	print "Exiting HODM Res Thread ..."

class LodmPosThread (threading.Thread):

    def __init__ (self, lodm_pos_proc, CloseLODMPos):
        threading.Thread.__init__(self)
        self.lodm_pos_proc = lodm_pos_proc
	self.CloseLODMPos = CloseLODMPos
	self.lodm_pos_alive = False

    def stop (self):
	self.lodm_pos_alive = False

    def run (self):
	self.lodm_pos_alive = True
	while self.lodm_pos_alive:
	    if self.lodm_pos_proc.poll() == None:
		#print "lodm pos ..."
	        time.sleep (.5)
	    elif self.lodm_pos_alive == False:
		print "no lodm pos plot alive. exiting ..."
		break
	    else:
		wx.CallAfter (self.CloseLODMPos)
		self.lodm_pos_alive = False
		break

    	print "Exiting LODM Pos Thread ..."

class LodmResThread (threading.Thread):
    def __init__ (self, lodm_res_proc, CloseLODMRes):
        threading.Thread.__init__(self)
        self.lodm_res_proc = lodm_res_proc
	self.CloseLODMRes = CloseLODMRes
	self.lodm_res_alive = False

    def stop (self):
	self.lodm_res_alive = False

    def run (self):
	self.lodm_res_alive = True
	while self.lodm_res_alive:
	    if self.lodm_res_proc.poll() == None:
		#print "lodm res ..."
	        time.sleep (.5)
	    elif self.lodm_res_alive == False:
		print "no lodm res plot alive. exiting ..."
		break
	    else:
		wx.CallAfter (self.CloseLODMRes)
		self.lodm_res_alive = False
		break
	
    	print "Exiting LODM Res Thread ..."

class PlotTool (wx.Frame):
    def __init__(self, parent, id, title): 
        wx.Frame.__init__(self, parent, id, title, size=(460, 190))
        self.panel = wx.Panel(self, - 1)
        
        ### Menubar ###
        menubar = wx.MenuBar ()
        ID_QUIT = wx.NewId()
        file = wx.Menu ()
        plotmb = wx.Menu ()
        file.AppendSeparator ()
        file.Append (ID_QUIT, "&Quit", "Terminate the program")
        plot = wx.Menu()
        
        ### TTM Submenu ###
        ttmMenu = wx.Menu()
        ttm1ID = wx.NewId()
        ttm2ID = wx.NewId()
        ttm3ID = wx.NewId()
        ttmMenu.Append (ttm1ID, "TTM Posistions", "Plot TTM Positions")
        self.Bind (wx.EVT_MENU, self.TTMPosMB, id=ttm1ID)
        ttmMenu.Append (ttm2ID, "TTM Residuals", "Plot TTM Residuals")
        self.Bind (wx.EVT_MENU, self.TTMResMB, id=ttm2ID)
        ttmMenu.Append (ttm3ID, "TTM RMS", "Plot TTM RMS")
        self.Bind (wx.EVT_MENU, self.TTMRMSMB, id=ttm3ID)
        
        ### HODM Submenu ###
        hoMenu = wx.Menu()
        hoMenu.Append (-1, "HODM Positions", "Plot HODM Positions")
        hoMenu.Append (-1, "HODM Residuals", "Plot HODM Residuals")
        hoMenu.Append (-1, "HODM RMS", "Plot HODM RMS")
        
        ### LODM Submenu ###
        loMenu = wx.Menu()
        loMenu.Append (-1, "LODM Positions", "Plot LODM Positions")
        loMenu.Append (-1, "LODM Residuals", "Plot LODM Residuals")
        loMenu.Append (-1, "LODM RMS", "Plot LODM RMS")
        
        ### WFS Submenu ###
        wfsMenu = wx.Menu()
        wfsMenu.Append (-1, "WFS Flux", "Plot WFS Flux")
        wfsMenu.Append (-1, "WFS Rate", "Plot WFS Camera Rate")
        wfsMenu.Append (-1, "WFS Frame", "Plot WFS Frame Count")
        
        ### Set up menu bars ###
        plotmb.AppendMenu(-1, 'TTM', ttmMenu)
        plotmb.AppendMenu(-1, 'HODM', hoMenu)
        plotmb.AppendMenu(-1, 'LODM', loMenu)
        plotmb.AppendMenu(-1, 'WFS', wfsMenu)
        plot.AppendMenu (-1, 'Plot', plot)
        menubar.Append (file, '&File')
        menubar.Append (plotmb, '&Plot')
        
        ### Statusbar ###
        self.CreateStatusBar()
        
        ### Static Boxes ###
        self.box1 = self.MakeStaticBoxSizer ("TTM Plots", labels[0:3], ids[0:3])
        self.box2 = self.MakeStaticBoxSizer ("HODM Plots", labels[3:6], ids[3:6])
        self.box3 = self.MakeStaticBoxSizer ("LODM Plots", labels[6:9], ids[6:9])
        self.box4 = self.MakeStaticBoxSizer ("WFS Plots", labels[9:12], ids[9:12])
        
        sizer = wx.BoxSizer (wx.HORIZONTAL)
        sizer.Add (self.box1, 0, wx.ALL, 10)
        sizer.Add (self.box2, 0, wx.ALL, 10)
        sizer.Add (self.box3, 0, wx.ALL, 10)
        sizer.Add (self.box4, 0, wx.ALL, 10)
        
	### lame hack to exit all processes upon parent window close ###
	self.hodm_pos_proc = None
	self.hodm_res_proc = None
	self.lodm_pos_proc = None
	self.lodm_res_proc = None

        self.panel.SetSizer (sizer)
        self.Bind (wx.EVT_MENU, self.OnQuit, id=ID_QUIT)
        self.Bind (wx.EVT_CLOSE, self.OnQuit)
        self.SetMenuBar (menubar)
        self.Centre()
        self.Show (True)
    
    def MakeStaticBoxSizer (self, boxlabel, itemlabels, itemids):
        box = wx.StaticBox (self.panel, - 1, boxlabel)
        sizer = wx.StaticBoxSizer (box, wx.VERTICAL)
        
        for label, id in zip(itemlabels, itemids):
            bw = BlockWindow (self.panel, label=label, id=id)

            if int (bw.id) == 1001:
                bw.button.Bind (wx.EVT_TOGGLEBUTTON, self.TTMPos, id=1001)
                pass
            elif int (bw.id) == 1002:
                bw.button.Bind (wx.EVT_TOGGLEBUTTON, self.TTMRes, id=1002)
                pass
            elif int (bw.id) == 1003:
                bw.button.Bind (wx.EVT_TOGGLEBUTTON, self.TTMRMS, id=1003)
                pass
            elif int (bw.id) == 1004:
                bw.button.Bind (wx.EVT_TOGGLEBUTTON, self.HODMPos, id=1004)
                pass
            elif int (bw.id) == 1005:
                bw.button.Bind (wx.EVT_TOGGLEBUTTON, self.HODMRes, id=1005)
                pass
            elif int (bw.id) == 1006:
                bw.button.Bind (wx.EVT_TOGGLEBUTTON, self.HODMRMS, id=1006)
                pass
            elif int (bw.id) == 1007:
                bw.button.Bind (wx.EVT_TOGGLEBUTTON, self.LODMPos, id=1007)
                pass
            elif int (bw.id) == 1008:
                bw.button.Bind (wx.EVT_TOGGLEBUTTON, self.LODMRes, id=1008)
                pass
            elif int (bw.id) == 1009:
                bw.button.Bind (wx.EVT_TOGGLEBUTTON, self.LODMRMS, id=1009)
                pass
            elif int (bw.id) == 1010:
                bw.button.Bind (wx.EVT_TOGGLEBUTTON, self.WFSFlux, id=1010)
                pass
            elif int (bw.id) == 1011:
                bw.button.Bind (wx.EVT_TOGGLEBUTTON, self.WFSRate, id=1011)
                pass
            elif int (bw.id) == 1012:
                bw.button.Bind (wx.EVT_TOGGLEBUTTON, self.WFSFrame, id=1012)
                pass
            else:    
                pass
        
            sizer.Add (bw, 0, wx.ALL, 2)
        return sizer

    def ClosePlotTools (self):
	### HODM POS
	if self.hodm_pos_proc is None:
            pass
        else:
            self.hpt.stop()
            time.sleep(1)
            os.kill (self.hodm_pos_proc.pid, signal.SIGTERM)

	### HODM RES
        if self.hodm_res_proc is None:
            pass
        else:
            self.hrt.stop()
            time.sleep(1)
            os.kill (self.hodm_res_proc.pid, signal.SIGTERM)
	    print self.lodm_pos_proc
	    print self.lodm_res_proc

	### LODM POS
        if self.lodm_pos_proc is None:
            pass
        else:
            self.lpt.stop()
            time.sleep (1)
            os.kill (self.lodm_pos_proc.pid, signal.SIGTERM)

	### LODM RES
        if self.lodm_res_proc is None:
            pass
        else:
            self.lrt.stop()
            time.sleep (1)
            os.kill (self.lodm_res_proc.pid, signal.SIGTERM)
    
    def OnQuit (self, event):

	if self.hodm_pos_proc is None:
	    pass
	else:
	    self.hpt.stop()
	    time.sleep(1)
	    os.kill (self.hodm_pos_proc.pid, signal.SIGTERM)

	if self.hodm_res_proc is None:
	    pass
	else:
	    self.hrt.stop()
	    time.sleep(1)
	    os.kill (self.hodm_res_proc.pid, signal.SIGTERM)

	if self.lodm_pos_proc is None:
	    pass
	else:
	    self.lpt.stop()
  	    time.sleep (1)
	    os.kill (self.lodm_pos_proc.pid, signal.SIGTERM)

	if self.lodm_res_proc is None:
	    pass
	else:
	    self.lrt.stop()
  	    time.sleep (1)
	    os.kill (self.lodm_res_proc.pid, signal.SIGTERM)

        if str (self.GetParent()) == "None":
            #print "Window has no parent. Closing..."
            #self.Close()
	    self.Destroy()
        else:
            print "Window has a parent. Calling parent close function ..."
            self.GetParent().ClosePlotTools()

        ### Button Event Listener ###
    def TTMPos (self, event):
        print "TTM Position Button Pressed"
        if self.box1.GetItem(0).GetWindow().button.GetValue() == True:
            self.box1.GetItem(0).GetWindow().button.SetBackgroundColour ('GREEN')
            self.box1.GetItem(0).GetWindow().button.ClearBackground()
            self.box1.GetItem(0).GetWindow().button.Refresh()
            pass
        else:
            self.box1.GetItem(0).GetWindow().button.SetBackgroundColour ('#ECEAD9')
            self.box1.GetItem(0).GetWindow().button.ClearBackground()
            self.box1.GetItem(0).GetWindow().button.Refresh()
            pass
        
    def TTMPosMB (self, event):
        print "TTM Position menubar selected"
        if self.box1.GetItem(0).GetWindow().button.GetValue() == False: 
            self.box1.GetItem(0).GetWindow().button.SetValue(True)
            self.box1.GetItem(0).GetWindow().button.SetBackgroundColour ('GREEN')
            self.box1.GetItem(0).GetWindow().button.ClearBackground()
            self.box1.GetItem(0).GetWindow().button.Refresh()
            pass
        else:
            self.box1.GetItem(0).GetWindow().button.SetValue(False)
            self.box1.GetItem(0).GetWindow().button.SetBackgroundColour ('#ECEAD9')
            self.box1.GetItem(0).GetWindow().button.ClearBackground()
            self.box1.GetItem(0).GetWindow().button.Refresh()
            pass
    
    ### Button Event Listener ###
    def TTMRes (self, event):
	   print "TTM Residual Button Pressed"
	   if self.box1.GetItem(1).GetWindow().button.GetValue() == True:
            self.box1.GetItem(1).GetWindow().button.SetBackgroundColour ('GREEN')
            self.box1.GetItem(1).GetWindow().button.ClearBackground()
            self.box1.GetItem(1).GetWindow().button.Refresh()
            pass
	   else:
            self.box1.GetItem(1).GetWindow().button.SetBackgroundColour ('#ECEAD9')
            self.box1.GetItem(1).GetWindow().button.ClearBackground()
            self.box1.GetItem(1).GetWindow().button.Refresh()
            pass

    ### Menubar Event Listener ###
    def TTMResMB (self, event):
        print "TTM Residual menubar selected"
        if self.box1.GetItem(1).GetWindow().button.GetValue() == False:
            self.box1.GetItem(1).GetWindow().button.SetValue(True)
            self.box1.GetItem(1).GetWindow().button.SetBackgroundColour ('GREEN')
            self.box1.GetItem(1).GetWindow().button.ClearBackground()
            self.box1.GetItem(1).GetWindow().button.Refresh()
            pass
        else:
            self.box1.GetItem(1).GetWindow().button.SetValue(False)
            self.box1.GetItem(1).GetWindow().button.SetBackgroundColour ('#ECEAD9')
            self.box1.GetItem(1).GetWindow().button.ClearBackground()
            self.box1.GetItem(1).GetWindow().button.Refresh()
            pass

    def TTMRMS (self, event):
        print "TTM RMS Button Pressed"
        if self.box1.GetItem(2).GetWindow().button.GetValue() == True:
            self.box1.GetItem(2).GetWindow().button.SetBackgroundColour ('GREEN')
            self.box1.GetItem(2).GetWindow().button.ClearBackground()
            self.box1.GetItem(2).GetWindow().button.Refresh()
            pass
        else:
            self.box1.GetItem(2).GetWindow().button.SetBackgroundColour ('#ECEAD9')
            self.box1.GetItem(2).GetWindow().button.ClearBackground()
            self.box1.GetItem(2).GetWindow().button.Refresh()
            pass
	
    def TTMRMSMB (self, event):
        print "TTM RMS menubar Pressed"
        if self.box1.GetItem(2).GetWindow().button.GetValue() == False: 
            self.box1.GetItem(2).GetWindow().button.SetValue(True)
            self.box1.GetItem(2).GetWindow().button.SetBackgroundColour ('GREEN')
            self.box1.GetItem(2).GetWindow().button.ClearBackground()
            self.box1.GetItem(2).GetWindow().button.Refresh()
            pass
        else:
            self.box1.GetItem(2).GetWindow().button.SetValue(False)
            self.box1.GetItem(2).GetWindow().button.SetBackgroundColour ('#ECEAD9')
            self.box1.GetItem(2).GetWindow().button.ClearBackground()
            self.box1.GetItem(2).GetWindow().button.Refresh()
            pass
	
    def HODMPos (self, event):
        if self.box2.GetItem(0).GetWindow().button.GetValue() == True:
            self.box2.GetItem(0).GetWindow().button.SetBackgroundColour ('GREEN')
            self.box2.GetItem(0).GetWindow().button.ClearBackground()
            self.box2.GetItem(0).GetWindow().button.Refresh()
	    self.hodm_pos_proc = subprocess.Popen (['python', 'HodmPosUI.py'])
	    self.hpt = HodmPosThread (self.hodm_pos_proc, self.CloseHODMPos)
	    self.hpt.start()
            pass
        else:
            self.box2.GetItem(0).GetWindow().button.SetBackgroundColour ('#ECEAD9')
            self.box2.GetItem(0).GetWindow().button.ClearBackground()
            self.box2.GetItem(0).GetWindow().button.Refresh()
	    self.hpt.stop()
	    time.sleep(1)
	    os.kill (self.hodm_pos_proc.pid, signal.SIGTERM)
            pass

    def CloseHODMPos (self):
        if self.box2.GetItem(0).GetWindow().button.GetValue() == True:
            self.box2.GetItem(0).GetWindow().button.SetValue (False)
            self.box2.GetItem(0).GetWindow().button.SetBackgroundColour ('#ECEAD9')
            self.box2.GetItem(0).GetWindow().button.ClearBackground()
            self.box2.GetItem(0).GetWindow().button.Refresh()
            pass

    def HODMRes (self, event):
        if self.box2.GetItem(1).GetWindow().button.GetValue() == True:
            self.box2.GetItem(1).GetWindow().button.SetBackgroundColour ('GREEN')
            self.box2.GetItem(1).GetWindow().button.ClearBackground()
            self.box2.GetItem(1).GetWindow().button.Refresh()
	    self.hodm_res_proc = subprocess.Popen (['python', 'HodmResUI.py'])
	    self.hrt = HodmResThread (self.hodm_res_proc, self.CloseHODMRes)
	    self.hrt.start()
            pass
        else:
            self.box2.GetItem(1).GetWindow().button.SetValue(False)
            self.box2.GetItem(1).GetWindow().button.SetBackgroundColour ('#ECEAD9')
            self.box2.GetItem(1).GetWindow().button.ClearBackground()
            self.box2.GetItem(1).GetWindow().button.Refresh()
	    self.hrt.stop()
	    time.sleep(1)
	    os.kill (self.hodm_res_proc.pid, signal.SIGTERM)
            pass
	
    def CloseHODMRes (self):
        if self.box2.GetItem(1).GetWindow().button.GetValue() == True:
            self.box2.GetItem(1).GetWindow().button.SetValue (False)
            self.box2.GetItem(1).GetWindow().button.SetBackgroundColour ('#ECEAD9')
            self.box2.GetItem(1).GetWindow().button.ClearBackground()
            self.box2.GetItem(1).GetWindow().button.Refresh()
            pass

    def HODMRMS (self, event):
        print "HODM RMS Button Pressed"
        if self.box2.GetItem(2).GetWindow().button.GetValue() == True:
            self.box2.GetItem(2).GetWindow().button.SetBackgroundColour ('GREEN')
            self.box2.GetItem(2).GetWindow().button.ClearBackground()
            self.box2.GetItem(2).GetWindow().button.Refresh()
            pass
        else:
            self.box2.GetItem(2).GetWindow().button.SetBackgroundColour ('#ECEAD9')
            self.box2.GetItem(2).GetWindow().button.ClearBackground()
            self.box2.GetItem(2).GetWindow().button.Refresh()
            pass

    def LODMPos (self, event):
        if self.box3.GetItem(0).GetWindow().button.GetValue() == True:
            self.box3.GetItem(0).GetWindow().button.SetBackgroundColour ('GREEN')
            self.box3.GetItem(0).GetWindow().button.ClearBackground()
            self.box3.GetItem(0).GetWindow().button.Refresh()
	    self.lodm_pos_proc = subprocess.Popen (['python', 'LodmPosUI.py'])
	    self.lpt = LodmPosThread (self.lodm_pos_proc, self.CloseLODMPos)
	    self.lpt.start()
            pass
        else:
            self.box3.GetItem(0).GetWindow().button.SetBackgroundColour ('#ECEAD9')
            self.box3.GetItem(0).GetWindow().button.ClearBackground()
            self.box3.GetItem(0).GetWindow().button.Refresh()
	    self.lpt.stop()
	    time.sleep (1)
	    os.kill (self.lodm_pos_proc.pid, signal.SIGTERM)
            pass

    def CloseLODMPos (self):
        if self.box3.GetItem(0).GetWindow().button.GetValue() == True:
            self.box3.GetItem(0).GetWindow().button.SetValue (False)
            self.box3.GetItem(0).GetWindow().button.SetBackgroundColour ('#ECEAD9')
            self.box3.GetItem(0).GetWindow().button.ClearBackground()
            self.box3.GetItem(0).GetWindow().button.Refresh()
            pass
	
    def LODMRes (self, event):
        if self.box3.GetItem(1).GetWindow().button.GetValue() == True:
            self.box3.GetItem(1).GetWindow().button.SetBackgroundColour ('GREEN')
            self.box3.GetItem(1).GetWindow().button.ClearBackground()
            self.box3.GetItem(1).GetWindow().button.Refresh()
	    self.lodm_res_proc = subprocess.Popen (['python', 'LodmResUI.py'])
	    self.lrt = LodmResThread (self.lodm_res_proc, self.CloseLODMRes)
	    self.lrt.start()
            pass
        else:
            self.box3.GetItem(1).GetWindow().button.SetBackgroundColour ('#ECEAD9')
            self.box3.GetItem(1).GetWindow().button.ClearBackground()
            self.box3.GetItem(1).GetWindow().button.Refresh()
	    self.lrt.stop()
	    time.sleep (1)
	    os.kill (self.lodm_res_proc.pid, signal.SIGTERM)
            pass
	
    def CloseLODMRes (self):
        if self.box3.GetItem(1).GetWindow().button.GetValue() == True:
            self.box3.GetItem(1).GetWindow().button.SetValue (False)
            self.box3.GetItem(1).GetWindow().button.SetBackgroundColour ('#ECEAD9')
            self.box3.GetItem(1).GetWindow().button.ClearBackground()
            self.box3.GetItem(1).GetWindow().button.Refresh()
            pass

    def LODMRMS (self, event):
        print "LODM RMS Button Pressed"
        if self.box3.GetItem(2).GetWindow().button.GetValue() == True:
            self.box3.GetItem(2).GetWindow().button.SetBackgroundColour ('GREEN')
            self.box3.GetItem(2).GetWindow().button.ClearBackground()
            self.box3.GetItem(2).GetWindow().button.Refresh()
            pass
        else:
            self.box3.GetItem(2).GetWindow().button.SetBackgroundColour ('#ECEAD9')
            self.box3.GetItem(2).GetWindow().button.ClearBackground()
            self.box3.GetItem(2).GetWindow().button.Refresh()
            pass
	
    def WFSFlux (self, event):
        print "WFS Flux Button Pressed"
        if self.box4.GetItem(0).GetWindow().button.GetValue() == True:
            self.box4.GetItem(0).GetWindow().button.SetBackgroundColour ('GREEN')
            self.box4.GetItem(0).GetWindow().button.ClearBackground()
            self.box4.GetItem(0).GetWindow().button.Refresh()
            pass
        else:
            self.box4.GetItem(0).GetWindow().button.SetBackgroundColour ('#ECEAD9')
            self.box4.GetItem(0).GetWindow().button.ClearBackground()
            self.box4.GetItem(0).GetWindow().button.Refresh()
            pass

    def WFSRate (self, event):
        print "WFS Rate Button Pressed"
        if self.box4.GetItem(1).GetWindow().button.GetValue() == True:
            self.box4.GetItem(1).GetWindow().button.SetBackgroundColour ('GREEN')
            self.box4.GetItem(1).GetWindow().button.ClearBackground()
            self.box4.GetItem(1).GetWindow().button.Refresh()
            pass
        else:
            self.box4.GetItem(1).GetWindow().button.SetBackgroundColour ('#ECEAD9')
            self.box4.GetItem(1).GetWindow().button.ClearBackground()
            self.box4.GetItem(1).GetWindow().button.Refresh()
            pass

    def WFSFrame (self, event):
        print "WFS Frame Button Pressed"
        if self.box4.GetItem(2).GetWindow().button.GetValue() == True:
            self.box4.GetItem(2).GetWindow().button.SetBackgroundColour ('GREEN')
            self.box4.GetItem(2).GetWindow().button.ClearBackground()
            self.box4.GetItem(2).GetWindow().button.Refresh()
            pass
        else:
            self.box4.GetItem(2).GetWindow().button.SetBackgroundColour ('#ECEAD9')
            self.box4.GetItem(2).GetWindow().button.ClearBackground()
            self.box4.GetItem(2).GetWindow().button.Refresh()
            pass

class BlockWindow (wx.Panel):
    def __init__ (self, parent, ID= - 1, label="", id="", pos=wx.DefaultPosition, size=(100, 25)):
        wx.Panel.__init__(self, parent, ID, pos, size, wx.NO_BORDER, label)
        self.id = id
        self.label = label
        self.button = wx.ToggleButton (self, int(self.id), self.label)
        self.button.SetBackgroundColour ('#ECEAD9')

if __name__ == "__main__":
	app = wx.App()
	PlotTool (None, -1, 'P3K Plot Tool')
	app.MainLoop()


