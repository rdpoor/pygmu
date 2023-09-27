import numpy as np
import os
import sys
import random
from threading import Thread
import wx

script_dir = os.path.dirname(__file__)
pygmu_dir = os.path.join(script_dir, "..", "pygmu")
sys.path.append(pygmu_dir)

import pygmu as pg
import utils as ut
from extent import Extent
from pyg_pe import PygPE
from pyg_gen import PygGen
import sounddevice as sd


class TOFSensor:
    def __init__(self):
        self.value = 0.5

    def poll(self):
        return self.value

    def update_value(self, new_value):
        self.value = float(new_value)


class ToFTransport(pg.Transport):
    def __init__(self, src_pe, sensor, frame_rate, **kwargs):
        super().__init__(src_pe, frame_rate=frame_rate, **kwargs)
        self.sensor = sensor
        self.gain = 1
        self.param_name = 'Speed'

    def play(self):
        curr_frame = 0

        def callback(outdata, n_frames, time, status):
            nonlocal curr_frame
            sensor_value = self.sensor.poll()
            if self.param_name == 'Speed':
                speed = 0.2 + (sensor_value * 3.8)
                self._src_pe.set_speed(speed)
            elif self.param_name == 'Gain':
                self.gain = 0.1 + (sensor_value * sensor_value * 0.9)

            requested = Extent(curr_frame, curr_frame + n_frames)
            outdata[:] = self._src_pe.render(requested).T * self.gain
            curr_frame += n_frames

        with sd.OutputStream(
                callback=callback,
                samplerate=self._frame_rate,
                channels=self._channel_count):
            input('ctrl-c to quit')

class WxPygPlayer(wx.Frame):
    def __init__(self, parent, title):
        super(WxPygPlayer, self).__init__(parent, title=title, size=(300, 200))

        self.sensor = TOFSensor()
        self.SRATE = 48000
        src = pg.NoisePE(gain=0.5, frame_rate=self.SRATE).gain(100)
        flt = pg.BQBandPassPE(src, f0=440, q=400)
        warp = pg.WarpSpeedPE(flt, speed=1)

        self.transport = ToFTransport(warp, self.sensor, frame_rate=self.SRATE)

        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        self.slider = wx.Slider(panel, value=int(self.sensor.poll() * 100), minValue=0, maxValue=100, style=wx.SL_HORIZONTAL)
        self.slider.Bind(wx.EVT_SLIDER, self.update_sensor_value)
        vbox.Add(self.slider, 1, flag=wx.ALIGN_CENTRE)

        self.choice = wx.Choice(panel, choices=['Speed', 'Gain'])
        self.choice.SetSelection(0)
        self.choice.Bind(wx.EVT_CHOICE, self.on_choice)
        vbox.Add(self.choice, 1, flag=wx.ALIGN_CENTRE)

        panel.SetSizer(vbox)
        self.Centre()
        self.Show(True)
        self.Raise()

        self.audio_thread = Thread(target=self.transport.play)
        self.audio_thread.start()

    def on_choice(self, event):
        self.transport.param_name = self.choice.GetString(self.choice.GetSelection())

    def update_sensor_value(self, event):
        val = self.slider.GetValue() / 100.0
        self.sensor.update_value(val)


if __name__ == '__main__':
    app = wx.App(False)
    frame = WxPygPlayer(None, 'TOF 3')
    app.MainLoop()
