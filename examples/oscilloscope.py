#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 27 17:06:09 2015 - cc0

@author: James Hoyland
Kwanlten Polytechnic University
Physics for Modern Technology

Oscilloscope replicates the standard 2 channel YT display of the Tektronix TBS1022
scope in a live animated plot. Its main purpose was to allow the live display of oscilloscope
traces on a data projector during classroom demonstrations. Update speed is rather slow
in comparison to the scope itself, probably limited by the USB transfer speed.

TODO: incorporate some more UI to allow freezing and saving of data. Save / recall of scope
settings. Display of channel / timebase parameters.

this example may be expanded at https://github.com/danpeirce/tektronix-oscilloscope
"""


import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as anim
import visa

class oscilloscope:
    
    def __init__(self):
        #Start communications with scope - probably should do some checking here
        self.resmgr = visa.ResourceManager()
        self.instr = self.resmgr.open_resource(self.resmgr.list_resources()[0])
        #Set data encoding to small-endian signed int to be output to NumPy array
        self.instr.write('DAT:ENC SRI') 
        self.instr.values_format.is_binary = True
        self.instr.values_format.datatype = 'b'
        self.instr.values_format.is_big_endian = False
        self.instr.values_format.container = np.array
        #Set up some lists to be used in the plotting for ranges and grid lines
        self.yticks = [(n * 96.0 / 4.0) for n in range(-4,5)]
        self.xticks = [(n * 250.0) for n in range(0,11)]
        self.t = range(0,2500)
        
    #Start acquisition    
        
    def aq_run(self):
        self.instr.write('ACQ:STATE RUN')
        
    #Stop acquisition    
        
    def aq_stop(self):
        self.instr.write('ACQ:STATE STOP')
        
    #Select the active data channel - needed before querying CURVE data.
    #Waveforms can only be transferred on at a time.        
        
    def data_chan(self,ch):
        self.instr.write('DAT:SOURCE CH%s' % ch)
        
    #Assign the plot object
        
    def assign_plot(self,p):
        self.plt = p
        
    #def set_time_axis():
    #    s = self.instr.query('HOR:DELAY:SCALE?')
    #    if s != self.st:
    #        self.t = np.array([s * dt for dt in range(2500)])
    #    #TO DO: strip other chars
            
    #Plots the actual graph. Most of this is just styling to make the graph
    #look like the scope screen. I feel there should be a more efficient way to
    #to do this but I need to learn more about mathplotlib            
            
    def plotGraph(self):
        self.plt.clear()        
        self.plt.plot(self.t,self.ch1,'y',self.t,self.ch2,'c')  
        self.plt.set_xticklabels([])
        self.plt.set_yticklabels([])
        self.plt.set_xticks(self.xticks,minor=False)
        self.plt.set_yticks(self.yticks,minor=False)
        self.plt.set_xlim(0,2500)
        self.plt.set_ylim(-96,96)        
        self.plt.grid(True,color='w')  

     
    #Makes the class callable by the FuncAnimation method. 
    #Obtains the curves from the scope and calls the plotGraph method
        
    def __call__(self,i):
        self.data_chan(1)
        self.ch1 = self.instr.query_values('CURV?')
        self.data_chan(2)
        self.ch2 = self.instr.query_values('CURV?')
        self.plotGraph()
        
#Create an oscilloscope instance
scope = oscilloscope()

#Create the plot figure and link it to the oscilloscope instance
fig = plt.figure()
ax = fig.add_subplot(111,axis_bgcolor='k')  
scope.assign_plot(ax)


scope.aq_run()

#Animate
ani = anim.FuncAnimation(fig,scope,interval=50)
plt.show()

  
        
        
