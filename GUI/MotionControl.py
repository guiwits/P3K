#!/usr/bin/python

import wx
import threading
import numpy
import socket
import struct
import binascii
import time

motors = "LENSLET_X LENSLET_Y WFSCAM_Z WHITE_X WHITE_Y WHITE_Z WFS_Z ACAM_LENS \
          STIM SSM1_A SSM1_B SSM2_A SSM2_B OAR_RELAY OAR_STIM SPATL_FLTR".split()
motorRB = [] ### Motor Radio Button ###
motorUI = [] ### Motor Position - User Input ###
motorCV = [] ### Motor Current Value ###

HOST = "192.168.0.100"  
PORT = 10106			# Motor Subscriber Port
AOCAPORT = 10000		# AOCA Communication Port
MSGLEN = 192 			# Bytes
THREADACTIVE = False

class DataThread (threading.Thread):
    def __init__ (self, window):
	threading.Thread.__init__ (self)
	self.window = window
	self.finished = threading.Event()

    def stop (self):
	self.finished.set()

    def run (self):
	print "Starting motor status data acquisition ..."
	self.socketobj = socket.socket (socket.AF_INET, socket.SOCK_STREAM)
	self.socketobj.setsockopt (socket.SOL_TCP, socket.TCP_NODELAY, 1)
	
	try:
	    self.socketobj.connect ((HOST, PORT))
	except socket.gaierror, e:
	    print "Address-related error connecting to server %s" % e
	    return
	except socket.error, e:
	    print "Connection error: %s" % e
	    return

	print "motor subscriber socket connection established."

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

	    wx.CallAfter (self.window.UpdateMotorStatus, msg)	

	    if self.finished.isSet():
	        self.socketobj.close()
		break 
	
	print "Exiting the motor status thread ..."

