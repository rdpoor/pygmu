import numpy as np
import os
import sys
import random

script_dir = os.path.dirname(__file__)
pygmu_dir = os.path.join(script_dir, "..", "pygmu")
sys.path.append(pygmu_dir)
import pygmu as pg
import utils as ut
from extent import Extent
from pyg_pe import PygPE
from pyg_gen import PygGen
import sounddevice as sd

import threading
import tkinter as tk
from tkinter import ttk

class InfiniteSinPE(PygGen):
    def __init__(self, frame_rate):
        super(InfiniteSinPE, self).__init__(frame_rate=frame_rate)
        self.frequency = 440  # Default frequency, this will be updated in real-time

    def render(self, requested: Extent):
        t0 = requested.start()
        t1 = requested.end()
        t = np.arange(t0, t1)
        return np.sin(2 * np.pi * self.frequency * t / self.frame_rate()).astype(np.float32).reshape(1, -1)

    def channel_count(self):
        return 1

class ToFTransport(pg.Transport):
    def __init__(self, src_pe, sensor, frame_rate, **kwargs):
        super().__init__(src_pe, frame_rate=frame_rate, **kwargs)
        self.sensor = sensor

    def play(self):
        curr_frame = 0

        def callback(outdata, n_frames, time, status):
            nonlocal curr_frame
            if status:
                print(status)
            sensor_value = self.sensor.poll()  # Poll sensor
            self._src_pe.frequency = map_sensor_to_frequency(sensor_value)  # Map to frequency

            requested = Extent(curr_frame, curr_frame + n_frames)
            outdata[:] = self._src_pe.render(requested).T  # Transpose to fit sounddevice's expectations
            curr_frame += n_frames

        try:
            with sd.OutputStream(
                device=self._output_device,
                samplerate=self._frame_rate,
                blocksize=self._blocksize,
                dtype=self._dtype,
                latency=self._latency,
                channels=self._channel_count,
                callback=callback):

                print('press return to quit')
                return input()
        except KeyboardInterrupt:
            exit('')
        except Exception as e:
            exit(type(e).__name__ + ': ' + str(e))

import tkinter as tk
from tkinter import ttk

class TOFSensor:
    def __init__(self):
        self.value = 0.5

    def poll(self):
        return self.value

    def update_value(self, new_value):
        self.value = float(new_value)

# Create a dummy function to map sensor value to frequency
def map_sensor_to_frequency(sensor_value):
    return 400 + (sensor_value * 180)

class UnthreadedPygPlayer:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("TOF Sensor Simulator")
        
        # Initialize TOFSensor instance
        self.sensor = TOFSensor()
        
        self.slider = ttk.Scale(self.root, from_=0.0, to_=1.0, value=self.sensor.poll(), orient="horizontal")
        self.slider.pack()
        self.slider.config(command=self.update_sensor_value)

        # Initialize these once
        self.SRATE = 48000
        self.sine_gen = InfiniteSinPE(frame_rate=self.SRATE)
        self.transport = ToFTransport(self.sine_gen, self.sensor, frame_rate=self.SRATE)
        self.transport.play()

        self.root.after(100, self.setFreqFromSensor)  # Run the function after a 100 ms delay
        self.root.mainloop()    

    def update_sensor_value(self, val):
        self.sensor.update_value(val)
        print(f"Sensor Value: {self.sensor.poll()}, Frequency: {map_sensor_to_frequency(self.sensor.poll())}")

    def setFreqFromSensor(self):
        # Only update the frequency here
        self.sine_gen.frequency = map_sensor_to_frequency(self.sensor.poll())
        #self.transport.play()
        self.root.after(100, self.setFreqFromSensor)  # Reschedule itself



if __name__ == "__main__":
    app = UnthreadedPygPlayer()