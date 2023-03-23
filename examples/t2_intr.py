"""
GUI design for the T2 transport

        +-------+-------+  +-------------------------+
        |       |       |  |                         |
        | PAUSE |  PLAY |  |    <time in seconds>    |
        |       |       |  |                         |
        +-------+-------+  +-------------------------+

        +--------------------------------------------+
jog     |      ||                                    |
        +--------------------------------------------+

         2.0x   1.0x   0.5x   0.   0.5x   1.0x   2.0x
        +--------------------------------------------+
shuttle |                                  ||        |
        +--------------------------------------------+

"""

import tkinter as tk
import numpy as np
import sounddevice as sd
from PIL import Image, ImageTk

class PygmuPlayer:
        playback_state = 'stopped'
        t2_driver = None
        def __init__(self):
                self.last_meter_n = 0
                self.stop_flag = False
                self.mouse_is_down = False

        def onPlayButtonHit(self):
                if self.playback_state == 'stopped':
                        self.t2_driver.play()
                        self.playback_state = 'playing'
                        play_button['text'] = 'Pause'
                elif self.playback_state == 'playing':
                        self.t2_driver.pause()
                        self.playback_state = 'stopped'
                        play_button['text'] = 'Play'

        def onRewindButtonHit(self):
                self.t2_driver.set_frame(0)

        def onJogChanged(self, q):
                frame = (jog.get() / 100) * self.t2_driver._src_pe.extent().end()
                if jog.user_is_interacting:
                        self.t2_driver.set_frame(frame)

        def onJogFinishedChanging(self, evt):
                frame = (jog.get() / 100) * self.t2_driver._src_pe.extent().end()
                self.t2_driver.set_frame(frame)
                
        def onShuttleChanged(self, evt):
                ndx = shuttle.get()
                if ndx < 7:
                      pow = 6 - ndx                
                else:
                      pow = ndx - 6
                spd = (2 ** (pow - 3))
                if ndx < 6:
                        spd = -spd
                elif ndx == 6:
                        spd = 1
                self.t2_driver.set_speed(spd)

        def onShuttleFinishedChanging(self, evt):
                self.t2_driver.set_speed(1)
                shuttle.set(6)

        def showAmp(self,a):
                h = 8
                n = round(a *165)
                if n == self.last_meter_n:
                       return
                self.last_meter_n = n
                x0 = 6
                x1 = 28
                y0 = 154 - (n * h)
                meter_canvas.delete('all')
                while (n > 0):
                        meter_canvas.create_line(x0, y0, x1, y0, fill='green', width=h - 1)
                        y0 = y0 + h
                        n = n - 1
                        #print(x0, y0, x1, y0 + h)



        def onT2Update(self, fr, amp):
                if self.stop_flag:
                        raise sd.CallbackStop
                prog = fr / self.t2_driver._src_pe.extent().end()
                jog.set(prog * 100)
                self.showAmp(amp)

player = PygmuPlayer()

def onWindowClose():
        player.stop_flag = True
        print('onWindowClose')
        #player.t2_driver.pause()
        #root.withdraw()
        root.after(100, root.destroy)

# Create the main window
root = tk.Tk()
root.geometry('300x300-5+40')
root.title("Pygmu Player")

root.protocol("WM_DELETE_WINDOW", onWindowClose)

labelframe = tk.LabelFrame(root, text="", padx=5, pady=5)
jogframe = tk.LabelFrame(root, text="", padx=9, pady=5)
shuttleframe = tk.LabelFrame(root, text="", padx=9, pady=5)


class PygJogger(tk.Scale):
    
    def __init__(self, master=None, commandFinished=None, **kwargs):
        super().__init__(master, **kwargs)
        self.commandFinished = commandFinished
        self.user_is_interacting = False
        self.bind("<ButtonPress-1>", self.onMouseDown)
        self.bind("<ButtonRelease-1>", self.onMouseUp)
    # Override methods or add new ones as needed
    def onMouseDown(self, event):
        self.user_is_interacting = True
        value_range = self["to"] - self["from"]
        if self["orient"] == tk.HORIZONTAL:
                position = (event.x - (self["sliderlength"] / 2)) / (self["length"]) * 1.5 #strange fudge factor
                new_value = self["from"] + (position * value_range)
        else:
                position = (event.y - (self["sliderlength"] / 2)) / (self["length"]) * 1.5 #strange fudge factor
                new_value = self["from"] + (1 - position) * value_range
        self.set(new_value)

    def onMouseUp(self, evt):
        self.user_is_interacting = False
        if self.commandFinished:
              self.commandFinished(evt)

def on_value_change(scale, tick_values, value):
    nearest_tick_value = min(tick_values, key=lambda x: abs(x - float(value)))
    scale.set(nearest_tick_value)
    player.onShuttleChanged(nearest_tick_value)

def create_custom_scale(master, tick_values, from_, to, orient=tk.HORIZONTAL, **kwargs):
    scale = tk.Scale(master, from_=from_, to=to, orient=orient, command=lambda value: on_value_change(scale, tick_values, value), **kwargs)

    for tick_value in tick_values:
        position = (tick_value - from_) / (to - from_)
        if orient == tk.HORIZONTAL:
            x = position * (scale["length"] - 2*scale["sliderlength"]) + scale["sliderlength"]
            y = scale["sliderlength"] // 2
            anchor = "n"
        else:
            x = scale["sliderlength"] // 2
            y = (1 - position) * (scale["length"] - 2*scale["sliderlength"]) + scale["sliderlength"]
            anchor = "w"

       # label = tk.Label(master, text=str(tick_value))
       # label.place(in_=scale, x=x, y=y, anchor=anchor)

    return scale