class MotionControl (wx.Frame):
    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, id, title, size = (400,400))

     	statusPanel = wx.Panel (self, -1)
	sizer = wx.GridBagSizer (0, 0)
	counter = 0

 	#--- Set up timer for start ---#
	self.timer1 = wx.Timer (self)
	self.timer1.Start (100, oneShot = True)
	
	vbox = wx.BoxSizer (wx.VERTICAL)

	for motor in motors:
	    var1 = "%sCB" % (motor, )
	    motorRB.append (var1)
	    var2 = "%sMotorState" % (motor, )
	    motorUI.append (var2)
	    var3 = "%sCurPos" % (motor, )
	    motorCV.append (var3)

	    if counter == 0:
	        motorRB[counter] = wx.RadioButton (statusPanel, -1, motor, style = wx.RB_GROUP)
	    else:
	        motorRB[counter] = wx.RadioButton (statusPanel, -1, motor)
		
	    sizer.Add (motorRB[counter], (counter, 0), flag = wx.TOP | wx.LEFT | wx.BOTTOM, border = 5)

	    motorUI[counter] = wx.StaticText (statusPanel, -1, '-----')
	    sizer.Add (motorUI[counter], (counter, 2), flag = wx.TOP | wx.LEFT | wx.BOTTOM, border = 5)

	    motorCV[counter] = wx.StaticText (statusPanel, -1, '-----')
	    sizer.Add (motorCV[counter], (counter, 4), flag = wx.TOP | wx.LEFT | wx.BOTTOM, border = 5)

	    counter = counter + 1

	### END FOR ###

	### STATIC LINE BREAK ### 
	staticLineOne = wx.StaticLine (statusPanel, -1)
	sizer.Add (staticLineOne, (16,0), (1, 5), flag = wx.EXPAND | wx.TOP | wx.BOTTOM, border = 5)
	### END STATIC LINE BREAK ### 

	self.offset = wx.RadioButton (statusPanel, -1, "Offset", style = wx.RB_GROUP)
	self.move = wx.RadioButton (statusPanel, -1, "Move")
	
	sizer.Add (self.move, (17, 3), flag = wx.BOTTOM | wx.ALIGN_RIGHT, border = 5)
	sizer.Add (self.offset, (17, 4), flag = wx.BOTTOM | wx.ALIGN_RIGHT, border = 5)

	reset = wx.Button (statusPanel, -1, "Reset", size = (20, 25))
	sizer.Add (reset, (18, 0), flag = wx.EXPAND | wx.TOP | wx.LEFT | wx.BOTTOM, border = 5)
	
	self.stop = wx.Button (statusPanel, -1, "Stop", size = (-1, 25))
	sizer.Add (self.stop, (18, 1), flag = wx.EXPAND | wx.TOP | wx.LEFT | wx.BOTTOM, border = 5)

	#self.userInput = wx.TextCtrl (statusPanel, -1, size = (60, 20))
	self.userInput = wx.SpinCtrl (statusPanel, -1, size = (60, 20))
	self.userInput.SetRange (-100000, 100000)
	self.userInput.SetValue (0)
	sizer.Add (self.userInput, (18, 2), (1, 2), flag = wx.EXPAND | wx.TOP | wx.LEFT | wx.BOTTOM, border = 5)

	self.go = wx.Button (statusPanel, -1, "Go", size = (-1, 25))
	sizer.Add (self.go, (18, 4), flag = wx.EXPAND | wx.TOP | wx.LEFT | wx.BOTTOM, border = 5)

	### Binds ###
	self.Bind (wx.EVT_TIMER, self.ConnectToSocket, self.timer1)
	self.Bind (wx.EVT_CLOSE, self.OnQuit)
	self.Bind (wx.EVT_BUTTON, self.OnReset, reset)
	self.Bind (wx.EVT_BUTTON, self.MoveMotor, self.go)
	self.Bind (wx.EVT_BUTTON, self.StopMotor, self.stop)


	#sizer.AddGrowableRow (17)
	sizer.AddGrowableCol (2)
	#sizer.Fit (self)
	#statusPanel.SetSizer (sizer)
	vbox.Add (sizer, 1, wx.EXPAND | wx.ALL, 20)
	statusPanel.SetSizer (vbox)
	vbox.Fit (self)
	
	self.Centre ()
	self.Show (True)

    def ConnectToSocket (self, event):
	cmd = "motor"
	self.thread = DataThread(self)
        self.thread.start()
	self.SendCmd (cmd, 0)
	THREADACTIVE = True

    def SendCmd (self, motorName, command):
        ''' check to see if motor is the spatial filter '''
	''' if it is, then change the name to the real  '''
	''' name (ie SPATIAL_FILTER)			'''
	if motorName == 'SPATL_FLTR':
	    self.motorName = 'SPATIAL_FILTER'
	else:
	    self.motorName = motorName

	self.command = command
        aocaAddress = (HOST, AOCAPORT)
        aocaSocket = socket.socket (socket.AF_INET, socket.SOCK_STREAM, 0)
        aocaSocket.connect (aocaAddress)
        defaultString = 'motor\r'
	stopString = 'stop %s' % (self.motorName)
	resetString = 'reset %s' % (self.motorName)

	''' Check for move or offset '''
	if self.move.GetValue() == True:
	    moveType = 'move'
	else:
	    moveType = 'offset'

	sendString = "%s %s %s" % (moveType, self.motorName, self.command)

	if self.motorName == 'motor':
            aocaSocket.send (defaultString)
            recvdata = aocaSocket.recv (512)
	elif self.command == 'stop':
	    print "Stopping motor %s" % self.motorName
            aocaSocket.send (stopString)
            recvdata = aocaSocket.recv (512)
	elif self.command == 'reset':
	    print "Resetting motor %s" % self.motorName
            aocaSocket.send (resetString)
            recvdata = aocaSocket.recv (512)
	else:
            aocaSocket.send (sendString)
            recvdata = aocaSocket.recv (512)

        if recvdata.find ('ERR:') == 0:
            #print "ERR received sending motor move."
            aocaSocket.close ()
        else:
            #print "Received data: ", repr (recvdata)
            aocaSocket.close ()

    def MoveMotor (self, event):
	motorToMove = self.GetMotorChecked ()
	moveValue = self.userInput.GetValue ()
  	self.SendCmd (motorToMove, moveValue)	

    def StopMotor (self, event):
	motorToStop = self.GetMotorChecked ()
	self.SendCmd (motorToStop, "stop")

    def ResetMotor (self):
	motorToReset = self.GetMotorChecked ()
	self.SendCmd (motorToReset, "reset")

    def GetMotorChecked (self): 
        for i in range (len (motors)):
	    if motorRB[i].GetValue() == True:
	        return motors[i]
	
    def OnReset (self, event):
	message = "Do you really want to reset motor %s?" % self.GetMotorChecked()
	dlg = wx.MessageDialog (self, message, "Confirm Reset", 
			        wx.OK | wx.CANCEL | wx.ICON_QUESTION)
	print "Rick is the master of all things MAC!!"
	result = dlg.ShowModal()
	dlg.Destroy ()
	if result == wx.ID_OK:
	    ### Send a reset command to AOCA ###
	    self.ResetMotor ()

    def UpdateMotorStatus (self, data):
	fmt = '<i128s20sffiffii12s'	### from motor.h -- motor_stat_t ###
	#print 'Packed Values	:', binascii.hexlify (data)
	motorData = struct.unpack (fmt, data)
	
	mname = motorData[2].strip ('\0')
	homing = str (motorData[5])
	position = "%.0f" % motorData[3]
	mpos   = str (position)
	mstate = str (motorData[9])

	'''
	print "---------------------------------------"
	print motorData[0]
	print motorData[1]
	print motorData[2]
	print motorData[3]
	print motorData[4]
	print motorData[5]
	print motorData[6]
	print motorData[7]
	print motorData[8]
	print motorData[9]
	print motorData[10]
	print "---------------------------------------"
        print '\n'
	'''

	if mname == 'LENSLET_X':
	    if homing == str (0):
	        motorCV[0].SetLabel(mpos)
	    elif homing == str (1):
	        motorCV[0].SetLabel ("Homing")
	    else:
	        motorCV[0].SetLabel(mpos)

	    if mstate == str (0):
	        motorUI[0].SetLabel('STOPPED')
		motorUI[0].SetForegroundColour('black')
	    elif mstate == str (1):
	        motorUI[0].SetLabel('MOVING')
		motorUI[0].SetForegroundColour('green')
	    else:
	        motorUI[0].SetLabel('ERROR')
		motorUI[0].SetForegroundColour('red')
	elif mname == "LENSLET_Y":
	    if homing == str (0):
	        motorCV[1].SetLabel (mpos)
	    elif homing == str (1):
	        motorCV[1].SetLabel ("Homing")
	    else:
	        motorCV[1].SetLabel (mpos)

	    if mstate == str (0):
	        motorUI[1].SetLabel('STOPPED')
		motorUI[1].SetForegroundColour('black')
	    elif mstate == str (1):
	        motorUI[1].SetLabel('MOVING')
		motorUI[1].SetForegroundColour('green')
	    else:
	        motorUI[1].SetLabel('ERROR')
		motorUI[1].SetForegroundColour('red')
	elif mname == "WFSCAM_Z":
	    motorCV[2].SetLabel(mpos)
	    if mstate == str (0):
	        motorUI[2].SetLabel('STOPPED')
		motorUI[2].SetForegroundColour('black')
	    elif mstate == str (1):
	        motorUI[2].SetLabel('MOVING')
		motorUI[2].SetForegroundColour('green')
	    else:
	        motorUI[2].SetLabel('ERROR')
		motorUI[2].SetForegroundColour('red')
	elif mname == "WHITE_X":
	    motorCV[3].SetLabel(mpos)
	    if mstate == str (0):
	        motorUI[3].SetLabel('STOPPED')
		motorUI[3].SetForegroundColour('black')
	    elif mstate == str (1):
	        motorUI[3].SetLabel('MOVING')
		motorUI[3].SetForegroundColour('green')
	    else:
	        motorUI[3].SetLabel('ERROR')
		motorUI[3].SetForegroundColour('red')
	elif mname == "WHITE_Y":
	    motorCV[4].SetLabel(mpos)
	    if mstate == str (0):
	        motorUI[4].SetLabel('STOPPED')
		motorUI[4].SetForegroundColour('black')
	    elif mstate == str (1):
	        motorUI[4].SetLabel('MOVING')
		motorUI[4].SetForegroundColour('green')
	    else:
	        motorUI[4].SetLabel('ERROR')
		motorUI[4].SetForegroundColour('red')
	elif mname == "WHITE_Z":
	    motorCV[5].SetLabel(mpos)
	    if mstate == str (0):
	        motorUI[5].SetLabel('STOPPED')
		motorUI[5].SetForegroundColour('black')
	    elif mstate == str (1):
	        motorUI[5].SetLabel('MOVING')
		motorUI[5].SetForegroundColour('green')
	    else:
	        motorUI[5].SetLabel('ERROR')
		motorUI[5].SetForegroundColour('red')
	elif mname == "WFS_Z":
	    motorCV[6].SetLabel(mpos)
	    if mstate == str (0):
	        motorUI[6].SetLabel('STOPPED')
		motorUI[6].SetForegroundColour('black')
	    elif mstate == str (1):
	        motorUI[6].SetLabel('MOVING')
		motorUI[6].SetForegroundColour('green')
	    else:
	        motorUI[6].SetLabel('ERROR')
		motorUI[6].SetForegroundColour('red')
	elif mname == "ACAM_LENS":
	    motorCV[7].SetLabel(mpos)
	    if mstate == str (0):
	        motorUI[7].SetLabel('STOPPED')
		motorUI[7].SetForegroundColour('black')
	    elif mstate == str (1):
	        motorUI[7].SetLabel('MOVING')
		motorUI[7].SetForegroundColour('green')
	    else:
	        motorUI[7].SetLabel('ERROR')
		motorUI[7].SetForegroundColour('red')
	elif mname == "STIM":
	    motorCV[8].SetLabel(mpos)
	    if mstate == str (0):
	        motorUI[8].SetLabel('STOPPED')
		motorUI[8].SetForegroundColour('black')
	    elif mstate == str (1):
	        motorUI[8].SetLabel('MOVING')
		motorUI[8].SetForegroundColour('green')
	    else:
	        motorUI[8].SetLabel('ERROR')
		motorUI[8].SetForegroundColour('red')
	elif mname == "SSM1_A":
	    motorCV[9].SetLabel(mpos)
	    if mstate == str (0):
	        motorUI[9].SetLabel('STOPPED')
		motorUI[9].SetForegroundColour('black')
	    elif mstate == str (1):
	        motorUI[9].SetLabel('MOVING')
		motorUI[9].SetForegroundColour('green')
	    else:
	        motorUI[9].SetLabel('ERROR')
		motorUI[9].SetForegroundColour('red')
	elif mname == "SSM1_B":
	    motorCV[10].SetLabel(mpos)
	    if mstate == str (0):
	        motorUI[10].SetLabel('STOPPED')
		motorUI[10].SetForegroundColour('black')
	    elif mstate == str (1):
	        motorUI[10].SetLabel('MOVING')
		motorUI[10].SetForegroundColour('green')
	    else:
	        motorUI[10].SetLabel('ERROR')
		motorUI[10].SetForegroundColour('red')
	elif mname == "SSM2_A":
	    motorCV[11].SetLabel(mpos)
	    if mstate == str (0):
	        motorUI[11].SetLabel('STOPPED')
		motorUI[11].SetForegroundColour('black')
	    elif mstate == str (1):
	        motorUI[11].SetLabel('MOVING')
		motorUI[11].SetForegroundColour('green')
	    else:
	        motorUI[11].SetLabel('ERROR')
		motorUI[11].SetForegroundColour('red')
	elif mname == "SSM2_B":
	    motorCV[12].SetLabel(mpos)
	    if mstate == str (0):
	        motorUI[12].SetLabel('STOPPED')
		motorUI[12].SetForegroundColour('black')
	    elif mstate == str (1):
	        motorUI[12].SetLabel('MOVING')
		motorUI[12].SetForegroundColour('green')
	    else:
	        motorUI[12].SetLabel('ERROR')
		motorUI[12].SetForegroundColour('red')
	elif mname == "OAR_RELAY":
	    motorCV[13].SetLabel(mpos)
	    if mstate == str (0):
	        motorUI[13].SetLabel('STOPPED')
		motorUI[13].SetForegroundColour('black')
	    elif mstate == str (1):
	        motorUI[13].SetLabel('MOVING')
		motorUI[13].SetForegroundColour('green')
	    else:
	        motorUI[13].SetLabel('ERROR')
		motorUI[13].SetForegroundColour('red')
	elif mname == "OAR_STIM":
	    motorCV[14].SetLabel(mpos)
	    if mstate == str (0):
	        motorUI[14].SetLabel('STOPPED')
		motorUI[14].SetForegroundColour('black')
	    elif mstate == str (1):
	        motorUI[14].SetLabel('MOVING')
		motorUI[14].SetForegroundColour('green')
	    else:
	        motorUI[14].SetLabel('ERROR')
		motorUI[14].SetForegroundColour('red')
	elif mname == "SPATIAL_FILTER":
	    motorCV[15].SetLabel(mpos)
	    if mstate == str (0):
	        motorUI[15].SetLabel('STOPPED')
		motorUI[15].SetForegroundColour('black')
	    elif mstate == str (1):
	        motorUI[15].SetLabel('MOVING')
		motorUI[15].SetForegroundColour('green')
	    else:
	        motorUI[15].SetLabel('ERROR')
		motorUI[15].SetForegroundColour('red')
	else:
	    print "Bad motor name received."
	    pass

    def OnQuit (self, event):
	if THREADACTIVE == True:
            self.thread.stop()
	    self.SendCmd ("motor", "motor")		### Force a motor update to help close out thread /hack
	    time.sleep (1)
	if str (self.GetParent()) == "None":
	    self.Destroy()
	else:
	    self.GetParent().CloseMotionControl()

if __name__ == "__main__":
    app = wx.App ()
    MotionControl (None, -1, 'Motion Control & Status')
    app.MainLoop ()
