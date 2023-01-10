import numpy as np
import extent as Extent
import sounddevice as sd
import utils as ut
import queue
import threading
import readchar
import sys
from fts_transport import FtsTransport
from wav_reader_pe import WavReaderPE
from wav_writer_pe import WavWriterPE

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
        self._use_ansi = ut.terminal_has_ansi_support()
        self._latency = latency
        if channel_count is None:
            self._channel_count = src_pe.channel_count()
        else:
            self._channel_count = channel_count
        self.__frame_info_queue = queue.Queue()
    def play(self, show_meter=False, max_silent_frames = 400):
        curr_frame = 0
        silent_count = 0
        show_meter = show_meter and self._use_ansi
        def callback(outdata, n_frames, time, status):
            nonlocal curr_frame, silent_count
            if status:
                print(status)
            # "The output buffer contains uninitialized data and the callback
            # is supposed to fill it with proper audio data. If no data is
            # available, the buffer should be filled with zeros (e.g. by using
            # outdata.fill(0))."
            requested = Extent.Extent(curr_frame, curr_frame + n_frames)
            outdata[:] = self._src_pe.render(requested)
            curr_frame += n_frames
            rms_array = ut.rms_for_audio_buffer(outdata)
            if sum(rms_array) == 0:
                silent_count += 1
            else:
                silent_count = 0
            self.__frame_info_queue.put(silent_count)
            if show_meter:
                meter_string = ut.meter_string_for_rms(rms_array) 
                # move up a line, print the meter string, then pop back down
                print(ut.ansicodes.PREVLINE, ut.ansicodes.CLEAR,meter_string)
        try:
            with sd.OutputStream(
                device=self._output_device,
                samplerate=self._frame_rate,
                blocksize=self._blocksize,
                dtype=self._dtype,
                latency=self._latency,
                channels=self._channel_count,
                callback=callback):
                print('press return to skip, q to exit')
                if show_meter:
                    ut.show_cursor(False)
                    print('') # extra line feed so meter doesnt erase us
                while True:
                    # blocking call will wait for new info via the play callback
                    fr_info = self.__frame_info_queue.get()
                    if max_silent_frames != 0 and fr_info > max_silent_frames:
                        ut.show_cursor(True)
                        return ''
                    # non-blocking attempt to read a char from stdin via input_thread
                    if not input_queue.empty():
                        b =  bytes(input_queue.get(),'UTF-8')[0]
                        if b == 10: # [return], so we clear out the meter
                            ut.clear_term_lines(2)
                            print('')
                            ut.show_cursor(True)
                            return ''
                        if b == 32: # [space]
                            print('')
                            #ut.show_cursor(True)
                            return b
                        if b == 113: # 'q'
                            ut.clear_term_lines(2)
                            print('')
                            ut.show_cursor(True)
                            sys.exit('')
        except KeyboardInterrupt:
            exit('')
        except Exception as e:
            exit(type(e).__name__ + ': ' + str(e))
    def term_play(self,show_meter=True, max_silent_frames=300):
        """
        Play to the output_device, with interactive options to skip, replay or quit the entire script
        [show_meter] option to draw a meter on terms with ansi code support
        [max_silent_frames ] if > 0, will automatically return after max_silent_frames of low signal
        """
        output_filename = "/tmp/term_play.wav"
        FtsTransport(WavWriterPE(self._src_pe, output_filename)).play()
        out = WavReaderPE(output_filename)
        dur_str = 'duration: {0:.2f} '.format(out.extent().end() / out.frame_rate())
        while True:
            print('press return to skip, q to exit, space to replay   ',dur_str,end='\r')
            ret = Transport(out).play(show_meter, max_silent_frames)
            match ret:
                case 32:
                    ut.clear_term_lines(3)
                    if ut.terminal_has_ansi_support:
                        print(ut.ansicodes.PREVLINE,end='\r')
                    print('')
                case _:
                    return('')

def input_thread(input_queue):
    while True:
        # read single character off stdin
        input_queue.put(readchar.readchar())

input_queue = queue.Queue()
input_thread = threading.Thread(target=input_thread, args=(input_queue,))
input_thread.daemon = True
input_thread.start()

