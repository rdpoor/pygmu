import numpy as np
import sys
import extent
import array_pe
import timewarp_pe
import sounddevice as sd

STATE_STOPPED = 0
STATE_PLAYING = 1
STATE_PAUSED = 2

class T2(object):

    def __init__(
        self,
        root_pe,
        file=None,
        output_device=None,
        frame_rate=None,
        blocksize=None,
        dtype=np.float32,
        latency=None,
        channel_count=None):
        """
        Create a Transport object that will read samples from root_pe.  If file
        is None, Transport will render samples into a temporary file and delete
        the file upon completion or a call to Transport.stop().  If file names a
        writable filename, the sample data will be saved in that file.  And if
        it is the special symbol REAL_TIME, samples will be rendered without
        writing an intermediate file.
        """
        self._root_pe = root_pe
        self._file = file
        self._output_device = output_device
        if frame_rate is None:
            self._frame_rate = root_pe.frame_rate()
        else:
            self._frame_rate = frame_rate
        self._blocksize = blocksize
        self._dtype = dtype
        self._latency = latency
        if channel_count is None:
            self._channel_count = root_pe.channel_count()
        else:
            self.channel_count = channel_count
        self._stream = None
        self.reset()

    def callback(self, outdata, n_frames, time, status):
        if status:
            print(status)
        if self._state == STATE_STOPPED:
            raise sd.CallbackStop()
        elif self._state == STATE_PAUSED:
            outdata[:] = np.zeros((n_frames, self._channel_count))
        elif self._speed == 1.0:
            # 1:1 playback speed
            end_frame = self._frame + n_frames
            requested = extent.Extent(self._frame, end_frame)
            # Use the .T operator (transpose) to convert pygmu row form to
            # sounddevice column form.
            outdata[:] = self._root_pe.render(requested).T
            self._frame = end_frame
        else:
            end_x = self._frame + n_frames
            end_y = self._frame + n_frames * self._speed
            requested = extent.Extent(self._frame, end_x)
            timeline = np.linspace(
                self._frame,
                end_y,
                n_frames,
                endpoint = False,
                dtype = np.float32).reshape(1, -1)
            timeline_pe = array_pe.ArrayPE(timeline)
            warper = timewarp_pe.TimewarpPE(self._root_pe, timeline_pe)
            # Use the .T operator (transpose) to convert pygmu row form to
            # sounddevice column form.
            outdata[:] = warper.render(requested).T
            self._frame = int(round(end_y))

    def play(self, frame=None, speed=None):
        """
        Start or resume playing samples from the current frame.  For scrubbing,
        speed sets the playback speed: 1.0 is normal, -1.0 is reverse, 0.1
        is very slow forward, etc.
        """
        if self._stream is None:
            self._stream = sd.OutputStream(
                device=self._output_device,
                samplerate=self._frame_rate,
                blocksize=self._blocksize,
                dtype=self._dtype,
                latency=self._latency,
                channels=self._channel_count,
                callback=self.callback)

        if frame is not None:
            self.set_frame(frame)
        if speed is not None:
            self.set_speed(speed)

        if self._state == STATE_STOPPED:
            self._stream.start()

        self._state = STATE_PLAYING

    def get_frame(self):
        """
        Return the current frame position.  (Also valid while the transport is
        running.
        """
        return self._frame

    def set_frame(self, frame):
        """
        Jog to the specified frame, whether or not the transport is running.
        """
        self._frame = frame

    def get_speed(self):
        """
        Return the current speed ratio.
        """
        return self._speed

    def set_speed(self, speed):
        """
        Set the current speed ratio, used for scrubbing.
        """
        if speed == 0:
            self.pause()
        else:
            self._speed = speed

    def pause(self):
        """
        Pause playback without modifying the current position or speed ratio.
        Note: the DAC continues to run, but will be fed buffers of zeros.
        """
        self._is_paused = True

    def stop(self):
        """
        Halt playback
        set current frame to 0, set speed to 1.0.
        """
        self.reset()

    def reset(self):
        self._frame = 0
        self._speed = 1.0
        self._state = STATE_STOPPED
