#!/usr/bin/env python
"""Minimal strip chart widget

For testing memory leaks.
"""
import bisect
import datetime
import time
import numpy
import Tkinter
import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class StripChartWdg(Tkinter.Frame):
    def __init__(self, master, timeRange):
        Tkinter.Frame.__init__(self, master)
        
        self._timeRange = float(timeRange)
        # interval at which to update the time axis
        self._updateInterval = max(0.1, min(5.0, self._timeRange / 2000.0))
        # purge old data every _maxPurgeCounter updates of the time axis
        self._maxPurgeCounter = max(1, int(0.5 + (5.0 / self._updateInterval)))
        self._purgeCounter = 0

        figure = matplotlib.figure.Figure(figsize=(8, 2), frameon=True)
        self.canvas = FigureCanvasTkAgg(figure, self)
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky="news")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.subplot = figure.add_subplot(1, 1, 1)
        self.subplot.grid(True)
        self.subplot.autoscale(enable=True, axis="y")

        self._tData = [] # time (x axis) data
        self._yData = [] # y axis data
        self.line = matplotlib.lines.Line2D([], [], animated=False)
        self.subplot.add_line(self.line)
        
        self._timeAxisTimer = None
        self._updateTimeAxis()

    def addPoint(self, y):
        """Append a new data point
        
        Inputs:
        - y: y value
        - t: time as a POSIX timestamp (e.g. time.time()); if None then "now"
        """
        t = time.time()
        self._tData.append(t)
        self._yData.append(y)
        self.line.set_data(self._tData, self._yData)
    
    def _purgeOldData(self, minTime):
        """Purge data with t < minTime

        Inputs:
        - minTime: time before which to delete data (unix seconds)
        """
        if not self._tData:
            return

        numToDitch = bisect.bisect_left(self._tData, minTime) - 1
        if numToDitch > 0:
            self._tData = self._tData[numToDitch:]
            self._yData = self._yData[numToDitch:]
            self.line.set_data(self._tData, self._yData)

    
    def _updateTimeAxis(self):
        """Update the time axis; calls itself at the update interval
        """
        if self._timeAxisTimer != None:
            self.after_cancel(self._timeAxisTimer)
            self._timeAxisTimer = None
        tMax = time.time() + self._updateInterval
        tMin = tMax - self._timeRange
        
        self._purgeCounter = (self._purgeCounter + 1) % self._maxPurgeCounter
        if self._purgeCounter == 0:
            self._purgeOldData(tMin)
        
        self.subplot.set_xlim(tMin, tMax)
        self.subplot.autoscale_view(scalex=False, scaley=True)
        self.canvas.draw()
        self._timeAxisTimer = self.after(int(self._updateInterval * 1000), self._updateTimeAxis)


if __name__ == "__main__":   
    root = Tkinter.Tk()
    stripChart = StripChartWdg(root, 10)
    stripChart.pack(expand=True, fill="both")

    def addRandomValues(interval=100):
        val = numpy.random.rand(1)[0]
        stripChart.addPoint(val)
        root.after(interval, addRandomValues, interval)

    addRandomValues(interval=200)
    root.mainloop()
