import os
import sys
import numpy as np
script_dir = os.path.dirname( __file__ )
pygmu_dir = os.path.join( script_dir, '..', 'pygmu' )
sys.path.append( pygmu_dir )
import pygmu as pg
"""
Test TimewarpPE
"""
FRAME_RATE = 48000

# mixing original with time-varying delay == flanging
source = pg.WavReaderPE("samples/Tamper_MagnifyingFrame1.wav").gain(3)
warped = pg.DelayPE(source, pg.SinPE(frequency=82, amplitude=30.0, frame_rate=FRAME_RATE))
# DelayPE with a time-varying delay has infinite extent.  Crop it to the length of the original
warped = warped.crop(source.extent())

warped2 = pg.DelayPE(source, pg.SinPE(frequency=4306, amplitude=114.0, frame_rate=FRAME_RATE))
warped2 = warped2.crop(source.extent())

warped3 = pg.DelayPE(source, pg.SinPE(frequency=2612, amplitude=14.0, frame_rate=FRAME_RATE))
warped3 = warped3.crop(source.extent())

def helloCallBack():
    print('blamo',warped2)
    pg.Transport(pg.MixPE(warped2, warped3)).play()

# def onReturn(x):
#     print('got return key!',x)

# def onKeyPress(k):
#     print('got key!',k)



from tkinter import *
from tkinter import ttk
root = Tk()
root.geometry('100x100')
label = ttk.Label(
    root,
    text="Hello, Tkinter",
    foreground="white",
    background="black",
    #width=10,
    #height=10
).grid()



ttk.Button(root, text="Play", command=helloCallBack).grid()

# add some padding
for child in root.winfo_children(): 
    child.grid_configure(padx=5, pady=5)

# root.bind("<Return>", onReturn)
root.bind("<KeyPress>", onReturn)

root.mainloop() # this will hang unless and until user closes the window


