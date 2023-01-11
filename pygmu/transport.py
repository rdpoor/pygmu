import numpy as np
import extent as Extent
import sounddevice as sd
import utils as ut
import queue
import threading
import readchar
import sys
from pygmu import (Extent)
from fts_transport import FtsTransport
from wav_reader_pe import WavReaderPE
from wav_writer_pe import WavWriterPE
from crop_pe import CropPE
import tempfile

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
    def play(self, meter_type='none', max_silent_frames=400, replayable=False):
        curr_frame = 0
        silent_count = 0
        if self._src_pe.extent().is_indefinite():
            frames_per_col = self._frame_rate #1 col per sec
        else:
            frames_per_col = int((self._src_pe.extent().end() / 512) / 58)
        cur_col_sum = 0
        cur_block = 0
        show_meter = meter_type != 'none'
        def callback(outdata, n_frames, time, status):
            nonlocal curr_frame, silent_count, cur_col_sum, frames_per_col, cur_block, show_meter
            if status:
                print(status)
            # "The output buffer contains uninitialized data and the callback
            # is supposed to fill it with proper audio data. If no data is
            # available, the buffer should be filled with zeros (e.g. by using
            # outdata.fill(0))."
            requested = Extent(curr_frame, curr_frame + n_frames)
            outdata[:] = self._src_pe.render(requested)
            curr_frame += n_frames
            cur_block += 1
            rms_array = ut.rms_for_audio_buffer(outdata)
            if sum(rms_array) == 0:
                silent_count += 1
            else:
                silent_count = 0
            self.__frame_info_queue.put(silent_count)
            if show_meter:
                if self._use_ansi and meter_type == 'live':
                    meter_string = ut.meter_string_for_rms(rms_array) 
                    # move up a line, print the meter string, then pop back down
                    print(ut.ansicodes.PREVLINE, ut.ansicodes.CLEAR,meter_string)
                else:
                    cur_col_sum += rms_array[0]
                    if cur_block % frames_per_col == 0:
                        block_rms = int(((cur_col_sum / frames_per_col)  * len(amp_chars) / 90) + 0.85)
                        amp_ndx = block_rms % len(amp_chars)
                        cur_col_sum = 0
                        if silent_count < 2:
                            print(chr(amp_chars[amp_ndx]),end='')
                            sys.stdout.flush()

        try:
            with sd.OutputStream(
                device=self._output_device,
                samplerate=self._frame_rate,
                blocksize=self._blocksize,
                dtype=self._dtype,
                latency=self._latency,
                channels=self._channel_count,
                callback=callback):
                if not replayable:
                    print('press return to skip, q to exit')
                if not ut.terminal_has_ansi_support():
                    print('')
                if show_meter:
                    ut.show_cursor(False)
                    print('') # extra line feed so meter doesnt erase us
                while True:
                    # blocking call will wait for new info via the play callback
                    fr_info = self.__frame_info_queue.get()
                    if max_silent_frames != 0 and fr_info > max_silent_frames:
                        ut.show_cursor(True)
                        print('')
                        return ''
                    # non-blocking attempt to read a char from stdin via input_thread
                    # will ignore everything except return, 'q' and space, and only cares about space if we are replayable
                    if not input_queue.empty():
                        c = input_queue.get()
                        if c == '\n' or c == '\r': # [return], so we clear out the meter
                            ut.clear_term_lines(1)
                            print('')
                            print('')
                            ut.show_cursor(True)
                            return ''
                        if c == ' ' and replayable: # [space]
                            #ut.clear_term_lines(1)
                            print('')
                            print('')
                            #ut.show_cursor(True)
                            return c
                        if c == 'q': # 'q'
                            #ut.clear_term_lines(2)
                            print('')
                            ut.show_cursor(True)
                            sys.exit('')
        except KeyboardInterrupt:
            exit('')
        except Exception as e:
            exit(type(e).__name__ + ': ' + str(e))
    def term_play(self,meter_type='live', max_silent_frames=300,  max_dur_secs_for_infinite_sources=100):
        """
        Play to the output_device, with interactive options to skip, replay or quit the entire script
        [meter_type] option to draw a meter 'none', 'bars' or 'live' (only works on terms with ansi code support)
        [max_silent_frames ] if > 0, will automatically return after max_silent_frames of low signal
        """
        if self._src_pe.extent().is_indefinite():
            source_pe = CropPE(self._src_pe, Extent(0,self._src_pe.frame_rate() * max_dur_secs_for_infinite_sources))
            ut.print_warn('term_play() will crop its indefinite source to ',max_dur_secs_for_infinite_sources,'seconds')
        else:
            source_pe = self._src_pe
        tmpfile = tempfile.gettempdir()+'/transport.wav'
        FtsTransport(WavWriterPE(source_pe, tmpfile)).play()
        out = WavReaderPE(tmpfile)
        end_frame = out.extent().end()
        dur_str = 'duration: {0:.2f} '.format(end_frame / out.frame_rate())
        show_meter = meter_type != 'none'
        while True:
            print('press return to skip, q to exit, space to replay',dur_str,'\n',end='' if show_meter else '\n')
            #print('press return to skip, q to exit, space to replay   ',dur_str,end='\r')
            ret = Transport(out).play(meter_type, max_silent_frames, True)
            match ret:
                case ' ':
                    ut.clear_term_lines(4)
                    if ut.terminal_has_ansi_support():
                        print(ut.ansicodes.PREVLINE,end='\r')
                    print('') # loop back up to play again
                case _:
                    return('')
                    
amp_chars = [32,46,111,79,64,64]

def input_thread(input_queue):
    while True:
        # read single character off stdin
        input_queue.put(readchar.readchar())

input_queue = queue.Queue()
input_thread = threading.Thread(target=input_thread, args=(input_queue,))
input_thread.daemon = True
input_thread.start()