def create_rounded_frame(parent, width, height, corner_radius, **kwargs):
    canvas = tk.Canvas(parent, width=width, height=height, **kwargs)
    canvas.create_rectangle(corner_radius, 0, width - corner_radius, height, outline="blue", fill="white")
    canvas.create_rectangle(0, corner_radius, width, height - corner_radius, outline="", fill="white")
    canvas.create_arc(corner_radius, corner_radius, 0, 0, start=90, extent=90, outline="", fill="white")
    canvas.create_arc(width - corner_radius, corner_radius, width, 0, start=0, extent=90, outline="", fill="white")
    canvas.create_arc(corner_radius, height - corner_radius, 0, height, start=180, extent=90, outline="", fill="white")
    canvas.create_arc(width - corner_radius, height - corner_radius, width, height, start=270, extent=90, outline="", fill="white")
    return canvas

def create_imaged_frame(parent, width, height, img_path):
    # Open and resize the image
    img = Image.open(img_path).resize((width, height), Image.ANTIALIAS)
    img = ImageTk.PhotoImage(img)

    # Create a Label widget with the image as background
    label = tk.Label(parent, image=img, width=width, height=height)
    label.image = img  # Store a reference to the image to avoid garbage collection

    return label

#jogframe = create_imaged_frame(root, 200, 140, 'vault/images/concertBlurBG2.png')


jog = PygJogger(jogframe, orient=tk.HORIZONTAL,
                sliderrelief=tk.FLAT,
                highlightthickness=0,
                showvalue=False,
                bd=0,
                bg='#777777',
                sliderlength=22,
                troughcolor='#313131',
                activebackground='#888888',
                command=player.onJogChanged, length=400, commandFinished = player.onJogFinishedChanging)

#jog.bind("<ButtonPress-1>", player.onJogFinishedChanging)
#jog.bind("<ButtonRelease-1>", player.onJogFinishedChanging)
#shuttle = tk.Scale(root, from_=-4, to=4, tickinterval=1, orient=tk.HORIZONTAL, command=player.onShuttleChanged, length=400)
shuttle = create_custom_scale(shuttleframe, tick_values=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], from_=1, to=11,
                sliderrelief=tk.FLAT,
                highlightthickness=0,
                showvalue=False,
                bd=0,
                bg='#777777',
                sliderlength=22,
                troughcolor='#313131',
                activebackground='#888888',           
                length=400, 
                orient=tk.HORIZONTAL)
shuttle.bind("<ButtonRelease-1>", player.onShuttleFinishedChanging)
shuttle.set(6)

meter_canvas = tk.Canvas(root, bg="#212121", height=150, width=30)


text = tk.Text(root, width=15, height=3)

# Lay out widgets
# canvas.pack(padx=5, pady=5)
# checkbutton.pack(padx=5, pady=5)
labelframe.pack(padx=5, pady=5)
jogframe.pack(padx=5, pady=5)
shuttleframe.pack(padx=5, pady=5)

# Menu: See below for adding the menu bar at the top of the window
jog.pack(padx=0, pady=0)
shuttle.pack(padx=0, pady=0)
meter_canvas.pack(padx=15, pady=5)

###############################################################################
# Add stuff to the widgets (if necessary)
# Draw something in the canvas
# canvas.create_oval(5, 15, 35, 45, outline='blue')
# canvas.create_line(10, 10, 40, 30, fill='red')

rewind_button = tk.Button(labelframe, text="<-", command=player.onRewindButtonHit)
play_button = tk.Button(labelframe, text="Play", command=player.onPlayButtonHit)

rewind_button.pack(side=tk.LEFT)
play_button.pack(side=tk.LEFT)

# root.bind("<ButtonPress-1>", player.OnMouseDown)
# root.bind("<ButtonRelease-1>", player.OnMouseUp)

import os
import sys
import time
import numpy as np
script_dir = os.path.dirname( __file__ )
pygmu_dir = os.path.join( script_dir, '..', 'pygmu' )
sys.path.append( pygmu_dir )
import pygmu as pg

src = pg.WavReaderPE("samples/TamperFrame_AfternoonOfAFaun.wav")
t2 = pg.T2(src)
t2.now_playing_callback = player.onT2Update
player.t2_driver = t2

root.mainloop()



# TODO
# VU Meter -- led stack on canvas, cool font
# Birth near mouse
# update jog from t2 callbacks
# metering
# display pos secs
# improve scale ticks displays, appearance
# wave canvas above jog
# sd.CallbackStop

# If so, I'd suggest the following:
# the middle of the Shuttle (speed) slider denotes zero speed (aka paused)
# to the left is progressively faster (reverse), to the right is progressively faster (forward)
# when not clicked on, the Shuttle (speed) slider snaps to the middle. 
# when you click anywhere in the shuttle slider area, the slider snaps to where you clicked and the speed is set accordingly.
# when you slide to the middle, the speed becomes zero.
# I previously suggested that the shuttle slider be continuous and not just quantized to powers of two.  It might be interesting to try:
# no quantization
# quantize to powers of two
# quantize to powers of 2/n (n steps per octave)
# ... and see which one feels best.