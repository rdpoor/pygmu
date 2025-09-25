import numpy as np
import math
import sys

def lerp(x, x0, x1, y0, y1):
    """
    Linear interpolation (aka two point line function): as x goes from x0 to x1,
    lerp(x) goes from y0 to y1.
    """
    return y0 + (x - x0) * (y1 - y0) / (x1 - x0)

def clamp(xlo, x, xhi):
    """
    Limit x such that xlo <= x <= xhi
    """
    if x < xlo:
        return xlo
    elif x > xhi:
        return xhi
    else:
        return x

def normalize_frames(numpy_frames):
    """
    Convert a 1-D array into a 2-D array with one row (pygmu mono frames)
    """
    if numpy_frames.ndim == 1:
        numpy_frames.shape = (1, numpy_frames.size)
    return numpy_frames

def channel_count(pygmu_frames):
    """
    Return the number of audio channels in pygmu-style frames
    """
    if pygmu_frames.ndim == 1:
        return 1
    else:
        return pygmu_frames.shape[0]

def frame_count(pygmu_frames):
    """
    Return the number of audio samples in pygmu-style frames
    """
    if pygmu_frames.ndim == 1:
        return pygmu_frames.size
    else:
        return pygmu_frames.shape[1]

def uninitialized_frames(n_channels, n_frames):
    """
    Create an uninitialized array of frames.
    """
    return np.ndarray([n_channels, n_frames], dtype=np.float32) # empty

def const_frames(value, n_channels, n_frames):
    """
    Create an array of frames containing a constant value.
    """
    return np.full([n_channels, n_frames], value, dtype=np.float32)

def ramp_frames(v0, v1, n_channels, n_frames):
    """
    Create an array of frames containing values ramping from v0 (inclusive) to
    v1 (exclusive).
    """
    ramp = np.linspace(v0, v1, num=n_frames, endpoint=False, dtype=np.float32)
    return ramp.repeat(n_channels).reshape(n_channels, -1)

def complex_to_magphase(c):
    """
    Convert a complex into magnitude and phase components, returned as a duple.
    """
    return np.abs(c), np.angle(c)

def magphase_to_complex(mag, phase):
    """
    Convert magnitude and phase into a complex.
    """
    return mag * np.exp(1j*phase)

RATIO_MIN = 1.1754944e-38  # np.finfo(np.float32).tiny

def sign(x):
    if x < 0:
        return -1
    if x > 0:
        return 1
    return 0

def ratio_to_db(ratio):
    ratio = np.maximum(ratio, RATIO_MIN)
    return 20 * np.log10(ratio)

def db_to_ratio(db):
    return np.power(10, db / 20)

def meter_string_for_rms(arr):
    nchans = len(arr)
    if nchans == 2:
        rms_left = clamp(0,arr[0],38)
        rms_right = clamp(0,arr[1],38)
        ctr = '.' if rms_left == 0 and rms_right == 0 else '|'
        ans = f'{" " * (38 - rms_left)}{"#" * (rms_left)}{ctr}{"#" * rms_right}'
    else:
        rms_left = clamp(0,arr[0],76)
        ans = f'|{"#" * rms_left}'
       
    return ans

def rms_for_audio_buffer(buf, scale=120):
    rms_arr = column_rms_linalg(buf)
    return [int(np.round(x * scale)) for x in rms_arr]

def column_rms_linalg(buf):
    return np.linalg.norm(buf, ord=2, axis=tuple(range(buf.ndim - 1))) / np.sqrt(np.prod(buf.shape[:-1]))

use_ansi_when_avaible = True

class ansicodes:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    CURSOR1 = '\033[1g'
    CURSOR2 = '\033[10;0f'
    CURSOR2B = '\033[11;0f'
    PREVLINE = '\033[1;F'
    PREVLINE2 = '\033[2;F'
    SCROLLUP = '\033[1;S'
    SCROLLDN = '\033[1;T'
    CLEAR = '\033[2K'
    HIDE_CURSOR = '\x1b[?25l'
    SHOW_CURSOR = '\x1b[?25h'
    ESC = '\x1b'
    RESET = f'{ESC}[0m'
    BOLD = f'{ESC}[1m'
    RED = f'{ESC}[31m'
    YELLOW = f'{ESC}[33m'
    GREEN = f'{ESC}[32m'

