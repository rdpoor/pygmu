import tkinter as tk
import numpy as np
import sounddevice as sd
from PIL import Image, ImageTk
import yaml
import time

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

class PygmuPlayer:
    playback_state = 'stopped'
    is_scrubbing = False
    t2 = None
    user_spd = 0
    recent_x = []
    current_frame = 0
    frame_amps = None
    peak = 0
    peak_age = 0
    def __init__(self):
        self.wave_canv_w = 1440
        self.winh = 300
        self.wavh = 200
        self.pixels_per_second = 40
        self.last_meter_n = 0
        self.stop_flag = False
        self.mouse_is_down = False
        self.last_x = -1
        self.frame_amps = np.zeros(1444, dtype=np.float32) #init issues
        self.shuttle_w = 180
        self.jog_h = 18
        self.wave_seg_pixel_width = 1
        self.bg_color = '#243B40'
        self.bg_color2 = '#444241' # 444241
        self.tr_color = '#0F081D' #191929
        self.bd_color = '#896A67'
        self.wv_color = '#5AFCE1'
        self.sc_color = '#48C7B0'
        self.tx_color = '#191929'
        
        # Create the main window
        self.root = tk.Tk()
        self.root.configure(bg=self.bg_color2)
        self.root.bind('<Configure>', self.on_resize)
        self.root.bind('<KeyPress>', self.on_keypress)
        position = self.load_window_geometry()
        if position:
                self.root.geometry(f"{position[2]}x{position[3]}+{position[0]}+{position[1]}")
        else:
                self.root.geometry('450x200-5+40')
        self.root.title("Pygmu Player")
        self.root.protocol("WM_DELETE_WINDOW", self.cleanUp)

        # Configure column 0 and row 0 to expand
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(2, weight=1)

        #make widgets 
        play_image = ImageTk.PhotoImage(Image.open("vault/images/play_icon.png").resize((24, 24), Image.Resampling.LANCZOS))
        pause_image = ImageTk.PhotoImage(Image.open("vault/images/pause_icon.png").resize((24, 24), Image.Resampling.LANCZOS))
        rewind_image = ImageTk.PhotoImage(Image.open("vault/images/rew_icon.png").resize((24, 24), Image.Resampling.LANCZOS))
        corner_image = ImageTk.PhotoImage(Image.open("vault/images/log2.png").resize((28, self.jog_h), Image.Resampling.LANCZOS))

        self.labelframe = tk.LabelFrame(self.root, text="", padx=5, pady=5, height=35, background=self.bg_color2) # kind of hacky way to set the row height
        self.rewind_button = tk.Label(self.root, image=rewind_image, height=22, width=22, background=self.bg_color2)
        self.rewind_button.bind("<Button-1>", self.onRewindButtonHit)
        self.rewind_button.rewind_image = rewind_image # prevent gc

        self.play_button = tk.Label(self.root, image=play_image, height=22, width=22, background=self.bg_color2)
        self.play_button.bind("<Button-1>", self.onPlayButtonHit)
        self.play_button.play_image = play_image # prevent gc
        self.play_button.pause_image = pause_image # prevent gc

        self.time_text = tk.StringVar()
        self.time_text.set("0.00")
        self.time_label = tk.Label(self.root, textvariable=self.time_text, font=("Arial", 12),fg=self.tx_color, background=self.bg_color2)
        self.speed_text = tk.StringVar()
        self.speed_text.set("1.00")
        self.speed_label = tk.Label(self.root, textvariable=self.speed_text, font=("Arial", 12),fg=self.tx_color, background=self.bg_color2)

        self.wave_frame = tk.LabelFrame(self.root, text="", bd=0, background='', highlightthickness=0)
        self.wave_canvas = tk.Canvas(self.wave_frame, bg=self.bg_color, height=50, width=self.wave_canv_w, highlightthickness=0)
        self.wave_canvas.bind("<ButtonPress-1>", self.onMouseDownWaveCanvas)
        self.wave_canvas.bind("<ButtonRelease-1>", self.onMouseUpWaveCanvas)
        self.wave_canvas.bind("<B1-Motion>", self.onMouseMoveWaveCanvas)
        self.wave_canvas.bind("<Double-Button-1>", self.onDoubleClickWaveCanvas)

        self.jog_canvas = tk.Canvas(self.root, bg=self.tr_color, height=self.jog_h, width=self.wave_canv_w, highlightthickness=0)
        self.jog_canvas.bind("<ButtonPress-1>", self.onMouseDownWaveCanvas)
        self.jog_canvas.bind("<ButtonRelease-1>", self.onMouseUpWaveCanvas)
        self.jog_canvas.bind("<B1-Motion>", self.onMouseMoveWaveCanvas)
        self.jog_canvas.bind("<Double-Button-1>", self.onDoubleClickWaveCanvas)

        self.meter_canvas = tk.Canvas(self.root, bg=self.tr_color, height=150, width=28, highlightthickness=0)
        #self.corner_canvas = tk.Canvas(self.root, bg=self.bg_color2, height=self.jog_h, width=28, highlightthickness=0)
        self.corner_canvas = tk.Label(self.root, image=corner_image, height=self.jog_h, width=28, background=self.bg_color2, highlightthickness=0)
        self.corner_canvas.bind("<ButtonPress-1>", self.onCornerHit)

        self.shuttle = create_custom_scale(self.root, 
            tick_values=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
            from_=1, to=11,
            sliderrelief=tk.FLAT,
            highlightthickness=0,
            showvalue=False,
            bd=0,
            bg='#333333',
            sliderlength=22,
            troughcolor=self.tr_color,
            activebackground='#888888',           
            length=self.shuttle_w,
            orient=tk.HORIZONTAL)
        self.shuttle.bind("<ButtonRelease-1>", self.onShuttleFinishedChanging)
        self.shuttle.bind("<B1-Motion>", self.onShuttleMouseMove)
        self.shuttle.set(6)

        # Lay out widgets                
        self.labelframe.grid(row=0, column=0)
        self.rewind_button.place(x=5, y=5)
        self.play_button.place(x=35, y=5)
        self.shuttle.place(x=71, y=11, height=16)

        # self.speed_label.grid(row=0, column=1)
        # self.time_label.grid(row=1, column=1, padx=(0,4))
        self.speed_label.place(x=self.shuttle_w + 84, y=8)
        self.time_label.place(x=self.shuttle_w + 122, y=8)

        self.jog_canvas.grid(row=1, column=0, sticky="nsew", padx=(6, 0))

        self.corner_canvas.grid(row=1, column=1, sticky="nsew", padx=(0,4), pady=(0,0))
        self.meter_canvas.grid(row=2, column=1, sticky="nsew", padx=(0,4), pady=(0,5))

        self.wave_frame.grid(row=2, column=0,  sticky="nsew", padx=(6, 0), pady=(0,5))
        self.wave_canvas.pack(side=tk.TOP, expand=True, fill=tk.BOTH, padx=0, pady=0)

    def on_keypress(self,event):
        if event.keysym == 'space':
            if self.playback_state == 'stopped':
                self.startPlaying()
            else:
                self.pausePlaying()
    
    def on_resize(self,event):
        if event.widget != self.root:
                return
        # self.root.update_idletasks() # make sure all the children have finished resizing BUT this seems to screw us up on boot
        self.wave_canv_w = self.wave_canvas.winfo_width()
        self.winh = event.height - 8
        self.wavh = (self.winh - 57)
        self.pixels_per_second = self.wave_canv_w / (self.t2._src_pe.extent().end() / self.t2._src_pe.frame_rate())
        self.wave_canvas.delete('all')
        self.draw_wave_hash()
        self.jog_canvas.delete('all')
        #self.wave_seg_pixel_width = max(1,round(self.wave_canv_w / 800)) # hack -- need to compute  based on the files duration in secs and frames per sec
        self.wave_seg_pixel_width = 1 

        # before we throw out the old amps, let's copy them into the new resolution and draw them
        old_frame_amps = self.frame_amps.copy()
        self.frame_amps = np.zeros(max(10,self.wave_canv_w + 1), dtype=np.float32)
        len_factor = self.wave_canv_w / len(old_frame_amps)
        old_x = 0
        for amp in old_frame_amps:
            x = int(np.round(len_factor * old_x))
            self.frame_amps[x] = amp
            self.drawWaveSegment(x,amp)
            old_x += 1

    def startPlaying(self):
        self.t2.play()
        self.playback_state = 'playing'
        self.play_button.config(image=self.play_button.pause_image) 
    def pausePlaying(self):
        self.t2.pause()
        self.playback_state = 'stopped'
        self.play_button.config(image=self.play_button.play_image) 
        self.showAmp(0) # hack to kill the peak indicator WIP

    def onPlayButtonHit(self,evt):
            if self.playback_state == 'stopped':
                    self.setSpeed(1)
                    self.startPlaying()
            elif self.playback_state == 'playing':
                    self.pausePlaying()

    def onRewindButtonHit(self,evt):
            self.t2.set_frame(0)

    def setSpeed(self, spd):
        self.t2.set_speed(spd)
        self.speed_text.set(f"{spd:.2f}")
  
    def onShuttleChanged(self, evt):
        ndx = self.shuttle.get()
        self.setSpeedFromShuttleIndex(ndx)

    def onShuttleFinishedChanging(self, evt):
        self.setSpeed(1)
        self.shuttle.set(6)

    def onShuttleMouseMove(self, event):
        x_norm = ((event.x + 11)/ self.shuttle_w) # slider width?
        ndx = (13 * x_norm) - 6 # magic numbers come from the range of shuttle indexes -- should be variable instead
        if np.round(ndx) == 6:
            return
        #self.setSpeedFromShuttleIndex(ndx)

    def setSpeedFromShuttleIndex(self, ndx):
        # ndx will be an int from the widget, but mousemove can send in floats
        null_stopped = self.playback_state == 'stopped'
        if null_stopped and ndx == 6:
            return
        mid_ndx = 6
        if ndx < 7:
            pow = mid_ndx - ndx                
        else:
            pow = ndx - mid_ndx
        spd = (2 ** (pow - 3))
        if ndx < 6:
            spd = -spd
        elif ndx == 6:
            spd = 0.0001
        self.setSpeed(spd)
        if null_stopped and ndx != mid_ndx:
            self.startPlaying()

    def onMouseDownWaveCanvas(self, event):
        self.wave_down_x = event.x
        x_norm = (event.x / self.wave_canv_w)
        self.wave_canvas_st_frame = x_norm * self.t2._src_pe.extent().end()
        self.recent_x = []

        frame = x_norm * self.t2._src_pe.extent().end()
        self.t2.set_frame(frame)

    def onMouseMoveWaveCanvas(self, event):
        x_norm = (event.x / self.wave_canv_w)
        self.recent_x.append([x_norm, time.time()])
        frame = x_norm * self.t2._src_pe.extent().end()
        # figure out what to do with speed based on playback situation
        # should keep a smoothed running average of the x velocity of the mouse
        # we let the magnitude of the changes dictate the amt of smoothing -- so big changes dont get smoothed nearly as much
        smoothing = 9
        n = min(smoothing, len(self.recent_x))
        if n < 2:
            return # dont interpret mousemoves as scrubbing until we've seen a couple, could just be a nervous click
        
        if self.playback_state == 'stopped':
            self.startPlaying()
                    
        self.is_scrubbing = True

        x0 = self.recent_x[-n]
        xl = self.recent_x[-1]
        vx = (xl[0] - x0[0]) * self.wave_canv_w / ((xl[1] - x0[1])) # pixels per sec
        src_px = self.wave_canv_w / (self.t2._src_pe.extent().end() / self.t2._src_pe.frame_rate()) # pixels per sec of the src_pe
        spd = vx / (1 * src_px)
        spd = min(max(spd, -38), 38)
        if spd == 0:
            spd = 0.05
        self.setSpeed(spd)

    def onMouseUpWaveCanvas(self, event):
        if self.is_scrubbing:
            self.pausePlaying()
            self.is_scrubbing = False

    def onDoubleClickWaveCanvas(self, event):
        if self.playback_state == 'stopped':
            self.startPlaying()
            self.setSpeed(1)
        else:
            self.pausePlaying()

    def showAmp(self,a):
        h = 8
        n = round(4.5 * a * (self.wavh / h))
        if n == self.last_meter_n:
                return
        if n > self.peak:
             self.peak = n
             self.peak_age = 0
        else:
             self.peak_age += 1
             if self.peak_age > 3:
                  self.peak -= 1

        self.last_meter_n = n
        x0 = 2
        x1 = 29
        y0 = self.wavh -  (n * h) + 4
        self.meter_canvas.delete('all')

        def color_for_y(y):
            y = self.wavh - y
            if y < self.wavh * 0.58:
                return 'green'
            if y < self.wavh * 0.85:
                return 'yellow'
            return 'red'

        while (n > 0):
                self.meter_canvas.create_line(x0, y0, x1, y0, fill=color_for_y(y0), width=h - 1)
                y0 = y0 + h
                n = n - 1
        y0 = self.wavh -  (self.peak * h)
        self.meter_canvas.create_line(x0, y0, x1, y0, fill=color_for_y(y0), width=h - 1)

    def drawWaveSegment(self,x,amp):
        h = self.wavh + 1
        col = self.wv_color
        w = self.wave_seg_pixel_width
        if self.is_scrubbing:
            col = self.sc_color
            w = 1
        self.wave_canvas.create_line(x,h,x,h - (amp * h * 4.5), fill=col, width = w)
        #self.wave_canvas.create_line(x,h,x,h - (amp * h * 5), fill=col, width = 1)
    def draw_wave_hash(self):
        h = self.wavh + 2
        col = '#222F40'
        w = self.pixels_per_second
        for i in range(round(self.wave_canv_w / w)):
            x = i * w
            self.wave_canvas.create_line(x, 0, x, h, fill=col, width=1)
        self.wave_canvas.create_line(0, h, self.wave_canv_w, h, fill=col, width=1)
         
    def now_playing_callback(self, fr, amp): # callback once per frame from T2
        if self.current_frame == fr:
             return
        self.current_frame = fr
        if self.stop_flag:
                raise sd.CallbackStop
        prog = fr / self.t2._src_pe.extent().end()
        if prog > 1 or prog < 0:
            return
        x = round(prog * self.wave_canv_w)
        if self.last_x == x:
             return;
        self.last_x = x
        self.showAmp(amp)
        self.time_text.set(f"{fr/self.t2._src_pe.frame_rate():.2f}")
        self.frame_amps[x] = amp
        self.drawWaveSegment(x,amp)
        self.jog_canvas.delete('all')
        self.jog_canvas.create_line(x,2,x,self.jog_h+3, fill='yellow', width=1)

    def onCornerHit(self, evt):
        self.t2.choose_src(self.t2._ur_src_pe._src_pe)
        self.wave_canvas.delete('all')

    def save_window_geometry(self):
        with open("user/window_position.yaml", "w") as f:
            yaml.dump({"window_x": self.root.winfo_x(), "window_y": self.root.winfo_y(), "window_w": self.root.winfo_width(), "window_h": self.root.winfo_height()}, f)

    def load_window_geometry(self):
        try:
            with open("user/window_position.yaml", "r") as f:
                position = yaml.safe_load(f)
                return position["window_x"], position["window_y"], position["window_w"], position["window_h"]
        except FileNotFoundError:
            return None

    def cleanUp(self):
        player.stop_flag = True
        self.save_window_geometry()
        self.root.after(50, self.root.destroy)

import os
import sys
import numpy as np
script_dir = os.path.dirname( __file__ )
pygmu_dir = os.path.join( script_dir, '..', 'pygmu' )
sys.path.append( pygmu_dir )
import pygmu as pg

player = PygmuPlayer()

src = pg.WavReaderPE("samples/TamperFrame_TooGoodToBeTrue_Edit.wav")

t2 = pg.T2(src)
t2.now_playing_callback = player.now_playing_callback
player.t2 = t2

ret = player.root.mainloop()
print(ret)

# TODO
# during scrubbing reduce smoothing when deltas are bigger
# speed(0) during scrubbing if current_time passes mouse time in the last direction of mouse mvt -- restart when we move past again?
# try a .cache() that's like play, but just fills out the pe's _cached_frames, which can be used as the source for T2 (pre warper anyway)
# add duration label right side place() on_resize
# extent arg for quick render checking
# make tree of all parent pes
# t2 pre_renders, and in process draws the wave -- we could render to ram instead of disk and allow partial playback
# fft view / cool 3d spectrogram
# VU Meter -- pics of a real meter -- needle inertia will be the challenge
# zoomable wave form, for more precise scrubbing? a scrollable canvas -- y mouse can control zoom factor, but for now fixed factor (settable)

