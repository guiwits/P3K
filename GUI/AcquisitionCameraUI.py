import wx
import threading
import os
import signal
import sys
import numpy
import struct
import socket
import time
import random
import wx.aui
import wx.lib.inspection

from VisionEgg import *
#start_default_logging(); watch_exceptions()
from VisionEgg.Core import *
import pygame
from pygame.locals import *

AOCAPORT = 10000
#AOCAPORT = 2157
ACAMPORT = 10001
ACAMSUBPORT = 10101
ACAMSTATUSPORT = 10002
HOST = "192.168.0.100"  
MSGLEN = 524292
BIAS = 0
BPP = 3                     # bytes per pixel

class StatusThread (threading.Thread):
    def __init__(self, window, threadID):
        threading.Thread__init__(self)
        self.window = window
        self.threadID = threadID
        self.socketobj = socket.socket (socket.AF_INET, socket.SOCK_STREAM)
        self.socketobj.setsockopt (socket.SOL_TCP, socket.TCP_NODELAY, 1)
        self.socketobj.connect ((HOST, ACAMSTATUSPORT))
        self.finished = threading.Event ()
        
    def stop (self):
        self.finished.set()
        
    def run (self):
        print 'Acquisition camera status thread started ...'
        
        while 1:
            msg = ''
            while len (msg) != MSGLEN:
                msg += self.socketobj.recv (MSGLEN)
                
                if msg == '':
                    raise RuntimeError, "socket connection broken"
           
           
            #wx.CallAfter (self.window.UpdateStatus, val1, val2, val3, valN) 
            if self.finished.isSet ():
                self.socketobj.close()
                break
        
        print 'Acquisition camera status thread stopped ...'
              
class DisplayThread (threading.Thread):
    def __init__(self, window, minSlider, maxSlider):
        threading.Thread.__init__(self, name="Acquisition Display")
        self.window = window

	self.minSlider = minSlider
	self.maxSlider = maxSlider
        self.socketobj = socket.socket (socket.AF_INET, socket.SOCK_STREAM)
        self.socketobj.setsockopt (socket.SOL_TCP, socket.TCP_NODELAY, 1)
        self.socketobj.connect ((HOST, ACAMSUBPORT))
        self.finished = threading.Event ()
	count = 0

        
    def stop (self):
        self.finished.set()
        
    def run (self):
        #print 'Starting acquisition camera display...'
        while not self.finished.isSet():

            #if self.finished.isSet ():
	        #print "Closing thread resources..."
                #self.socketobj.close()
                #break

            msg = ''
            while len (msg) < MSGLEN:
		chunk = self.socketobj.recv (MSGLEN-len(msg))
                
                if chunk == '':
                    raise RuntimeError, "socket connection broken"

		msg = msg + chunk

            #fmt = '<I262146H'
            #data = struct.unpack (fmt, msg)
            #frame_number = data[0]
            img = numpy.fromstring (msg[4:], dtype=numpy.uint16)
            
            """ Do any min/max adjusting here before it becomes """
            """ a 2D array as behavior of the functions changes """
            minval = self.minSlider.GetValue()
            maxval = self.maxSlider.GetValue()

            if minval > 0:
                img[img < minval] = minval
                
            if maxval < 4096:
                img[img > maxval] = maxval
            """ end of image array adjustment """
                
            ndimg = img.reshape ((512, 512))
            final_image = numpy.flipud (ndimg)  # correctly flip the image
    	
	    #self.window.CamCntrl.nbpanel.nb.UpdateDisplay        
            rgb = numpy.zeros ((512, 512, 3), dtype=numpy.ubyte)
            rgb[:,:,0] = rgb[:,:,1] = rgb[:,:,2] = final_image / 16.0   #16 = 2^12 / 256
	    print "Sending image to viewer..."
            wx.CallAfter (self.window.UpdateDisplay, rgb)

        #print 'P3K Acquisition Camara Viewing Thread: Exiting display thread ....'
            
    def join (self, timeout=None):
	self.finished.set()
	threading.Thread.join (self, timeout)


