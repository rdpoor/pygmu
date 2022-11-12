import numpy as np
import extent as Extent
import sounddevice as sd

class Transport(object):
    """
    Transport is the abstract base class for controlling the system.
    """

    FRAME_RATE = 48000
    CHANNEL_COUNT = 2

    def __init__(self, output_device=None,
        frame_rate=FRAME_RATE,
        blocksize=None,
        dtype=np.float32,
        latency=None,
        channel_count=CHANNEL_COUNT):
        self._output_device = output_device
        self._frame_rate = frame_rate
        self._blocksize = blocksize
        self._dtype = dtype
        self._latency = latency
        self._channel_count = channel_count

    def play(self, pe):
        self.pe = pe
        curr_frame = 0

        def callback(outdata, n_frames, time, status):
            nonlocal curr_frame
            if status:
                print(status)
            # "The output buffer contains uninitialized data and the callback
            # is supposed to fill it with proper audio data. If no data is
            # available, the buffer should be filled with zeros (e.g. by using
            # outdata.fill(0))."

            outdata.fill(0)
            requested = Extent.Extent(curr_frame, curr_frame + n_frames)
            (src_data, offset) = self.pe.render(requested, self._channel_count)
            # https://stackoverflow.com/questions/74414680/replacing-full-rows-of-2d-numpy-data
            outdata[offset:offset + src_data.shape[0], :] = src_data
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
                input()
        except KeyboardInterrupt:
            exit('')
        except Exception as e:
            exit(type(e).__name__ + ': ' + str(e))
