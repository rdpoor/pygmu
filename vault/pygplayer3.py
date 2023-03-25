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
    t2_driver = None
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
        self.last_meter_n = 0
        self.stop_flag = False
        self.mouse_is_down = False
        self.frame_amps = np.zeros(1444, dtype=np.float32) #init issues
        self.shuttlew = 180
        self.wave_seg_pixel_width = 2
        self.bg_color = '#243B40'
        self.bd_color = '#896A67'
        self.wv_color = '#53D8FB'
        self.sc_color = '#22AAA1'
        self.tx_color = '#53D8FB'
        
        # Create the main window
        self.root = tk.Tk()
        self.root.bind('<Configure>', self.on_resize)
        position = self.load_window_geometry()
        if position:
                self.root.geometry(f"{position[2]}x{position[3]}+{position[0]}+{position[1]}")
        else:
                self.root.geometry('450x300-5+40')
        self.root.title("Pygmu Player")
        self.root.protocol("WM_DELETE_WINDOW", self.onWindowClose)

        # Configure column 0 and row 0 to expand
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(2, weight=1)

        #make widgets
        play_image = ImageTk.PhotoImage(Image.open("vault/images/9045012_play_filled_alt_icon.png"))
        pause_image = ImageTk.PhotoImage(Image.open("vault/images/9045012_play_filled_alt_icon.png"))
        rewind_image = ImageTk.PhotoImage(Image.open("vault/images/9045012_play_filled_alt_icon.png"))

        self.labelframe = tk.LabelFrame(self.root, text="", padx=5, pady=5, height=35)
        self.rewind_button = tk.Label(self.root, image=rewind_image, height=22, width=22, bg='green')
        self.rewind_button.bind("<Button-1>", self.onRewindButtonHit)
        self.rewind_button.rewind_image = rewind_image # prevent gc

        self.play_button = tk.Label(self.root, image=play_image, height=22, width=22, bg='green')
        self.play_button.bind("<Button-1>", self.onPlayButtonHit)
        self.play_button.play_image = play_image # prevent gc
        self.play_button.pause_image = pause_image # prevent gc

        self.time_text = tk.StringVar()
        self.time_text.set("0.00")
        self.time_label = tk.Label(self.root, textvariable=self.time_text, font=("Arial", 11),fg=self.tx_color)
        self.speed_text = tk.StringVar()
        self.speed_text.set("1.00")
        self.speed_label = tk.Label(self.root, textvariable=self.speed_text, font=("Arial", 11),fg=self.tx_color)

        self.wave_frame = tk.LabelFrame(self.root, text="", bd=0, background='')
        self.wave_canvas = tk.Canvas(self.wave_frame, bg=self.bg_color, height=50, width=self.wave_canv_w)
        self.wave_canvas.bind("<ButtonPress-1>", self.onMouseDownWaveCanvas)
        self.wave_canvas.bind("<ButtonRelease-1>", self.onMouseUpWaveCanvas)
        self.wave_canvas.bind("<B1-Motion>", self.onMouseMoveWaveCanvas)
        self.wave_canvas.bind("<Double-Button-1>", self.onDoubleClickWaveCanvas)

        self.jog_canvas = tk.Canvas(self.root, bg="#212121", height=20, width=self.wave_canv_w)
        self.jog_canvas.bind("<ButtonPress-1>", self.onMouseDownWaveCanvas)
        self.jog_canvas.bind("<ButtonRelease-1>", self.onMouseUpWaveCanvas)
        self.jog_canvas.bind("<B1-Motion>", self.onMouseMoveWaveCanvas)
        self.jog_canvas.bind("<Double-Button-1>", self.onDoubleClickWaveCanvas)

        self.meter_canvas = tk.Canvas(self.root, bg="#212121", height=150, width=30)

        self.shuttle = create_custom_scale(self.root, 
            tick_values=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
            from_=1, to=11,
            sliderrelief=tk.FLAT,
            highlightthickness=0,
            showvalue=False,
            bd=0,
            bg='#777777',
            sliderlength=22,
            troughcolor='#222222',
            activebackground='#888888',           
            length=self.shuttlew,
            orient=tk.HORIZONTAL)
        self.shuttle.bind("<ButtonRelease-1>", self.onShuttleFinishedChanging)
        self.shuttle.bind("<B1-Motion>", self.onShuttleMouseMove)
        self.shuttle.set(6)

        # Lay out widgets                
        self.labelframe.grid(row=0, column=0)
        self.rewind_button.place(x=5, y=5)
        self.play_button.place(x=65, y=5)
        self.shuttle.place(x=143, y=15, height=14)

        self.speed_label.grid(row=0, column=1)
        self.time_label.grid(row=1, column=1)

        self.jog_canvas.grid(row=1, column=0,  sticky="nsew", padx=(4, 0))

        self.meter_canvas.grid(row=2, column=1,  sticky="nsew", padx=(0,4), pady=(0,5))

        self.wave_frame.grid(row=2, column=0,  sticky="nsew", padx=(6, 0), pady=(0,5))
        self.wave_canvas.pack(side=tk.TOP, expand=True, fill=tk.BOTH, padx=0, pady=0)

    def on_resize(self,event):
        if event.widget != self.root:
                return
        # self.root.update_idletasks() # make sure all the children have finished resizing BUT this seems to screw us up on boot
        self.wave_canv_w = self.wave_canvas.winfo_width()
        self.winh = event.height - 8
        self.wavh = (self.winh - 57)
        self.wave_canvas.delete('all')
        self.jog_canvas.delete('all')
        self.wave_seg_pixel_width = max(1,round(self.wave_canv_w / 400)) # hack -- need to compute  based on the files duration in secs and frames per sec

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
        self.t2_driver.play()
        self.playback_state = 'playing'
        self.play_button.image = self.play_button.pause_image

    def pausePlaying(self):
        self.t2_driver.pause()
        self.playback_state = 'stopped'
        self.play_button.image = self.play_button.play_image
        self.showAmp(0) # hack to kill the peak indicator WIP

    def onPlayButtonHit(self,evt):
            if self.playback_state == 'stopped':
                    self.setSpeed(1)
                    self.startPlaying()
            elif self.playback_state == 'playing':
                    self.pausePlaying()

    def onRewindButtonHit(self,evt):
            self.t2_driver.set_frame(0)

    def setSpeed(self, spd):
        self.t2_driver.set_speed(spd)
        self.speed_text.set(f"{spd:.2f}")
  
    def onShuttleChanged(self, evt):
        ndx = self.shuttle.get()
        self.setSpeedFromShuttleIndex(ndx)

    def onShuttleFinishedChanging(self, evt):
        self.setSpeed(1)
        self.shuttle.set(6)

    def onShuttleMouseMove(self, event):
        x_norm = ((event.x + 11)/ self.shuttlew) # slider width?
        ndx = (13 * x_norm) - 6 # magic numbers come from the range of shuttle indexes -- should be variable instead
        if np.round(ndx) == 6:
            return
        #print(x_norm, ndx)
        #self.setSpeedFromShuttleIndex(ndx)

    def setSpeedFromShuttleIndex(self, ndx):
        null_stopped = self.playback_state == 'stopped'
        print(ndx)
        if null_stopped and ndx == 6:
            return
        # ndx will be an int from the widget, but mousemove can send in floats
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
        self.wave_canvase_st_frame = x_norm * self.t2_driver._src_pe.extent().end()
        self.recent_x = []

        frame = x_norm * self.t2_driver._src_pe.extent().end()
        self.t2_driver.set_frame(frame)

    def onMouseMoveWaveCanvas(self, event):
        x_norm = (event.x / self.wave_canv_w)
        self.recent_x.append([x_norm, time.time()])
        frame = x_norm * self.t2_driver._src_pe.extent().end()
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
        src_px = self.wave_canv_w / (self.t2_driver._src_pe.extent().end() / 48000) # pixels per sec of the src_pe
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
        n = round(5.5 * a * (self.wavh / h))
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
        x0 = 6
        x1 = 28
        y0 = self.wavh -  (n * h)
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
        h = self.wavh
        col = self.wv_color
        w = self.wave_seg_pixel_width
        if self.is_scrubbing:
            col = self.sc_color
            w = 1
        # if x % 2 == 0:
        #     col = '#434343'
        self.wave_canvas.create_line(x,h,x,h - (amp * h * 5), fill=col, width = w)
        #self.wave_canvas.create_line(x,h,x,h - (amp * h * 5), fill=col, width = 1)
         
    def now_playing_callback(self, fr, amp): # callback once per frame from T2
        if self.current_frame == fr:
             return
        self.current_frame = fr
        if self.stop_flag:
                raise sd.CallbackStop
        prog = fr / self.t2_driver._src_pe.extent().end()
        if prog > 1 or prog < 0:
            return
        self.showAmp(amp)
        self.time_text.set(f"{fr/48000:.2f}")
        x = round(prog * self.wave_canv_w)
        self.frame_amps[x] = amp
        self.drawWaveSegment(x,amp)
        self.jog_canvas.delete('all')
        self.jog_canvas.create_line(x,0,x,20, fill='green')
        #self.draw_wave()
            
    def draw_wave(self): # deprecated -- not really any faster
        # Use NumPy vectorized operations to compute the y-coordinates
        y_coords = 50 - self.frame_amps * 280

        # Generate a list of (x, y) coordinate pairs
        x_coords = np.arange(len(self.frame_amps))
        points = np.column_stack((x_coords, y_coords)).flatten()

        # Draw all the line segments in one call STILL surprisingly slow
        col = self.wv_color
        self.wave_canvas.delete('all')
        self.wave_canvas.create_line(*points, fill=col)

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

    def onWindowClose(self):
        player.stop_flag = True
        self.save_window_geometry()
        self.root.after(50, self.root.destroy)