class WriteFITS (wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)
     
        sizer = wx.BoxSizer (wx.VERTICAL)
        vbox = wx.BoxSizer (wx.VERTICAL)
        grid = wx.GridSizer(2, 1, 10, 10)
        self.fitsTC = wx.TextCtrl (self, -1, size=(240, -1))
        self.fitsBtn = wx.Button (self, -1, 'Write File', size=(240, -1))
        grid.Add (self.fitsTC, 0, wx.ALIGN_CENTER_HORIZONTAL, 0)
        grid.Add (self.fitsBtn, 0, wx.ALIGN_CENTER_HORIZONTAL, 0)
        vbox.Add (grid, wx.TOP, 10)
        sizer.Add (vbox, 0, wx.RIGHT | wx.LEFT | wx.TOP, 80)
        
        self.SetSizer(sizer)
        self.Bind (wx.EVT_BUTTON, self.SendWriteCmd, self.fitsBtn)
        
    def SendWriteCmd (self, event):
        
        ''' set up socket connection '''
        fitsAddress = (HOST, AOCAPORT)
        fitsSocket = socket.socket (socket.AF_INET, socket.SOCK_STREAM, 0)
        fitsSocket.connect (fitsAddress)
        defaultString = 'write_fits\r'
        customString = 'write_fits ' + self.fitsTC.GetValue() + '\r'
        

        if self.fitsTC.GetValue() == '':
            print 'Nothing entered in text field. Writing default...'
            ''' send a default write fits to aoca '''
            #for line in defaultString:
            #fitsSocket.send (line)
            fitsSocket.send (defaultString)
            recvdata = fitsSocket.recv (512)
            if recvdata.find ('ERR:') == 0:
                print "ERR received sending write_fits."
                fitsSocket.close ()
            else:
                print "Received data: ", repr (recvdata)
                print "Writing default FITS file"
                fitsSocket.close ()
        else:
            print 'Text field has', self.fitsTC.GetValue(), 'as its filename.'
            ''' send over a requested write fits to aoca '''
            #for line in customString:
            #fitsSocket.send (line)
            fitsSocket.send (customString)
            recvdata = fitsSocket.recv (512)
            if recvdata.find ('ERR:') == 0:
                print "ERR received sending write_fits."
                fitsSocket.close ()
            else:
                print "Received data: ", repr (recvdata)
                print "Writing custom FITS file"
                fitsSocket.close ()
            
