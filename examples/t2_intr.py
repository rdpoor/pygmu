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
import yaml

def save_window_position():
    x = root.winfo_x()
    y = root.winfo_y()
    with open("user/window_position.yaml", "w") as f:
        yaml.dump({"window_x": x, "window_y": y}, f)

def load_window_position():
    try:
        with open("user/window_position.yaml", "r") as f:
            position = yaml.safe_load(f)
            return position["window_x"], position["window_y"]
    except FileNotFoundError:
        return None


class PygmuPlayer:
        playback_state = 'stopped'
        t2 = None
        def __init__(self):
                self.last_meter_n = 0
                self.stop_flag = False
                self.mouse_is_down = False

        def startPlaying(self):
                self.t2.play()
                self.playback_state = 'playing'
                play_button['text'] = 'Pause'
        def pausePlaying(self):
                self.t2.pause()
                self.playback_state = 'stopped'
                play_button['text'] = 'Play'

        def onPlayButtonHit(self):
                print('onPlayButtonHit',self.playback_state)
                if self.playback_state == 'stopped':
                        self.startPlaying()
                elif self.playback_state == 'playing':
                        self.pausePlaying()


        def onRewindButtonHit(self):
                self.t2.set_frame(0)

        def onJogChanged(self, q):
                frame = (jog.get() / 100) * self.t2._src_pe.extent().end()
                if jog.user_is_interacting:
                        self.t2.set_frame(frame)

        def onJogFinishedChanging(self, evt):
                frame = (jog.get() / 100) * self.t2._src_pe.extent().end()
                self.t2.set_frame(frame)
                
        def onShuttleChanged(self, evt):
                mid_ndx = 6
                null_stopped = self.playback_state == 'stopped'
                ndx = shuttle.get()
                if ndx < 7:
                      pow = mid_ndx - ndx                
                else:
                      pow = ndx - mid_ndx
                spd = (2 ** (pow - 3))
                if ndx < 6:
                        spd = -spd
                elif ndx == 6:
                        spd = 1
                self.t2.set_speed(spd)
                if null_stopped and ndx != mid_ndx:
                      self.startPlaying()

        def onShuttleFinishedChanging(self, evt):
                self.t2.set_speed(1)
                shuttle.set(6)

        def showAmp(self,a):
                h = 8
                n = round(a * 165)
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

        def onT2Update(self, fr, amp):
                if self.stop_flag:
                        raise sd.CallbackStop
                prog = fr / self.t2._src_pe.extent().end()
                if jog.user_is_interacting == False:
                        jog.set(prog * 100)
                self.showAmp(amp)
                time_text.set(f"{fr/48000:.2f}")
                x = prog * 440
                if round(x) % 2 == 0:
                      col = 'yellow'
                else:
                      col = 'gray'
                wave_canvas.create_line(x, 50, x, 50 - amp * 280, fill=col, width=0.15)

player = PygmuPlayer()

def cleanUp():
        player.stop_flag = True
        save_window_position()
        root.after(50, root.destroy)

# Create the main window
root = tk.Tk()

position = load_window_position()
if position:
        root.geometry(f"+{position[0]}+{position[1]}")
else:
        root.geometry('300x300-5+40')

root.title("Pygmu Player")

root.protocol("WM_DELETE_WINDOW", cleanUp)

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
    def onMouseDown(self, event):
        self.user_is_interacting = True

    def onMouseUp(self, event):

        slider_position = self.get()
        # Convert the slider's position (in scale units) to the corresponding pixel coordinate
        slider_pixel_position = self.coords(slider_position)
        if slider_pixel_position[0] - 9 <= event.x <= slider_pixel_position[0] + 9:
                return # clicked on the little slider knob, so this is probably the beginning of a grab/slide
        value_range = self["to"] - self["from"]
        if self["orient"] == tk.HORIZONTAL:
                position = (event.x - (self["sliderlength"] / 2)) / (self["length"]) * 1.05 #strange fudge factor
                new_value = self["from"] + (position * value_range)
        else:
                position = (event.y - (self["sliderlength"] / 2)) / (self["length"]) * 1.05 #strange fudge factor
                new_value = self["from"] + (1 - position) * value_range
        self.set(new_value)

        if self.commandFinished:
              self.commandFinished(event)

        self.user_is_interacting = False

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

shuttle = create_custom_scale(shuttleframe, 
                tick_values=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
                from_=1, to=11,
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
wave_canvas = tk.Canvas(root, bg="#212121", height=50, width=440)

time_text = tk.StringVar()
time_text.set("0.00")
time_label = tk.Label(labelframe, textvariable=time_text, font=("Arial", 11)).pack(anchor='w')


text = tk.Text(root, width=15, height=3)

# Lay out widgets
labelframe.pack(padx=5, pady=5)
jogframe.pack(padx=5, pady=5)
shuttleframe.pack(padx=5, pady=5)

jog.pack(padx=0, pady=0)
shuttle.pack(padx=0, pady=0)
meter_canvas.pack(padx=15, pady=5)
wave_canvas.pack(padx=15, pady=5)

rewind_button = tk.Button(labelframe, text="<-", command=player.onRewindButtonHit)
play_button = tk.Button(labelframe, text="Play", command=player.onPlayButtonHit)

rewind_button.pack(side=tk.LEFT)
play_button.pack(side=tk.LEFT)

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
player.t2 = t2

root.mainloop()


# TODO
# display pos secs, spd
# wave canvas above jog (can just store the frame amps)
# VU Meter -- led stack on canvas, cool font
# V2, actual pics of a VU meter, choose pic based on amp
# use an Image bg on the slider knob -- will require a custom slider class

# Rob:
# the middle of the Shuttle (speed) slider denotes zero speed (aka paused)
# to the left is progressively faster (reverse), to the right is progressively faster (forward)
# when not clicked on, the Shuttle (speed) slider snaps to the middle. 
# when you click anywhere in the shuttle slider area, the slider snaps to where you clicked and the speed is set accordingly.

# andy subtle -- when stopped, shuttle jumps to speed0, then you can creep slowly back and forth, snapback stays at 0.  when playing, it jumps to speed1, and that becomes the snapback point when dragging the shuttle

# when you slide to the middle, the speed becomes zero.
# I previously suggested that the shuttle slider be continuous and not just quantized to powers of two.  It might be interesting to try:
# no quantization
# quantize to powers of two
# quantize to powers of 2/n (n steps per octave)
# ... and see which one feels best.