player = PygmuPlayer()


import os
import sys
import numpy as np
script_dir = os.path.dirname( __file__ )
pygmu_dir = os.path.join( script_dir, '..', 'pygmu' )
sys.path.append( pygmu_dir )
import pygmu as pg

src = pg.WavReaderPE("samples/TamperFrame_TooGoodToBeTrue_Edit.wav")
#src = pg.WavReaderPE("samples/TamperFrame_SugarPlumFaries_Edit2.wav")
t2 = pg.T2(src)
t2.now_playing_callback = player.now_playing_callback
player.t2_driver = t2

player.root.mainloop()

# TODO
# finish button cosmetics
# write up manual
# dbl-click, scrubbing, shuttle, resize,
# add duration, sr, n channels, and add units to the time_text
# rename vars related to scrubbing

# speed(0) during scrubbing if current_time passes mouse time in the last direction of mouse mvt -- restart when we move past again?
# WIP when you click anywhere in the shuttle slider area, the slider snaps to where you clicked and the speed is set accordingly.
# WIP try no quanitzation for shuttle, with detents at the powers of 2
# during scrubbing reduce smoothing when deltas are bigger
# VU Meter -- pics of a real meter -- needle inertia will be the challenge
# zoomable wave form, for more precise scrubbing? a scrollable canvas -- y mouse can control zoom factor, but for now fixed factor (settable)

# Rob:
# the middle of the Shuttle (speed) slider denotes zero speed (aka paused)
# to the left is progressively faster (reverse), to the right is progressively faster (forward)
# when not clicked on, the Shuttle (speed) slider snaps to the middle. 

# andy subtle -- when stopped, shuttle jumps to speed0, then you can creep slowly back and forth, snapback stays at 0.  when playing, it jumps to speed1, and that becomes the snapback point when dragging the shuttle

# when you slide to the middle, the speed becomes zero.
# I previously suggested that the shuttle slider be continuous and not just quantized to powers of two.  It might be interesting to try:
# no quantization
# quantize to powers of two
# quantize to powers of 2/n (n steps per octave)
# ... and see which one feels best.