class CameraControl (wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)
        
	self.threadCreated = 0
	self.timer1 = wx.Timer (self)
	self.Bind (wx.EVT_TIMER, self.OnTimer1, self.timer1)

        sizer = wx.BoxSizer (wx.VERTICAL)
        vbox = wx.BoxSizer (wx.VERTICAL)
        grid = wx.GridSizer (6, 2, 5, 5)
        grid2 = wx.GridSizer (2, 1, 5, 5)
        minimumST = wx.StaticText (self, -1, '    Minimum:', size=(110, -1))    
        self.minSlider = wx.Slider (self, -1, 0, 0, 4096, (-1, -1), (170, -1), wx.SL_AUTOTICKS | wx.SL_HORIZONTAL | wx.SL_LABELS) #2^12 = 4096
        maximumST = wx.StaticText (self, -1, '    Maximum:', size=(110, -1))    
        self.maxSlider = wx.Slider (self, -1, 4096, 0, 4096, (-1, -1), (170, -1), wx.SL_AUTOTICKS | wx.SL_HORIZONTAL | wx.SL_LABELS)
        self.zoom = wx.ComboBox (self, -1, size=(230, -1), choices=["Regular", "Double"], value='Scale Control', 
                            style=wx.CB_DROPDOWN)
        self.displayBtn = wx.ToggleButton (self, -1, 'Display Video', size=(230, -1))
        
        #gammaST = wx.StaticText (self, -1, '    Gamma:', size=(110, -1))
        #self.gammaSlider = wx.Slider (self, -1, 1, 1, 4, (-1, -1), (170, -1), 
        #                               wx.SL_AUTOTICKS | wx.SL_HORIZONTAL | wx.SL_LABELS)
        
        grid.Add (minimumST, 0, wx.ALIGN_CENTER_VERTICAL)
        grid.Add (self.minSlider, 0, wx.ALIGN_CENTER, 0)
        grid.Add (maximumST, 0, wx.ALIGN_CENTER_VERTICAL)
        grid.Add (self.maxSlider, 0, wx.ALIGN_CENTER, 0)
        #grid.Add (gammaST, 0, wx.ALIGN_CENTER_VERTICAL)
        #grid.Add (self.gammaSlider, 0, wx.ALIGN_CENTER, 0)
        
        grid2.Add (self.zoom, 0, wx.ALIGN_CENTER, 0)
        grid2.Add (self.displayBtn, 0, wx.ALIGN_CENTER, 0)
        
        vbox.Add (grid)
        vbox.Add (grid2, 0, wx.ALL | wx.EXPAND, 15)
        
        sizer.Add (vbox, 0, wx.TOP, 20)
        self.SetSizer (sizer)
        
        self.Bind (wx.EVT_TOGGLEBUTTON, self.OnDisplayButton, self.displayBtn)
        
    def OnTimer1 (self, event):
        if self.displayBtn.GetValue () == False:
	    self.screen.close()

    def OnDisplayButton (self, event):
        if self.displayBtn.GetValue () == True:
            self.screen = VisionEgg.Core.Screen (size = (512, 512))
            self.screen.set (bgcolor = (0.0, 0.0, 0.0)) # Black (RGB)
            self.displayBtn.SetBackgroundColour (wx.Colour (0, 200, 0))
            self.displayBtn.ClearBackground ()
            self.displayBtn.Refresh ()
            #print 'Contrast slider at ', self.contrastSlider.GetValue()
            #print 'Brightness slider at ', self.brightnessSlider.GetValue()
            #print 'Combo box selection = ', self.zoom.GetValue()
	    if self.threadCreated == 0:
                self.thread = DisplayThread (self, self.minSlider, self.maxSlider)
                self.thread.start()
	        self.timer1.Start (1000, oneShot = False)
		self.threadCreated = 1
	    else:
    	        pass
        else:
            #self.displayBtn.SetBackgroundColour (wx.Colour (236, 233, 216))
            self.displayBtn.SetBackgroundColour (wx.NullColor)
            self.displayBtn.ClearBackground ()
            self.displayBtn.Refresh ()
            #self.thread.join ()    

    def UpdateDisplay (self, rgb):
	img = rgb
        if self.displayBtn.GetValue () == True:
            self.screen.put_pixels (pixels = img, position=(self.screen.size[0]/2.0, self.screen.size[1]/2.0), anchor="center")
            swap_buffers () # display what we've drawn
	else:
	    #self.thread.join()
            self.screen.close()
             

