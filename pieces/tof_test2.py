import numpy as np
import os
import sys
import random
from threading import Thread
import wx
from opt3101 import OPT3101

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
    def __init__(self, opt_sensor):
        self.value = 0.5
        self.opt_sensor = opt_sensor
        self.opt_sensor.start(*OPT3101.find_ports())
        self.poll_thread = Thread(target=self.poll)
        self.poll_thread.start()

    def poll(self):
        while True:
            self.value = self.opt_sensor.read()
            # print(self.value, flush=True)

    def read(self):
        return self.value
        # return self.opt_sensor.read()

    def update_value(self, new_value):
        self.value = float(new_value)

class ToFPE(PygPE):
    """
    take readings from the ToF in real time
    """
    def __init__(self, sensor:TOFSensor):
        super(ToFPE, self).__init__()
        self._sensor = sensor

    def channel_count(self):
        return 1

    def render(self, requested:Extent):
        raw = self._sensor.read()
        norm = (raw-0.0) / (8000.0 - 0.0)
        # print(f'norm={norm}', flush=True)
        freq = ut.mtof((1-norm) * 70 + 5)

        return ut.const_frames(freq, self.channel_count(), requested.duration())

class WxPygPlayer(wx.Frame):
    def __init__(self, parent, title):
        super(WxPygPlayer, self).__init__(parent, title=title, size=(300, 200))

        self.sensor = ToFPE(TOFSensor(OPT3101()))

        self.SRATE = 48000
        # src = pg.NoisePE(gain=0.5, frame_rate=self.SRATE).gain(100)
        # flt = pg.BQBandPassPE(src, f0=440, q=400)
        # gain = pg.GainPE(flt, self.sensor)
        src = pg.BlitSawPE(self.sensor, n_harmonics=3, frame_rate=self.SRATE).gain(0.3)
        self.transport = pg.Transport(src, frame_rate=self.SRATE, blocksize=64)

        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        self.slider = wx.Slider(panel, value=int(self.sensor._sensor.read() * 100), minValue=0, maxValue=100, style=wx.SL_HORIZONTAL)
        self.slider.Bind(wx.EVT_SLIDER, self.update_sensor_value_from_slider)
        vbox.Add(self.slider, 1, flag=wx.ALIGN_CENTRE)

        panel.SetSizer(vbox)
        self.Centre()
        self.Show(True)
        self.Raise()

        self.audio_thread = Thread(target=self.transport.play)
        self.audio_thread.start()

    def update_sensor_value_from_slider(self, event):
        val = self.slider.GetValue() / 100.0
        self.sensor._sensor.update_value(val)


if __name__ == '__main__':
    app = wx.App(False)
    frame = WxPygPlayer(None, 'TOF 3')
    app.MainLoop()
