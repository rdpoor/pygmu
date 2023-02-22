import numpy as np
import extent as Extent
import sounddevice as sd
import utils as ut
import queue
import threading
import sys
from pygmu import (Extent)
from fts_transport import FtsTransport
from wav_reader_pe import WavReaderPE
from wav_writer_pe import WavWriterPE
from crop_pe import CropPE
import tempfile

input_queue = queue.Queue()

def onKeyPress(k):
    print(k)
    input_queue.put(k)

def onButton1():
    print('button1')






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

# Add a Canvas widget
#canvas= Canvas(root)


playbut = ttk.Button(root, text="Play", command=onButton1).grid()

#Adding transparent background property
root.wm_attributes('-alpha', 0.5)

#Create a Label
#Label(root, text= "This is a New line Text", font= ('Helvetica 18'), bg= '#ab23ff').pack(ipadx= 50, ipady=50, padx= 20)


# add some padding
for child in root.winfo_children(): 
    child.grid_configure(padx=5, pady=5)

# root.bind("<Return>", onReturn)
root.bind("<KeyPress>", onKeyPress)

root.mainloop() # this will hang unless and until user closes the window












# def input_thread(input_queue):
#     while True:
#         # read single character off stdin
#         input_queue.put(readchar.readchar())

# input_thread = threading.Thread(target=input_thread, args=(input_queue,))
# input_thread.daemon = True
# input_thread.start()

