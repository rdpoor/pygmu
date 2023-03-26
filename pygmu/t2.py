import numpy as np
import sys
import extent
import array_pe
import warp_speed_pe
import sounddevice as sd

STATE_STOPPED = 0
STATE_PLAYING = 1
STATE_PAUSED = 2

class T2(object):

    def __init__(
        self,
        src_pe,
        output_device=None,
        frame_rate=None,
        blocksize=None,
        dtype=np.float32,
        latency=None,
        channel_count=None,
        skp=0,
        now_playing_callback=None):
        """
        Create a Transport object that will read and play samples from src_pe,
        with the added ability to change speed and jump to different frames.
        """
        self._src_pe = src_pe
        self._src_frame = 0
        self._output_device = output_device
        self.skp = 0
        if frame_rate is None:
            self._frame_rate = src_pe.frame_rate()
        else:
            self._frame_rate = frame_rate
        self._blocksize = blocksize
        self._dtype = dtype
        self._latency = latency
        if channel_count is None:
            self._channel_count = src_pe.channel_count()
        else:
            self.channel_count = channel_count
        self._stream = None
        self._warper = warp_speed_pe.WarpSpeedPE(self._src_pe, speed=1.0)
        self.reset()

    def callback(self, outdata, n_frames, time, status):
        if status:
            print(status)

        if self._state == STATE_STOPPED:
            raise sd.CallbackStop()

        elif self._state == STATE_PAUSED or self._speed == 0:
            # Continue to stream buffers of zeros while paused
            outdata[:] = np.zeros((n_frames, self._channel_count))

        elif self._speed == 1.0:
            # 1:1 playback speed
            start_frame = self._src_frame
            end_frame = start_frame + n_frames
            requested = extent.Extent(int(start_frame), int(end_frame))
            # Use the .T operator (transpose) to convert pygmu row form to
            # sounddevice column form.
            outdata[:] = self._src_pe.render(requested).T
            self._src_frame = end_frame

        else:
            # Use WarpSpeed to adjust the playback speed
            self._warper.set_speed(self._speed)
            # Implementation note: if you ask WarpSpeed to render frame F at
            # speed S, it will request frame F*S from the source. We want to
            # render self._src_frame from the source, so we request frame
            # self._src_frame / S
            start_frame = self._src_frame / self._speed
            end_frame = start_frame + n_frames
            requested = extent.Extent(int(start_frame), int(end_frame))
            # Use the .T operator (transpose) to convert pygmu row form to
            # sounddevice column form.
            outdata[:] = self._warper.render(requested).T
            # Note next starting frame
            self._src_frame = self._src_frame + (n_frames * self._speed)

        if self.now_playing_callback:
            self.skp = self.skp + 1 # experimentally skipping n frames to reduce dropouts
            if self.skp > 2:
                left_channel = outdata[:, 0]
                self.now_playing_callback(self._src_frame, np.sqrt(np.mean(np.square(left_channel))))
                self.skp = 0
    



    def play(self, frame=None, speed=None):
        """
        Start, resume or continue playing samples from the current frame.  For
        jog, set the frame.  For shuttle, set speed: 1.0 is normal, -1.0 is
        reverse, 0.1 is very slow forward, etc.
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
        return self._src_frame

    def set_frame(self, frame):
        """
        Jog to the specified frame, whether or not the transport is running.
        """
        self._src_frame = frame

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
        self._state = STATE_PAUSED

    def stop(self):
        """
        Halt playback
        set current frame to 0, set speed to 1.0.
        """
        self.reset()

    def reset(self):
        self._src_frame = 0
        self._speed = 1.0
        self._state = STATE_STOPPED
        self._stream = None