def terminal_has_ansi_support():
    # Check if the colorama module is available
    try:
        import colorama
        has_colorama = True
    except ImportError:
        has_colorama = False

    # Check if the operating system is Windows
    is_windows = sys.platform.startswith('win')

    # If colorama is available and the operating system is Windows, assume ANSI escape code support
    if is_windows and not has_colorama:
        return False
    else:
         return use_ansi_when_avaible

def clear_term_lines(howmany):
    if not terminal_has_ansi_support():
        return
    while howmany > 0:
        print(ansicodes.PREVLINE,ansicodes.CLEAR,'',end='\r')
        howmany -= 1

def show_cursor(flag):
    if not terminal_has_ansi_support():
        return
    if flag:
        print(ansicodes.SHOW_CURSOR,end='')
    else:
        print(ansicodes.HIDE_CURSOR,end='')

def print_warn(*args):
    if terminal_has_ansi_support():
        print(ansicodes.WARNING,*args,ansicodes.ENDC)
    else:
        print('WARNING:',*args)

def print_info(*args):
    if terminal_has_ansi_support():
        print(ansicodes.OKCYAN,*args,ansicodes.ENDC)
    else:
        print('INFO:',*args)

"""
Tuning Systems
"""

PHI = 1.6180339887

RenoldTemperament = [0, 1.914023, 3.6104998, 6.244825, 8.033583, -1.8587259, 0, 1.804308, 3.829694, 6.021689, 7.952746, 9.64478287] # cents deviation from 12ET

JustTemperament = [0, 11.73, 3.91, 15.64, -13.69, -1.96, -17.49, 1.96, 13.69, -15.64, -3.91, -11.73] # cents deviation from 12ET

Bohlen833Scale = [99.27, 235.77, 366.91, 466.18, 597.32, 733.82, 833.09] # ratios (in cents) of each step above the base

def freq_to_nearest_just_freq(frequency, a_hz = 440.0):
    # round to nearest frequency on the Just Intonation scale, based on C 
    C0 = a_hz * pow(2, -4.75)
    baseFrequency = C0
    rawSteps = 12 * np.log2(frequency / baseFrequency)
    steps = round(rawSteps)
    pc = steps % 12
    bentSteps = steps + (JustTemperament[pc]) / 100
    return baseFrequency * pow(2, bentSteps / 12) # ET freq for this note

def freq_to_nearest_renold_freq(frequency, a_hz = 432.0):
    # round to nearest frequency on the Renold Temperament, based on C 
    C0 = a_hz * pow(2, -4.75)
    baseFrequency = C0
    rawSteps = 12 * np.log2(frequency / baseFrequency)
    steps = round(rawSteps)
    pc = steps % 12
    bentSteps = steps + (RenoldTemperament[pc]) / 100
    return baseFrequency * pow(2, bentSteps / 12) # ET freq for this note

def pitch_to_freq(note, tuning_system = "12TET", a_hz = 440.0):
    """
    Return the frequency (floating hz) for a given MIDI note value (integers 1:128) under a given system of tuning.

    Possible values for tuning_system are:
        '12TET'     - Standard 12 tone equal temperament [default]

        'Renold'    - Developed by Maria Renold (1917-2003) -- https://128hertz.com/maria-renold-temperament/
                        a violin-friendly non-tempered temperament designed for use with A = 432
                        
        'Just'      - Just intontation aka Helmholz's scale -- https://pages.mtu.edu/~suits/scales.html
                        harmonic tuning based on the overtone series

        '833'       - A radical scale developed by Heinz Bohlen based on the golden ratio, with some striking properties -- http://www.huygens-fokker.org/bpsite/833cent.html
                        https://en.xen.wiki/w/833_Cent_Golden_Scale_(Bohlen)

    """


    et_freq = a_hz * pow(2.0, (note - 69) / 12.0)

    match tuning_system:
        case "12TET":
            freq = et_freq

        case "Renold":
            freq = freq_to_nearest_renold_freq(et_freq, a_hz)

        case "Just":
            freq = freq_to_nearest_just_freq(et_freq, a_hz)

        case "833":
            freq = a_hz * pow(2.0, (note - 69) / 12.0) #TODO

        case _:
            print("Unknown tuning system.",tuning_system," - sticking with 12TET.")
            freq = a_hz * pow(2.0, (note - 69) / 12.0)

    return freq

