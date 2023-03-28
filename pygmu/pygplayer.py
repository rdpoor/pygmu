'''
click to jump to a location
dlb-click to start/stop playback
drag to scrub

key_commands:
    <space>  = toggle playback
    <return> = rewind
    ->       = skip later 1 second
    -<       = skip earlier 1 second
    q        = stop and close window
    Q        = stop and exit script
'''

import tkinter as tk
import numpy as np
import sounddevice as sd
from PIL import Image, ImageTk
import yaml
import time
import utils as ut

class PygPlayer:
    def __init__(self, title='d',auto_start=True):
        self.title = title
        self.auto_start = auto_start
        self.peak_hold_frames = 15
        self.playback_state = 'stopped'
        self.is_scrubbing = False
        self.t2 = None
        self.recent_x = []
        self.current_frame = 0
        self.frame_amps = None,
        self.peak = 0
        self.peak_age = 0
        self.wave_canv_w = 1440
        self.winh = 300
        self.wavh = 200
        self.pixels_per_second = 40
        self.last_meter_n = 0
        self.stop_flag = False
        self.last_x = -1
        self.resize_timer = None
        self.frame_amps = np.zeros(1444, dtype=np.float32)
        self.shuttle_w = 180
        self.jog_h = 7
        self.wave_seg_pixel_width = 1
        self.bg_color = '#243B40'
        self.bg_color2 = '#444241'
        self.tr_color = '#0F081D'
        self.bd_color = '#896A67'
        self.wv_color = '#5AFCE1'
        self.sc_color = '#48C7B0'
        self.tx_color = '#909CC2'
        self.exit_script_flag = False

        # Create the main window
        self.root = tk.Tk()
        self.root.configure(bg=self.bg_color2)
        self.root.bind('<Configure>', self.on_configure)
        self.root.bind('<KeyPress>', self.on_keypress)
        position = self.load_window_geometry()
        if position:
            self.root.geometry(f"{position[2]}x{position[3]}+{position[0]}+{position[1]}")
        else:
            self.root.geometry('450x200-5+40')
        self.root.title(self.title)
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
        self.corner_canvas = tk.Label(self.root, image=corner_image, height=self.jog_h, width=28, background=self.bg_color2, highlightthickness=0)
        self.corner_canvas.bind("<ButtonPress-1>", self.onCornerHit)

        self.shuttle = tk.Scale(self.root,
            from_=1, to=11,
            sliderrelief=tk.FLAT,
            highlightthickness=0,
            showvalue=False,
            bd=0,
            sliderlength=14,
            troughcolor=self.tr_color,
            activebackground='#777777',           
            length=self.shuttle_w,
            command=self.onShuttleChanged,
            orient=tk.HORIZONTAL)
        
        self.shuttle.bind("<ButtonRelease-1>", self.onShuttleFinishedChanging)
        self.shuttle.bind("<B1-Motion>", self.onShuttleMouseMove)
        self.shuttle.set(6)

        # Lay out widgets                
        self.labelframe.grid(row=0, column=0)
        self.rewind_button.place(x=5, y=5)
        self.play_button.place(x=35, y=5)
        self.shuttle.place(x=71, y=13, height=10)
        self.speed_label.place(x=self.shuttle_w + 84, y=7)
        self.time_label.place(x=self.shuttle_w + 122, y=7)
        self.jog_canvas.grid(row=1, column=0, sticky="nsew", padx=(6, 0))
        self.corner_canvas.grid(row=1, column=1, sticky="nsew", padx=(0,4), pady=(0,0))
        self.meter_canvas.grid(row=2, column=1, sticky="nsew", padx=(0,6), pady=(0,5))
        self.wave_frame.grid(row=2, column=0,  sticky="nsew", padx=(6, 0), pady=(0,5))
        self.wave_canvas.pack(side=tk.TOP, expand=True, fill=tk.BOTH, padx=0, pady=0)

    def on_keypress(self,event):
        key = event.keysym
        def space():
            if self.playback_state == 'stopped':
                self.startPlaying()
            else:
                self.pausePlaying()
        def Return():
            self.onRewindButtonHit(event)
        def q():
            self.cleanUp()
        def Q():
            self.exit_script_flag = True
            self.cleanUp()
        def Right():
            self.t2.set_frame(self.t2.get_frame() + 48000)
        def Left():
            self.t2.set_frame(self.t2.get_frame() - 48000)
        def default():
            print("Unhandled key:", key)
        key_actions = {
            "space": space,
            "Return": Return,
            "Right": Right,
            "Left": Left,
            "q": q,
            "Q": Q,
        }
        action = key_actions.get(key, default)
        if action:
            action()
        else:
            default()

    # confusing hack around idle_tasks() when we fire up multiple windows in succession
    def on_configure(self, event):
        if event.width == 1:
            return
        if event.widget != self.root:
            return       
        if self.resize_timer:
            self.root.after_cancel(self.resize_timer)  # Cancel the previous timer, if any
        self.resize_timer = self.root.after(500, self.delayed_on_configure,event)  # Set a new timer for 500 ms
    
    def delayed_on_configure(self,event):
        if event.widget != self.root:
            return
        #self.root.update_idletasks() # make sure all the children have finished resizing BUT this seems to screw us up on boot
        self.wave_canv_w = self.wave_canvas.winfo_width()
        self.winh = event.height - 8
        self.wavh = (self.winh - 39 - self.jog_h)
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
        if self.auto_start:
            self.root.after(10, self.startPlaying)
            self.auto_start = False #only the first time

    def startPlaying(self):
        self.setSpeed(1)
        self.t2.play()
        self.playback_state = 'playing'
        self.play_button.config(image=self.play_button.pause_image)

    def pausePlaying(self):
        self.t2.pause()
        self.playback_state = 'stopped'
        self.play_button.config(image=self.play_button.play_image) 

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
        self.t2.set_frame(self.wave_canvas_st_frame)

    def onMouseMoveWaveCanvas(self, event):
        x_norm = (event.x / self.wave_canv_w)
        self.recent_x.append([x_norm, time.time()])
        mouse_frame = x_norm * self.t2._src_pe.extent().end()
        # figure out what to do with speed based on playback situation
        # should keep a smoothed running average of the x velocity of the mouse
        # we let the magnitude of the changes dictate the amt of smoothing -- so big changes dont get smoothed nearly as much
        smoothing = 3
        n = min(smoothing, len(self.recent_x))
        if n < 2:
            return # dont interpret mousemoves as scrubbing until we've seen a couple, could just be a nervous click      
        self.is_scrubbing = True
        x0 = self.recent_x[-n]
        xl = self.recent_x[-1]
        vx = (xl[0] - x0[0]) * self.wave_canv_w / ((xl[1] - x0[1])) # pixels per sec
        if self.playback_state == 'stopped':
            self.startPlaying()
        # self.chasing = ut.sign(self.wave_canvas_st_frame  - frame) == ut.sign(vx)
        # if not self.chasing:
        #      print('crossed!')
        spd = vx * 0.6 / (1 * self.pixels_per_second) # 0.6 keeps it from catching the mouse right away
        spd = min(max(spd, -38), 38)
        if spd == 0:
            spd = 0.05
        self.setSpeed(spd)
        
    def onMouseMoveWaveCanvasX(self, event):
        x_norm = (event.x / self.wave_canv_w)
        self.recent_x.append([x_norm, time.time()])
        frame = x_norm * self.t2._src_pe.extent().end()
        # figure out what to do with speed based on playback situation
        # should keep a smoothed running average of the x velocity of the mouse
        # we let the magnitude of the changes dictate the amt of smoothing -- so big changes dont get smoothed nearly as much
        smoothing = 9
        n = min(smoothing, len(self.recent_x))
        if n < 2:
            return # dont interpret mousemoves as scrubbing until we've seen a couple, could just be a smudgy click
        
        if self.playback_state == 'stopped':
            self.startPlaying()
                    
        self.is_scrubbing = True

        x0 = self.recent_x[-n]
        xl = self.recent_x[-1]
        vx = (xl[0] - x0[0]) * self.wave_canv_w / ((xl[1] - x0[1])) # pixels per sec
        spd = vx / (1 * self.pixels_per_second)
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
        h = 6
        n = int(min(1,4 * a) * (self.wavh / h))
        if n > self.peak:
             self.peak = n
             self.peak_age = 0
        else:
             self.peak_age += 1
             if self.peak_age > self.peak_hold_frames:
                  self.peak -= 1
        self.last_meter_n = n
        x0 = 2
        x1 = 27
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
        if self.peak ==0:
           return
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
    def draw_wave_hash(self):
        h = self.wavh + 2
        col = '#222F40'
        w = self.pixels_per_second
        for i in range(round(self.wave_canv_w / w)):
            x = i * w
            self.wave_canvas.create_line(x, 0, x, h, fill=col, width=1)
        self.wave_canvas.create_line(0, h, self.wave_canv_w, h, fill=col, width=1)
         
    def now_playing_callback(self, fr, amp): # callback once per frame from T2
        if self.stop_flag:
            self.t2._state = 0 # STATE_STOPPED, raises sd stop 
            return
        self.showAmp(amp)
        if self.current_frame == fr:
             return
        self.current_frame = fr

        prog = fr / self.t2._src_pe.extent().end()
        if prog > 1 or prog < 0:
            return
        x = round(prog * self.wave_canv_w)
        if self.last_x == x:
             return;
        self.last_x = x
        self.time_text.set(f"{fr/self.t2._src_pe.frame_rate():.2f}")
        self.frame_amps[x] = amp
        self.drawWaveSegment(x,amp)
        self.jog_canvas.delete('all')
        self.jog_canvas.create_line(x,1,x,self.jog_h+3, fill='yellow', width=1)

    def onCornerHit(self, evt):
        self.t2.choose_src(self.t2._ur_src_pe._src_pe)
        self.wave_canvas.delete('all')

    def save_window_geometry(self):
        with open("user_files/window_position.yaml", "w") as f:
            yaml.dump({"window_x": self.root.winfo_x(), "window_y": self.root.winfo_y(), "window_w": self.root.winfo_width(), "window_h": self.root.winfo_height()}, f)

    def load_window_geometry(self):
        try:
            with open("user_files/window_position.yaml", "r") as f:
                position = yaml.safe_load(f)
                return position["window_x"], position["window_y"], position["window_w"], position["window_h"]
        except FileNotFoundError:
            return None

    def cleanUp(self):
        self.pausePlaying()
        self.stop_flag = True
        self.save_window_geometry()
        self.root.after(10, self.root.destroy)