class RADECInfo (wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)
        
        sizer = wx.BoxSizer (wx.VERTICAL) 
        vbox = wx.BoxSizer (wx.VERTICAL)
        grid = wx.GridSizer (2, 3, 0, 5)
        grid2 = wx.GridSizer (1, 1, 5, 5)
        self.rast1 = wx.StaticText (self, -1, '    RA:')
        self.ratc1 = wx.StaticText (self, -1, '90.0', size=(100, -1), style=wx.TE_READONLY)
        self.ratc2 = wx.TextCtrl (self, -1, size=(100, -1))
        self.decst1 = wx.StaticText (self, -1, '    DEC:')
        self.dectc1 = wx.StaticText (self, -1, '0.0', size=(100, -1), style=wx.TE_READONLY)
        self.dectc2 = wx.TextCtrl (self, -1, size=(100, -1))
        self.bgBtn = wx.Button (self, -1, 'Take Background', size=(230, -1))
        grid.Add (self.rast1)
        grid.Add (self.ratc1)
        grid.Add (self.ratc2)
        grid.Add (self.decst1)
        grid.Add (self.dectc1)
        grid.Add (self.dectc2)
        grid2.Add (self.bgBtn, 0, wx.ALIGN_RIGHT | wx.ALL, 10)
        vbox.Add (grid)
        vbox.Add (grid2, 0, wx.ALL | wx.EXPAND, 10)
        sizer.Add (vbox, 0, wx.TOP, 20)
        self.SetSizer (sizer)
        
        self.Bind (wx.EVT_BUTTON, self.TakeBackground, self.bgBtn)
        
    def TakeBackground (self, event):
        if self.ratc2.GetValue() != '':
            print 'RA value is', self.ratc2.GetValue()
            self.ratc1.SetLabel(self.ratc2.GetValue())
        else:
            print 'Nothing entered for RA value...'
            
        if self.dectc2.GetValue() != '':
            print 'Dec value is', self.dectc2.GetValue()
            self.dectc1.SetLabel (self.dectc2.GetValue())
        else:
            print 'Nothing entered for Dec value...'
        