def mtof(midi_pitch):
    """
    Convert a midi pitch to a frequency
    """
    return 440 * math.pow(2, (midi_pitch-69) / 12)

def ftom(frequency):
    """
    Convert a frequency to a midi pitch
    """
    return 69 + 12 * math.log(frequency / 440.0)/math.log(2.0)

def velocity_to_db(velocity, reference=127):
    if velocity == 0:
        return -math.inf  # return negative infinity for silence
    else:
        return 20 * math.log10(velocity / reference)
    
def midi_to_note(midi_pitch):
    note_names = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B']
    octave = midi_pitch // 12 - 1
    note = note_names[midi_pitch % 12]
    return note + str(octave)

# https://docs.bokeh.org/en/latest/docs/user_guide/interaction/tools.html

from bokeh.plotting import figure, output_file, show, gridplot
from bokeh.layouts import column
import inspect
from scipy.signal import spectrogram
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

def plot_pes(pes, plot_types=["raw"], filepath="output.html", width=1200, height=250, title="PE Plots", y_ranges=None):
    # Convert pes to a list if it's a single PE
    if not isinstance(pes, list):
        pes = [pes]

    # Convert plot_types to a list if it's a single type
    if not isinstance(plot_types, list):
        plot_types = [plot_types]
    
    # Get the variable names of the PEs passed to the function
    caller_frame = inspect.currentframe().f_back
    caller_locals = caller_frame.f_locals
    var_names = {id(value): var_name for var_name, value in caller_locals.items() if id(value) in [id(pe) for pe in pes]}
    
    # Generate labels for each PE
    labels = []
    for pe in pes:
        pe_id = id(pe)
        if pe_id in var_names:
            labels.append(var_names[pe_id])
        else:
            labels.append(f"PE {len(labels) + 1}")
    
    # Find the largest non-empty, non-infinite extent among the PEs
    max_extent = None
    for pe in pes:
        extent = pe.extent()
        if not extent.is_empty() and not extent.is_indefinite():
            if max_extent is None or extent.duration() > max_extent.duration():
                max_extent = extent
    
    if max_extent is None:
        print("All PEs have empty or infinite extent. Skipping plotting.")
        return
    
    # Create a Bokeh figure for each plot type and each PE
    figures = {plot_type: [] for plot_type in plot_types}
    for plot_type in plot_types:
        for i, pe in enumerate(pes):
            if y_ranges is not None and i < len(y_ranges):
                y_range = y_ranges[i]
                p = figure(width=width, height=height, title=f"{labels[i]} ({plot_type})", y_range=y_range)
            else:
                p = figure(width=width, height=height, title=f"{labels[i]} ({plot_type})")
            figures[plot_type].append(p)
    
    # Iterate over each PE and plot its values for each plot type
    for i, pe in enumerate(pes):
        try:
            # Render the audio frames using the largest non-empty, non-infinite extent
            audio_frames = pe.render(max_extent)
            
            for plot_type in plot_types:
                if plot_type == "raw":
                    abs_values = np.abs(audio_frames)
                    duration = max_extent.duration()
                    time_values = np.linspace(0, duration / pe.frame_rate(), num=width, endpoint=False)
                    resampled_values = np.interp(time_values, np.linspace(0, duration / pe.frame_rate(), num=len(abs_values[0])), abs_values[0])
                    figures[plot_type][i].line(time_values, resampled_values, line_width=2)
                
                elif plot_type == "rms":
                    rms_values = np.sqrt(np.mean(audio_frames ** 2, axis=0))
                    duration = max_extent.duration()
                    time_values = np.linspace(0, duration / pe.frame_rate(), num=duration, endpoint=False)
                    figures[plot_type][i].line(time_values, rms_values, line_width=2)
                
                elif plot_type == "fft":
                    n = len(audio_frames[0])
                    f = np.fft.fftfreq(n, d=1/pe.frame_rate())
                    fft_values = np.abs(np.fft.fft(audio_frames[0]))
                    figures[plot_type][i].line(f[:n//2], fft_values[:n//2], line_width=2)
                
                elif plot_type == "spectrogram":
                    f, t, Sxx = spectrogram(audio_frames[0], pe.frame_rate())
                    Sxx = np.where(Sxx == 0, 1e-10, Sxx)  # Add small epsilon to avoid log10(0)
                    plt.pcolormesh(t, f, 10 * np.log10(Sxx))
                    plt.ylabel('Frequency [Hz]')
                    plt.xlabel('Time [sec]')
                    plt.title('Spectrogram')
                    plt.colorbar(label='Intensity [dB]')
                    plt.savefig('spectrogram.png')
                    plt.close()
                    figures[plot_type][i].image_url(url=['spectrogram.png'], x=0, y=0, w=1, h=1, anchor="bottom_left")
                
                elif plot_type == "waterfall":
                    f, t, Sxx = spectrogram(audio_frames[0], pe.frame_rate())
                    Sxx = np.where(Sxx == 0, 1e-10, Sxx)  # Add small epsilon to avoid log10(0)
                    fig = plt.figure()
                    ax = fig.add_subplot(111, projection='3d')
                    T, F = np.meshgrid(t, f)
                    ax.plot_surface(T, F, 10 * np.log10(Sxx), cmap='viridis')
                    ax.set_xlabel('Time [sec]')
                    ax.set_ylabel('Frequency [Hz]')
                    ax.set_zlabel('Intensity [dB]')
                    plt.title('Waterfall Spectrogram')
                    plt.savefig('waterfall.png')
                    plt.close()
                    figures[plot_type][i].image_url(url=['waterfall.png'], x=0, y=0, w=1, h=1, anchor="bottom_left")
              
                elif plot_type == "envelope":
                    env_values = np.abs(audio_frames[0])
                    duration = max_extent.duration()
                    time_values = np.linspace(0, duration / pe.frame_rate(), num=len(env_values), endpoint=False)
                    figures[plot_type][i].line(time_values, env_values, line_width=2)
                
                elif plot_type == "zero_crossing":
                    zero_crossings = np.where(np.diff(np.sign(audio_frames[0])))[0]
                    zero_crossing_rate = len(zero_crossings) / duration
                    time_values = np.linspace(0, duration / pe.frame_rate(), num=width, endpoint=False)
                    zcr_values = np.full(len(time_values), zero_crossing_rate)
                    figures[plot_type][i].line(time_values, zcr_values, line_width=2)
                
                elif plot_type == "peak":
                    peak_values = np.max(np.abs(audio_frames), axis=0)
                    duration = max_extent.duration()
                    time_values = np.linspace(0, duration / pe.frame_rate(), num=len(peak_values), endpoint=False)
                    figures[plot_type][i].line(time_values, peak_values, line_width=2)
        
        except Exception as e:
            print(f"Error occurred while processing {labels[i]}: {str(e)}")
            continue
    
    # Customize the plots
    for plot_type in plot_types:
        for p in figures[plot_type]:
            p.xaxis.axis_label = "Time (seconds)"
            p.yaxis.axis_label = "Amplitude"
    
    # Create a grid layout for the plots
    all_figures = []
    for plot_type in plot_types:
        all_figures.extend(figures[plot_type])
    grid = gridplot([[p] for p in all_figures], toolbar_location="above")
    
    # Save the grid to an HTML file
    output_file(filepath)
    
    # Display the grid
    show(grid)

# temp fix to avoid needing to pass in sr everywhere
FRAME_RATE = 48000
def stof(seconds):
    '''Convert seconds to frames (samples)'''
    return int(seconds * FRAME_RATE)
