
'''
@author: Stou Sandalski (stou@icapsid.net)
@license:  Public Domain
'''

#Uncomment if you have multiple wxWidgets versions
#import wxversion
#wxversion.select('2.8')

import math, wx

from wx.glcanvas import GLCanvas
from OpenGL.GLU import *
from OpenGL.GL import *


class WxGLTest(GLCanvas):
    def __init__(self, parent):
        GLCanvas.__init__(self, parent,-1, attribList=[wx.glcanvas.WX_GL_DOUBLEBUFFER])
        wx.EVT_PAINT(self, self.OnDraw)
        wx.EVT_SIZE(self, self.OnSize)
        wx.EVT_MOTION(self, self.OnMouseMotion)
        wx.EVT_WINDOW_DESTROY(self, self.OnDestroy)
        
        self.init = True

    def OnDraw(self,event):
        self.SetCurrent()

        if not self.init:
            self.InitGL()
            self.init = False

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        
        # Draw the spiral in 'immediate mode'
        # WARNING: You should not be doing the spiral calculation inside the loop
        # even if you are using glBegin/glEnd, sin/cos are fairly expensive functions
        # I've left it here as is to make the code simpler.
        radius = 1.0
        x = radius*math.sin(0)
        y = radius*math.cos(0)
        glColor(0.0, 1.0, 0.0)
        glBegin(GL_LINE_STRIP)
        for deg in xrange(1000):
            glVertex(x, y, 0.0)
            rad = math.radians(deg)
            radius -= 0.001
            x = radius*math.sin(rad)
            y = radius*math.cos(rad)
        glEnd()
        
        glEnableClientState(GL_VERTEX_ARRAY)
        
        spiral_array = []
        
        # Second Spiral using "array immediate mode" (i.e. Vertex Arrays)
        radius = 0.8
        x = radius*math.sin(0)
        y = radius*math.cos(0)
        glColor(1.0, 0.0, 0.0)
        for deg in xrange(820):
            spiral_array.append([x,y])
            rad = math.radians(deg)
            radius -= 0.001
            x = radius*math.sin(rad)
            y = radius*math.cos(rad)

        glVertexPointerf(spiral_array)
        glDrawArrays(GL_LINE_STRIP, 0, len(spiral_array))
        glFlush()
        self.SwapBuffers()
        return
    
    def InitGL(self):
        '''
        Initialize GL
        '''

#        # set viewing projection
#        glClearColor(0.0, 0.0, 0.0, 1.0)
#        glClearDepth(1.0)
#
#        glMatrixMode(GL_PROJECTION)
#        glLoadIdentity()
#        gluPerspective(40.0, 1.0, 1.0, 30.0)
#
#        glMatrixMode(GL_MODELVIEW)
#        glLoadIdentity()
#        gluLookAt(0.0, 0.0, 10.0,
#                  0.0, 0.0, 0.0,
#                  0.0, 1.0, 0.0)

    def OnSize(self, event):

        try:
            width, height = event.GetSize()
        except:
            width = event.GetSize().width
            height = event.GetSize().height
        
        self.Refresh()
        self.Update()

    def OnMouseMotion(self, event):
        x = event.GetX()
        y = event.GetY()
    
    def OnDestroy(self, event):
        print "Destroying Window"


if __name__ == '__main__':

    app = wx.App()
    frame = wx.Frame(None, -1, 'wxPython and OpenGL', wx.DefaultPosition, wx.Size(400,400))
    canvas = WxGLTest(frame)

    frame.Show()
    app.MainLoop()
