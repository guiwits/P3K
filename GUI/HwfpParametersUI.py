import wx
import os
import threading
import socket
import struct
import binascii
import time
import numpy

HOST = "192.168.0.100"       
PORT = 10107                    # HWFP Params Subscriber Port
AOCAPORT = 10000                # AOCA Communication Port
MSGLEN = 888                    # Number of Bytes in hwfp_stat_t

servoParams = "self.hoProp self.loProp self.ttProp self.hoLeaky self.loLeaky self.hoLoOffload \
               self.hoTTOffload self.loTTOffload self.calHOFlat self.calCentroid".split()

class DataThread (threading.Thread):
    def __init__ (self, window):
        threading.Thread.__init__ (self)
        self.window = window
        self.finished = threading.Event()

    def stop (self):
        self.finished.set()

    def run (self):
        print "Starting hwfp parameters data acquisition ..."
        self.socketobj = socket.socket (socket.AF_INET, socket.SOCK_STREAM)
        self.socketobj.setsockopt (socket.SOL_TCP, socket.TCP_NODELAY, 1)
        
        try:
            self.socketobj.connect ((HOST, PORT))
        except socket.gaierror, e:
            print "Address-related error connecting to server %s" % e
            return -1
        except socket.error, e:
            print "Connection error: %s" % e
            return -1

        while 1:
            chunk = ''
            msg = ''

            while len (msg) < MSGLEN:
                try:
                    chunk = self.socketobj.recv (MSGLEN - len (msg))
                except socket.error, e:
                    print "Error recieving data: %s" % e

                if chunk == '':
                    raise RuntimeError, ":: Socket connection broken."

                msg = msg + chunk
                
                if self.finished.isSet():
                    self.socketobj.close()
                    break

            wx.CallAfter (self.window.UpdateHwfpStat, msg)   

            if self.finished.isSet():
                self.socketobj.close()
                break 
        
        print "Exiting the motor status thread ..."



