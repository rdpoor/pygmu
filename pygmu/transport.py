import numpy as np
import extent as Extent
import sounddevice as sd

class Transport(object):
    """
    Transport is the abstract base class for controlling the system.
    """

    def __init__(self, src_pe, output_device=None,
        frame_rate=None,
        blocksize=None,
        dtype=np.float32,
        latency=None,
        channel_count=None):
        self._src_pe = src_pe
        self._output_device = output_device
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
            self._channel_count = channel_count

    def play(self):
        curr_frame = 0

        def callback(outdata, n_frames, time, status):
            nonlocal curr_frame
            if status:
                print(status)
            # "The output buffer contains uninitialized data and the callback
            # is supposed to fill it with proper audio data. If no data is
            # available, the buffer should be filled with zeros (e.g. by using
            # outdata.fill(0))."

            requested = Extent.Extent(curr_frame, curr_frame + n_frames)
            # Use the .T operator (transpose) to convert pygmu row form to
            # sounddevice column form.
            outdata[:] = self._src_pe.render(requested).T 
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