class AcamGui (wx.Frame):
    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent=parent, id=wx.ID_ANY, title="Acquisition Camera", size=(410, 615))

        #print wx.version()
        #wx.lib.inspection.InspectionTool().Show()
	global tid
    	tid = os.getpid()

        vbox_top = wx.BoxSizer (wx.VERTICAL)
        panel = wx.Panel (self, -1)

        # Parent panel (1 column)
        vbox = wx.BoxSizer (wx.VERTICAL)

        # status panel
        statuspanel = wx.Panel (panel, -1)
        statusgrid = wx.GridSizer (1, 1)

        statusgrid.Add (wx.TextCtrl (statuspanel, -1, pos=(-1, -1), size=(400,200), style=wx.TE_MULTILINE))
        statuspanel.SetSizer (statusgrid)
        vbox.Add (statuspanel, 0, wx.BOTTOM | wx.TOP, 10) 
        
        # Camera/BG Sub ON/OFF
        panel2 = wx.Panel (panel, -1, pos=(-1, -1), size=(200,200))
        hbox2 = wx.BoxSizer (wx.HORIZONTAL)
        
         # we must define wx.RB_GROUP style, otherwise all 4 RadioButtons would be mutually exclusive
        self.camOn = wx.RadioButton (panel2, -1, 'On                ', style=wx.RB_GROUP)
        self.camOff = wx.RadioButton (panel2, -1, 'Off')
        self.camOff.SetValue (True)
        self.bgdOn = wx.RadioButton (panel2, -1, 'On                ', style=wx.RB_GROUP)
        self.bgdOff = wx.RadioButton (panel2, -1, 'Off')
        self.bgdOff.SetValue (True)
        
        sizer21 = wx.StaticBoxSizer (wx.StaticBox(panel2, -1, 'Camera'), orient=wx.HORIZONTAL)
        sizer21.Add (self.camOn)
        sizer21.Add (self.camOff)
        hbox2.Add (sizer21, 0, wx.LEFT, 10) 

        sizer22 = wx.StaticBoxSizer (wx.StaticBox(panel2, -1, 'BGD Subtraction'), orient=wx.HORIZONTAL)
    
        sizer22.Add (self.bgdOn)
        sizer22.Add (self.bgdOff)
        hbox2.Add (sizer22, 0, wx.LEFT, 55)

        panel2.SetSizer (hbox2)
        vbox.Add (panel2, 0, wx.BOTTOM, 15)
        self.Bind (wx.EVT_RADIOBUTTON, self.CameraOnOff, self.camOn)
        self.Bind (wx.EVT_RADIOBUTTON, self.CameraOnOff, self.camOff)
        self.Bind (wx.EVT_RADIOBUTTON, self.BGDOnOff, self.bgdOn)
        self.Bind (wx.EVT_RADIOBUTTON, self.BGDOnOff, self.bgdOff)

        # Notebook Panel
        nbpanel = wx.Panel (panel, -1, pos=(-1, -1), size=(260, 300))
        #nbsizer = wx.StaticBoxSizer(wx.StaticBox(nbpanel, -1, name='Engineering Data'), wx.VERTICAL)
        #nbvbox = wx.BoxSizer (wx.VERTICAL) 
        nbsizer=wx.BoxSizer (wx.VERTICAL)
            
        """ Create the notebook """
        nb = wx.aui.AuiNotebook (nbpanel, -1, pos=(-1, -1), size=(300, 300))
        nb.SetMinSize (vbox.GetMinSize())
        
        """ Create Notebook Pages """    
        self.RADecPanel = RADECInfo (nb)
        self.CamCntrl = CameraControl (nb)
        self.WriteFits = WriteFITS (nb)
        
        """ Add pages to the notebook """
        nb.AddPage (self.CamCntrl, "Camera Control")
        nb.AddPage (self.RADecPanel, "BGD Automation")
        nb.AddPage (self.WriteFits, "Write FITS")
            
        #nbvbox.Add (nb, -1, wx.EXPAND, 5)
        #nbsizer.Add (nbvbox, -1, wx.EXPAND, 5)
        nbsizer.Add (nb, 2)

        nbpanel.SetSizer (nbsizer)
        vbox.Add (nbpanel, 0, wx.BOTTOM, 5)
    

        # Close Panel
        closepanel = wx.Panel (panel, -1, size=(360, -1))
        closesizer = wx.BoxSizer (wx.HORIZONTAL)
        closeButton = wx.Button (closepanel, -1, 'Close', size=(100, -1))
        closesizer.Add ((300, -1), 1, wx.ALIGN_RIGHT)
        #closesizer.Add (wx.Button (closepanel, -1, 'Close', size=(100, -1)))
        closesizer.Add (closeButton)
        closepanel.SetMaxSize (vbox.GetMinSize())

        closepanel.SetSizer (closesizer)
        vbox.Add (closepanel, 1, wx.BOTTOM, 9)
        
        # Close Events
        self.Bind (wx.EVT_BUTTON, self.OnCloseButton, closeButton)
        self.Bind (wx.EVT_MENU, self.OnClose)

        ### Add vbox to main sizer ###
        vbox_top.Add (vbox, 1, wx.LEFT, 5)
        panel.SetSizer (vbox_top)

        self.SetBackgroundColour(wx.Colour (236, 233, 216))
        self.Centre ()
        self.Show (True)
      
    def CameraOnOff (self, event):
        if self.camOn.GetValue() == True:
            print 'Camera on ... '
	    onSocket = socket.socket (socket.AF_INET, socket.SOCK_STREAM, 0)
	    onSocket.connect ((HOST, AOCAPORT))
	    onString = 'acam on\r'
	    onSocket.send (onString)
	    onRecvData = onSocket.recv (512)
	    if onRecvData.find ('ERR:') == 0:
	        print "ERR received turning on the Acquisition Camera..."
	        onSocket.close()
	    else:
	        print "Received data: ", repr (onRecvData)
	        print "Turning on the Aquisition Camera ...."
	        onSocket.close()

	    ### Future Status Thread Creation ###
            #self.thread = StatusThread (self, random.randrange (10000, 11000))
            #self.thread.start ()
        else:
            print 'Camera off ... '
	    offSocket = socket.socket (socket.AF_INET, socket.SOCK_STREAM, 0)
	    offSocket.connect ((HOST, AOCAPORT))
	    offString = 'acam off\r'
	    offSocket.send (offString)
	    offRecvData = offSocket.recv (512)
	    if offRecvData.find ('ERR:') == 0:
	        print "ERR received turning off the Acquisition Camera..."
	        offSocket.close()
	    else:
	        print "Received data: ", repr (offRecvData)
	        print "Turning the Aquisition Camera off ...."
	        offSocket.close()

	    ### Future Status Thread Deletion ###
            #self.thread.stop ()
            
    def BGDOnOff (self, event):
        if self.bgdOn.GetValue() == True:
            print 'Turning background subtraction on ...'
	    bgdOnSocket = socket.socket (socket.AF_INET, socket.SOCK_STREAM, 0)
	    bgdOnSocket.connect ((HOST, AOCAPORT))
	    onString = 'acam bgd=on\r'
	    bgdOnSocket.send (onString)
	    bgdOnRecvData = bgdOnSocket.recv (512)
	    if bgdOnRecvData.find ('ERR:') == 0:
	        print "ERR received turning on the background subtraction..."
	        bgdOnSocket.close()
	    else:
	        print "Received data: ", repr (bgdOnRecvData)
	        print "Turning off the background subtraction...."
	        bgdOnSocket.close()
        else:
            print 'Turning background subtraction off ...'
	    bgdOffSocket = socket.socket (socket.AF_INET, socket.SOCK_STREAM, 0)
	    bgdOffSocket.connect ((HOST, AOCAPORT))
	    offString = 'acam bgd=off\r'
	    bgdOffSocket.send (offString)
	    bgdOffRecvData = bgdOffSocket.recv (512)
	    if bgdOffRecvData.find ('ERR:') == 0:
	        print "ERR received turning off background subtraction..."
	        bgdOffSocket.close()
	    else:
	        print "Received data: ", repr (bgdOffRecvData)
	        print "Turning the background subtraction off ...."
	        bgdOffSocket.close()

    def UpdateStatus (self, val1, val2, val3, valN):
        print 'Inside UpdateStatus ...'
        ''' UPDATE VARIOUS FIELDS WITH APPROPRIATE STATUS '''
            
    def UpdateDisplay (self, rgb):
        print 'Inside UpdateDisplay ...'
        print self.CamCntrl.displayBtn.GetValue ()
	img = rgb
        if self.CamCntrl.displayBtn.GetValue () == True:
            screen.put_pixels (pixels = img, position=(screen.size[0]/2.0, screen.size[1]/2.0), anchor="center")
            swap_buffers () # display what we've drawn
	else:
            screen.clear()
            screen.close()
             
    def OnCloseButton (self, event):
        print 'Closing P3K Acquisition Control'
	if str (self.GetParent()) == "None":
            #self.GetParent().CloseAcqCam ()
	    if threading.active_count() >= 2:
	        self.CamCntrl.thread.stop()
	        self.CamCntrl.thread.join()
	    #os.kill (tid, signal.SIGKILL)
	    #screen.clear()			# Close the screen if it sill open
	    #screen.close()
            self.Destroy ()
            pass
        else:
            self.GetParent().CloseAcqCam ()
	    if threading.active_count() >= 2:
	        self.CamCntrl.thread.stop()
	        self.CamCntrl.thread.join()
            #os.kill (tid, signal.SIGKILL)
            self.Destroy ()
            self.Close()
            pass
        
    def OnClose (self, event):
        if str (self.GetParent()) == "None":
	    #os.kill (tid, signal.SIGKILL)
            self.GetParent().CloseAcqCam ()
            self.Destroy ()
            pass
        else:
	    #os.kill (tid, signal.SIGKILL)
            self.GetParent().CloseAcqCam ()
            pass
        
if __name__ == '__main__':
    app = wx.App()
    AcamGui (None, -1, 'Acquisition Camera Control')
    app.MainLoop()
    