class HWFPParameters (wx.Frame):
    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, id, title, size = (365, 730))

	self.threadActive = False

	#--- Timer for starting thread ---#
	self.timer1 = wx.Timer (self)
	self.timer1.Start (100, oneShot = True)
	#---			       ---#

        vbox_top = wx.BoxSizer (wx.VERTICAL)
        panel = wx.Panel(self, -1)

        vbox = wx.BoxSizer (wx.VERTICAL)

        # panel1
        panel1 = wx.Panel (panel, -1)
        grid1 = wx.GridBagSizer (0, 0)
	g1sizer = wx.StaticBoxSizer (wx.StaticBox (panel1, -1, 'HWFP Mode and Subaperature Flux'), 
					orient=wx.VERTICAL)
	vbox1 = wx.BoxSizer (wx.VERTICAL)

	modeText = wx.StaticText (panel1, -1, 'HWFP Mode:')
	filler = wx.StaticText (panel1, -1, '     ')
	self.modeVar = wx.StaticText (panel1, -1, '-----')
        grid1.Add (modeText, (0, 0), flag = wx.TOP | wx.LEFT | wx.RIGHT | wx.BOTTOM, border = 5)
        grid1.Add (self.modeVar, (0, 3), flag = wx.TOP | wx.LEFT | wx.RIGHT | wx.BOTTOM, border = 5)

	self.subApMinFluxText = wx.StaticText (panel1, -1, 'Subap Minimum Flux:')
	self.subApMinFluxVal = wx.StaticText (panel1, -1, '-----')
	self.subApMinFluxUserInput = wx.TextCtrl (panel1, -1, size = (60, 20), style = wx.TE_PROCESS_ENTER)
	self.subApApplyBtn = wx.Button (panel1, -1, "Apply", size = (60, 25))

	grid1.Add (self.subApMinFluxText, (1, 0), flag = wx.RIGHT | wx.LEFT | wx.BOTTOM, border = 5) 
        grid1.Add (filler, (0, 2), flag = wx.TOP | wx.LEFT | wx.RIGHT | wx.BOTTOM, border = 5)
	grid1.Add (self.subApMinFluxVal, (1, 3), flag = wx.RIGHT | wx.LEFT | wx.BOTTOM, border = 5) 
        grid1.Add (filler, (0, 4), flag = wx.TOP | wx.LEFT | wx.RIGHT | wx.BOTTOM, border = 3)
	grid1.Add (self.subApMinFluxUserInput, (1, 5), flag = wx.RIGHT | wx.LEFT | wx.BOTTOM, border = 5) 
	grid1.Add (self.subApApplyBtn, (2, 5),  flag = wx.RIGHT | wx.LEFT | wx.BOTTOM, border = 5)

	vbox1.Add (grid1)
	g1sizer.Add (vbox1, 0, wx.TOP | wx.BOTTOM | wx.LEFT | wx.RIGHT, 5)
        panel1.SetSizer (g1sizer)
        vbox.Add (panel1, 0, wx.TOP, 10)
	#---END PANDEL 1---#

        # panel2
        panel2 = wx.Panel(panel, -1)
        grid2= wx.GridBagSizer(0, 0)
	#g2sizer = wx.StaticBoxSizer (wx.StaticBox (panel2, -1, "Configuration Files"), orient=wx.VERTICAL)
	vbox2 = wx.BoxSizer (wx.VERTICAL)

	#--- Radio button set-up ---#
	self.coRB = wx.RadioButton (panel2, -1, "Centroid Offset:", style = wx.RB_GROUP)
	self.pgRB = wx.RadioButton (panel2, -1, "Pixel Gains:")
	self.poRB = wx.RadioButton (panel2, -1, "Pixel Offsets:")
	self.reconstRB = wx.RadioButton (panel2, -1, "Reconstructor:")
	self.clRB = wx.RadioButton (panel2, -1, "Centroid Linearity:")
	self.isRB = wx.RadioButton (panel2, -1, "Illuminated Subaps:           ")
	self.homapRB = wx.RadioButton (panel2, -1, "HODM Map:")
	self.lomapRB = wx.RadioButton (panel2, -1, "LODM Map:")
	self.hoofflRB = wx.RadioButton (panel2, -1, "HO Offload:")
	self.caludRB = wx.RadioButton (panel2, -1, "Cal Update:")

	#--- Static Text set-up ---#
	self.coVal = wx.StaticText (panel2, -1, '----------')
	self.pgVal = wx.StaticText (panel2, -1, '----------')
	self.poVal = wx.StaticText (panel2, -1, '----------')
	self.reconstVal = wx.StaticText (panel2, -1, '----------')
	self.clVal = wx.StaticText (panel2, -1, '----------')
	self.isVal = wx.StaticText (panel2, -1, '----------')
	self.homapVal = wx.StaticText (panel2, -1, '----------')
	self.lomapVal = wx.StaticText (panel2, -1, '----------')
	self.hoofflVal = wx.StaticText (panel2, -1, '----------')
	self.caludVal = wx.StaticText (panel2, -1, '----------')
	self.f2 = wx.StaticText (panel2, -1, "     ")

	grid2.Add (self.coRB, (0, 0), flag = wx.LEFT | wx.TOP | wx.RIGHT, border = 5)
	grid2.Add (self.pgRB, (1, 0), flag = wx.LEFT | wx.RIGHT, border = 5)
	grid2.Add (self.poRB, (2, 0), flag = wx.LEFT | wx.RIGHT, border = 5)
	grid2.Add (self.reconstRB, (3, 0), flag = wx.LEFT | wx.RIGHT, border = 5)
	grid2.Add (self.clRB, (4, 0), flag = wx.LEFT | wx.RIGHT, border = 5)
	grid2.Add (self.isRB, (5, 0), flag = wx.LEFT | wx.RIGHT, border = 5)
	grid2.Add (self.homapRB, (6, 0), flag = wx.LEFT | wx.RIGHT, border = 5)
	grid2.Add (self.lomapRB, (7, 0), flag = wx.LEFT | wx.RIGHT, border = 5)
	grid2.Add (self.hoofflRB, (8, 0), flag = wx.LEFT | wx.RIGHT, border = 5)
	grid2.Add (self.caludRB, (9, 0), flag = wx.LEFT | wx.RIGHT, border = 5)
	grid2.Add (self.coVal, (0, 2), flag = wx.LEFT | wx.RIGHT, border = 5)
	grid2.Add (self.pgVal, (1, 2), flag = wx.LEFT | wx.RIGHT, border = 5)
	grid2.Add (self.poVal, (2, 2), flag = wx.LEFT | wx.RIGHT, border = 5)
	grid2.Add (self.reconstVal, (3, 2), flag = wx.LEFT | wx.RIGHT, border = 5)
	grid2.Add (self.clVal, (4, 2), flag = wx.LEFT | wx.RIGHT, border = 5)
	grid2.Add (self.isVal, (5, 2), flag = wx.LEFT | wx.RIGHT, border = 5)
	grid2.Add (self.homapVal, (6, 2), flag = wx.LEFT | wx.RIGHT, border = 5)
	grid2.Add (self.lomapVal, (7, 2), flag = wx.LEFT | wx.RIGHT, border = 5)
	grid2.Add (self.hoofflVal, (8, 2), flag = wx.LEFT | wx.RIGHT, border = 5)
	grid2.Add (self.caludVal, (9, 2), flag = wx.LEFT | wx.RIGHT | wx.BOTTOM, border = 5)

	self.fileBtn = wx.Button (panel2, -1, "Load File", size = (95, 25))
	grid2.Add (self.f2, (10, 0),  flag = wx.LEFT | wx.RIGHT, border = 5)
	grid2.Add (self.f2, (10, 1),  flag = wx.LEFT | wx.RIGHT, border = 5)
	grid2.Add (self.fileBtn, (10, 2), flag = wx.LEFT | wx.RIGHT | wx.TOP, border = 5)

	vbox2.Add (grid2)
	#g2sizer.Add (vbox2, 0, wx.TOP | wx.BOTTOM | wx.LEFT, 5)

        #panel2.SetSizer(g2sizer)
        panel2.SetSizer(vbox2)
        vbox.Add (panel2, 0, wx.BOTTOM | wx.TOP, 10)
	#---END PANDEL 2---#

        # panel3
        panel3 = wx.Panel (panel, -1)
        grid3 = wx.GridBagSizer (0, 0)
        grid4 = wx.GridBagSizer (0, 0)
	g3sizer = wx.StaticBoxSizer (wx.StaticBox (panel3, -1, "Servo Gains"), orient=wx.VERTICAL)
	vbox3 = wx.BoxSizer (wx.VERTICAL)

	self.hoPropGainText = wx.StaticText (panel3, -1, 'HO Proportional Gain \tK0:')
	self.hoPropGainVal = wx.StaticText (panel3, -1, '  -----  ')
	self.hoPropGainUserInput = wx.TextCtrl (panel3, -1, size = (60, 20))
	self.loPropGainText = wx.StaticText (panel3, -1, 'LO Proportional Gain \tK1:')
	self.loPropGainVal = wx.StaticText (panel3, -1, '  -----  ')
	self.loPropGainUserInput = wx.TextCtrl (panel3, -1, size = (60, 20))
	self.ttPropGainText = wx.StaticText (panel3, -1, 'TT Proportional Gain \tK2:')
	self.ttPropGainVal = wx.StaticText (panel3, -1, '  -----  ')
	self.ttPropGainUserInput = wx.TextCtrl (panel3, -1, size = (60, 20))
	self.hoLeakyGainText = wx.StaticText (panel3, -1, 'HO Leaky Gain \t\tK3:')
	self.hoLeakyGainVal = wx.StaticText (panel3, -1, '  -----  ')
	self.hoLeakyGainUserInput = wx.TextCtrl (panel3, -1, size = (60, 20))
	self.loLeakyGainText = wx.StaticText (panel3, -1, 'LO Leaky Gain \t\tK4:')
	self.loLeakyGainVal = wx.StaticText (panel3, -1, '  -----  ')
	self.loLeakyGainUserInput = wx.TextCtrl (panel3, -1, size = (60, 20))
	self.hoLoOffloadGainText = wx.StaticText (panel3, -1, 'HO-LO Offload Gain \tK5:')
	self.hoLoOffloadGainVal = wx.StaticText (panel3, -1, '  -----  ')
	self.hoLoOffloadGainUserInput = wx.TextCtrl (panel3, -1, size = (60, 20))
	self.hoTTOffloadGainText = wx.StaticText (panel3, -1, 'HO TT Offload Gain \tK6:')
	self.hoTTOffloadGainVal = wx.StaticText (panel3, -1, '  -----  ')
	self.hoTTOffloadGainUserInput = wx.TextCtrl (panel3, -1, size = (60, 20))
	self.loTTOffloadGainText = wx.StaticText (panel3, -1, 'LO TT Offload Gain \tK7:')
	self.loTTOffloadGainVal = wx.StaticText (panel3, -1, '  -----  ')
	self.loTTOffloadGainUserInput = wx.TextCtrl (panel3, -1, size = (60, 20))
	self.calHOFlatGainText = wx.StaticText (panel3, -1, 'LO TT Offload Gain \tK8:')
	self.calHOFlatGainVal = wx.StaticText (panel3, -1, '  -----  ')
	self.calHOFlatGainUserInput = wx.TextCtrl (panel3, -1, size = (60, 20))
	self.calCentroidGainText = wx.StaticText (panel3, -1, 'Cal Centroid Gain \t\tK9:')
	self.calCentroidGainVal = wx.StaticText (panel3, -1, '  -----  ')
	self.calCentroidGainUserInput = wx.TextCtrl (panel3, -1, size = (60, 20))
	''' wx.TE_READONLY to make text read-only '''

	grid3.Add (self.hoPropGainText, (0, 0), flag = wx.TOP | wx.LEFT | wx.RIGHT, border = 5) 
	grid3.Add (self.hoPropGainVal, (0, 1), flag = wx.TOP | wx.LEFT | wx.RIGHT, border = 5) 
	grid3.Add (self.hoPropGainUserInput, (0, 3), flag = wx.TOP | wx.LEFT | wx.RIGHT, border = 5) 
	grid3.Add (self.loPropGainText, (1, 0), flag = wx.LEFT | wx.RIGHT, border = 5) 
	grid3.Add (self.loPropGainVal, (1, 1), flag = wx.LEFT | wx.RIGHT, border = 5) 
	grid3.Add (self.loPropGainUserInput, (1, 3), flag = wx.LEFT | wx.RIGHT, border = 5) 
	grid3.Add (self.ttPropGainText, (2, 0), flag = wx.LEFT | wx.RIGHT, border = 5)
	grid3.Add (self.ttPropGainVal, (2, 1), flag = wx.LEFT | wx.RIGHT, border = 5)
	grid3.Add (self.ttPropGainUserInput, (2, 3), flag = wx.LEFT | wx.RIGHT, border = 5)
	grid3.Add (self.hoLeakyGainText, (3, 0), flag = wx.LEFT | wx.RIGHT, border = 5)
	grid3.Add (self.hoLeakyGainVal, (3, 1), flag = wx.LEFT | wx.RIGHT, border = 5)
	grid3.Add (self.hoLeakyGainUserInput, (3, 3), flag = wx.LEFT | wx.RIGHT, border = 5)
	grid3.Add (self.loLeakyGainText, (4, 0), flag = wx.LEFT | wx.RIGHT, border = 5)
	grid3.Add (self.loLeakyGainVal, (4, 1), flag = wx.LEFT | wx.RIGHT, border = 5)
	grid3.Add (self.loLeakyGainUserInput, (4, 3), flag = wx.LEFT | wx.RIGHT, border = 5)
	grid3.Add (self.hoLoOffloadGainText, (5, 0), flag = wx.LEFT | wx.RIGHT, border = 5)
	grid3.Add (self.hoLoOffloadGainVal, (5, 1), flag = wx.LEFT | wx.RIGHT, border = 5)
	grid3.Add (self.hoLoOffloadGainUserInput, (5, 3), flag = wx.LEFT | wx.RIGHT, border = 5)
	grid3.Add (self.hoTTOffloadGainText, (6, 0), flag = wx.LEFT | wx.RIGHT, border = 5) 
	grid3.Add (self.hoTTOffloadGainVal, (6, 1), flag = wx.LEFT | wx.RIGHT, border = 5) 
	grid3.Add (self.hoTTOffloadGainUserInput, (6, 3), flag = wx.LEFT | wx.RIGHT, border = 5) 
	grid3.Add (self.loTTOffloadGainText, (7, 0), flag = wx.LEFT | wx.RIGHT, border = 5) 
	grid3.Add (self.loTTOffloadGainVal, (7, 1), flag = wx.LEFT | wx.RIGHT, border = 5) 
	grid3.Add (self.loTTOffloadGainUserInput, (7, 3), flag = wx.LEFT | wx.RIGHT, border = 5) 
	grid3.Add (self.calHOFlatGainText, (8, 0), flag = wx.LEFT | wx.RIGHT, border = 5)
	grid3.Add (self.calHOFlatGainVal, (8, 1), flag = wx.LEFT | wx.RIGHT, border = 5)
	grid3.Add (self.calHOFlatGainUserInput, (8, 3), flag = wx.LEFT | wx.RIGHT, border = 5)
	grid3.Add (self.calCentroidGainText, (9, 0), flag = wx.LEFT | wx.RIGHT, border = 5)
	grid3.Add (self.calCentroidGainVal, (9, 1), flag = wx.LEFT | wx.RIGHT, border = 5)
	grid3.Add (self.calCentroidGainUserInput, (9, 3),flag = wx.LEFT | wx.RIGHT, border = 5)

	f2 = wx.StaticText (panel3, -1, "      ")
	self.applyBtn = wx.Button (panel3, -1, "Apply", size = (95, 25))
	grid4.Add (f2, (0, 0), flag = wx.LEFT | wx.RIGHT | wx.TOP, border = 10)
	grid4.Add (f2, (0, 1), flag = wx.LEFT | wx.RIGHT | wx.TOP, border = 10)
	grid4.Add (f2, (0, 2), flag = wx.LEFT | wx.RIGHT | wx.TOP, border = 10)
	grid4.Add (f2, (0, 3), flag = wx.LEFT | wx.RIGHT | wx.TOP, border = 10)
	grid4.Add (f2, (0, 4), flag = wx.LEFT | wx.RIGHT | wx.TOP, border = 10)
	grid4.Add (self.applyBtn, (0, 5), flag = wx.LEFT | wx.RIGHT | wx.TOP, border = 5)

	vbox3.Add (grid3)
	vbox3.Add (grid4)
	g3sizer.Add (vbox3, 0, wx.TOP | wx.BOTTOM | wx.LEFT, 5)
        panel3.SetSizer(g3sizer)
        vbox.Add (panel3, 0, wx.BOTTOM, 10)
	#---END PANDEL 3---#
	### Panel 4 is a sub panel inside 3 to help with alignment ###

        # panel 5
        panel5 = wx.Panel (panel, -1)
        grid5 = wx.GridBagSizer (0, 0)
	
	f5 = wx.StaticText (panel5, -1, "         ")
	telemSettingsBtn = wx.Button (panel5, -1, "Settings", size = (95, 25))

	grid5.Add (f5, (0, 0), flag = wx.LEFT | wx.RIGHT, border = 5)
	grid5.Add (f5, (0, 1), flag = wx.LEFT | wx.RIGHT, border = 5)
	grid5.Add (f5, (0, 2), flag = wx.LEFT | wx.RIGHT, border = 5)
	grid5.Add (f5, (0, 3), flag = wx.LEFT | wx.RIGHT, border = 5)
	grid5.Add (f5, (0, 4), flag = wx.LEFT | wx.RIGHT, border = 5)
	grid5.Add (telemSettingsBtn, (0, 5), flag = wx.RIGHT | wx.LEFT, border = 5)

        panel5.SetSizer (grid5)
        vbox.Add (panel5, 1, wx.TOP | wx.BOTTOM, 10)
	#---END PANDEL 4---#

	#--- BIND ---#
	self.Bind (wx.EVT_BUTTON, self.LoadFile, self.fileBtn)
	self.Bind (wx.EVT_BUTTON, self.ApplyServoGains, self.applyBtn)
	self.Bind (wx.EVT_BUTTON, self.ApplySubapFlux, self.subApApplyBtn)
	#self.subApMinFluxUserInput.Bind (wx.EVT_KEY_DOWN, self.ApplySubapFlux)
	self.Bind (wx.EVT_TIMER, self.ConnectToSocket, self.timer1)
	self.Bind (wx.EVT_CLOSE, self.OnQuit)
	
        vbox_top.Add (vbox, 1, wx.LEFT, 10)
        panel.SetSizer(vbox_top)
	#self.SetMinSize (self.GetBestSize())
	self.SetMinSize ((365, 720))

        self.Centre()
        self.Show (True)

    def ConnectToSocket (self, event):
        cmd = "hwfp\r"			### force it to update the status
        self.thread = DataThread (self)
        self.thread.start()
	time.sleep (1)
	if self.thread.isAlive() == True:
            self.threadActive = True
            self.SendCmd (cmd)
	else:
            self.threadActive = False
	
    def SendCmd (self, command):
        ''' set up socket connection to aoca '''
        self.command = command
        aocaAddress = (HOST, AOCAPORT)
        self.aocaSocket = socket.socket (socket.AF_INET, socket.SOCK_STREAM, 0)
        self.aocaSocket.connect (aocaAddress)
	
	print "SendCmd sending %s\n" % self.command
        self.aocaSocket.send (self.command)
	recvdata = self.aocaSocket.recv (512)

    def ApplySubapFlux (self, event):
	'''
	keycode = event.GetKeyCode ()
	print keycode
	sav = "%s%s" % (self.subApMinFluxUserInput.GetValue(), chr (keycode))
	self.subApMinFluxUserInput.SetValue (sav)

	if keycode  == wx.WXK_RETURN:
	    smf = sav
	    print smf
	    aocaCmd = "hwfp SUBAP_MIN_FLUX = %s\r" % smf
	    if self.threadActive == True:
	        self.SendCmd (aocaCmd)
	    self.subApMinFluxUserInput.SetValue ("")
	'''
	smf = self.subApMinFluxUserInput.GetValue()
	aocaCmd = "hwfp SUBAP_MIN_FLUX = %s\r" % smf
	print aocaCmd
	if self.threadActive == True:
	    self.SendCmd (aocaCmd)
	self.subApMinFluxUserInput.SetValue ("")

    def LoadFile (self, event):

	opendir = ""

        ''' determine which radio box is checked '''
	if self.coRB.GetValue() == True:
	    opendir = "/p3k/tables/cent_offsets"
	    cmd = "cent_offsets"
	elif self.pgRB.GetValue() == True:
	    opendir = "/p3k/tables/pix_gains"
	    cmd = "pix_gains"
	elif self.poRB.GetValue() == True:
	    opendir = "/p3k/tables/pix_offsets"
	    cmd = "pix_offsets"
	elif self.reconstRB.GetValue() == True:
	    opendir = "/p3k/tables/reconst"
	    cmd = "reconst"
	elif self.clRB.GetValue() == True:
	    opendir = "/p3k/tables/cent_lin"
	    cmd = "cent_lin"
	elif self.isRB.GetValue() == True:
	    opendir = "/p3k/tables/ill_subaps"
	    cmd = "ill_subaps"
	elif self.homapRB.GetValue() == True:
	    opendir = "/p3k/tables/hodm_map"
	    cmd = "hodm_map"
	elif self.lomapRB.GetValue() == True:
	    opendir = "/p3k/tables/lodm_map"
	    cmd = "lodm_map"
	elif self.hoofflRB.GetValue() == True:
	    opendir = "/p3k/tables/ho_offload"
	    cmd = "ho_offload"
	elif self.caludRB.GetValue() == True:
	    opendir = "/p3k/tables/cal_update"
	    cmd = "cal_update"
	else:
	    pass

	#wildcard = "All Files (*.*)|*.*"
	dialog = wx.FileDialog (None, "Choose a file", opendir, "", "*", wx.OPEN)
	if dialog.ShowModal() == wx.ID_OK:
	    filePath = dialog.GetPath()
	    aocaCmd = "hwfp %s = %s\r" % (cmd, filePath)
	    self.SendCmd (aocaCmd)

	dialog.Destroy()
    ''' End LoadFile '''

    def ApplyServoGains (self, event):
	KCur = [0,0,0,0,0,0,0,0,0,0]
	KNew = [0,0,0,0,0,0,0,0,0,0]
	K = [0,0,0,0,0,0,0,0,0,0]

	for i in range (len (servoParams)):
	    currentValue = "%sGainVal.GetLabel()" % (servoParams[i])
	    newValue = "%sGainUserInput.GetValue()" % (servoParams[i])
	    KCur[i] = eval (currentValue)
	    KNew[i] = eval (newValue)
	    if KNew[i] != "":
	        K[i] = str (KNew[i])
	    else:
		if KCur[i] == "  -----  ":
		    # just do nothing is it's ---- #
		    #K[i] = "0.0"
		    pass
		else:
	            K[i] = str (KCur[i])

	aocaCmd = "hwfp K0=%s K1=%s K2=%s K3=%s K4=%s K5=%s K6=%s K7=%s K8=%s K9=%s" \
		  % (K[0], K[1], K[2], K[3], K[4], K[5], K[6], K[7], K[8], K[9])

	self.SendCmd (aocaCmd)

	for i in range (len (servoParams)):
	    changeVal = "%sGainUserInput.SetValue('')" % (servoParams[i])
	    eval (changeVal)

    def UpdateHwfpStat (self, data):
        fmt = '<ffHHBBBBffffffffffffb80s80s80s80s80s80s80si259s'	# 259 is 256 + 3 padding
	s = struct.unpack (fmt, data)
	
	### subap min flux ###
	smf = str (s[0])
	
	### Config Files ###
	pgParse = s[21].split('/')
	pgtt = s[21]
	poParse = s[22].split('/')
	pott = s[22]
	coParse = s[23].split('/')
	clParse = s[24].split('/')
	cltt = s[24]
	reconstParse = s[25].split('/')
	reconsttt = s[25]
	homapParse = s[26].split('/')
	homaptt = s[26]
	lomapParse = s[27].split('/')
	lomaptt = s[27]

	pgStr = pgParse[-1]
	poStr = poParse[-1]
	coStr = coParse[-1]
	coTT = s[23]
	clStr = clParse[-1]
	reconstStr = reconstParse[-1]
	homapStr = homapParse[-1]
	lomapStr = lomapParse[-1]

	### Servo Gains ###
	k0Str = "%.5f" % s[8]
	k1Str = "%.5f" % s[9]
	k2Str = "%.5f" % s[10]
	k3Str = "%.5f" % s[11]
	k4Str = "%.5f" % s[12]
	k5Str = "%.5f" % s[13]
	k6Str = "%.5f" % s[14]
	k7Str = "%.5f" % s[15]
	k8Str = "%.5f" % s[16]
	k11Str = "%.5f" % s[19]

	self.subApMinFluxVal.SetLabel (smf)
	self.subApMinFluxVal.SetToolTipString ("Subaperature Minimum Flux")

	self.coVal.SetLabel (coStr[0:14])
 	self.coVal.SetToolTip (wx.ToolTip (coTT))
 	self.coRB.SetToolTip (wx.ToolTip ("Centroid Offsets"))

	#self.pgVal.SetLabel (pgStr[0:14])
	#self.pgVal.SetToolTip (wx.ToolTip (pgtt))

	self.poVal.SetLabel (poStr[0:14])
	self.poVal.SetToolTip (wx.ToolTip (pott))

	self.reconstVal.SetLabel (reconstStr[0:14])
	self.reconstVal.SetToolTip (wx.ToolTip (reconsttt))

	#self.clVal.SetLabel (clStr[0:14])
	#self.clVal.SetToolTip (wx.ToolTip (cltt))

	self.homapVal.SetLabel (homapStr[0:14])
	self.homapVal.SetToolTip (wx.ToolTip (homaptt))

	self.lomapVal.SetLabel (lomapStr[0:14])
	self.lomapVal.SetToolTip (wx.ToolTip (lomaptt))

	### K[x] Values ###
	self.hoPropGainVal.SetLabel(k0Str)
	self.loPropGainVal.SetLabel(k1Str)
	self.ttPropGainVal.SetLabel(k2Str)
	self.hoLeakyGainVal.SetLabel(k3Str)
	self.loLeakyGainVal.SetLabel(k4Str)
	self.hoLoOffloadGainVal.SetLabel(k5Str)
	self.hoTTOffloadGainVal.SetLabel(k6Str)
	self.loTTOffloadGainVal.SetLabel(k7Str)
	self.calHOFlatGainVal.SetLabel(k8Str)
	self.calCentroidGainVal.SetLabel(k11Str)

        '''
	print "s[0] = ", s[0] # min_flux
	print "s[1] = ", s[1] # rate
	print "s[2] = ", s[2] # log int
	print "s[3] = ", s[3] # log data
	print "s[4] = ", s[4] # num pixels
	print "s[5] = ", s[5] # num subaps
	print "s[6] = ", s[6] # pix subap
	print "s[7] = ", s[7] # calc on/off
	print "s[8] = ", s[8] # K[0]
	print "s[9] = ", s[9] # K[1]
	print "s[10] = ", s[10] # K[2]
	print "s[11] = ", s[11] # K[3]
	print "s[12] = ", s[12] # K[4]
	print "s[13] = ", s[13] # K[5]
	print "s[14] = ", s[14] # K[6]
	print "s[15] = ", s[15] # K[7]
	print "s[16] = ", s[16] # K[8]
	print "s[17] = ", s[17] # K[9]
	print "s[18] = ", s[18] # K[10]
	print "s[19] = ", s[19] # K[11]
	print "s[20] = ", s[20] # servo on/off
	print "s[21] = ", s[21] # pix gains
	print "s[22] = ", s[22] # pix offs
	print "s[23] = ", s[23] # cent offs
	print "s[24] = ", s[24] # cent lin
	print "s[25] = ", s[25] # reconst
	print "s[26] = ", s[26] # ho flatmap
	print "s[27] = ", s[27] # lo flatmap
	print "s[28] = ", s[28] # number of last error
	print "s[29] = ", s[29] # free form status string
	pass  
	'''

    '''
    (4) float    min_flux;      /* minimum flux value */
    (4) float    rate;          /* detected frame rate */
    (2) uint16_t log_interval;  /* log every 'log_interval' frames */
    (2) uint16_t log_data;      /* bit mask of log data types */
    (1) uint8_t  num_pixels;    /* 128 | 64 */
    (1) uint8_t  num_subaps;    /* 8 | 16 | 32 | 64 */
    (1) uint8_t  pix_subap;     /* 2 | 4 */
    (1) uint8_t  on;            /* true => CALC ON, false => CALC OFF */
    -----
    16 bytes

    (48) float    K[HWFP_NUM_GAINS];/* the servo gains */
    (1) uint8_t  on;            /* true => SERVO ON, false => SERVO OFF */
    -----
    49 bytes

    (80) char pix_gains[HWFP_FILENAME_LEN];
    (80) char pix_offs[HWFP_FILENAME_LEN];
    (80) char cent_offs[HWFP_FILENAME_LEN];
    (80) char cent_lin[HWFP_FILENAME_LEN];
    (80) char reconst[HWFP_FILENAME_LEN];
    (80) char ho_flatmap[HWFP_FILENAME_LEN];
    (80) char lo_flatmap[HWFP_FILENAME_LEN];
    -----
    560 bytes

    (4) int  error;                     /* number of last error */
    (256) char status[HWFP_STATUS_LEN];   /* free-form status string */
    -----
    260 Bytes
    -----
    Total: 888 bytes
    '''

    def OnQuit (self, event):
	if self.threadActive == True:
	    self.thread.stop()
	    self.SendCmd ("hwfp\r")
	    time.sleep (1)
 	
	if str (self.GetParent()) == "None":
	    if self.threadActive == True:
	         self.aocaSocket.close()
	    self.Destroy()
	else:
	    if self.threadActive == True:
	        self.aocaSocket.close()
	    self.GetParent().CloseHwfpParameters()
	
if __name__ == "__main__":
    app = wx.App()
    HWFPParameters(None, -1, 'HWFP Parameters')
    app.MainLoop()

