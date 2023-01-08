import numpy as np
import math

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

def uninitialized_frames(n_frames, n_channels):
    """
    Create an uninitialized array of frames.
    """
    return np.ndarray([n_frames, n_channels], dtype=np.float32) # empty

def const_frames(value, n_frames, n_channels):
    """
    Create an array of frames containing a constant value.
    """
    return np.full([n_frames, n_channels], value, dtype=np.float32)

def ramp_frames(v0, v1, n_frames, n_channels):
    """
    Create an array of frames containing values ramping from v0 (inclusive) to
    v1 (exclusive).
    """
    ramp = np.linspace(v0, v1, num=n_frames, endpoint=False, dtype=np.float32)
    return ramp.repeat(n_channels).reshape(-1, n_channels)

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

def ratio_to_db(ratio):
    return 20 * np.log10(ratio)

def db_to_ratio(ratio):
    return np.power(10, ratio / 20)

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

"""
Tuning Systems
"""

PHI = 1.6180339887

RenoldTemperament = [0, 1.914023, 3.6104998, 6.244825, 8.033583, -1.8587259, 0, 1.804308, 3.829694, 6.021689, 7.952746, 9.64478287]; # cents deviation from 12ET

JustTemperament = [0, 11.73, 3.91, 15.64, -13.69, -1.96, -17.49, 1.96, 13.69, -15.64, -3.91, -11.73]; # cents deviation from 12ET

Bohlen833Scale = [99.27, 235.77, 366.91, 466.18, 597.32, 733.82, 833.09] # ratios (in cents) of each step above the base

def freq_to_nearest_just_freq(frequency, a_hz = 440.0):
    # round to nearest frequency on the Just Intonation scale, based on C 
    C0 = a_hz * pow(2, -4.75)
    baseFrequency = C0
    rawSteps = 12 * np.log2(frequency / baseFrequency)
    steps = round(rawSteps)
    pc = steps % 12
    bentSteps = steps + (JustTemperament[pc]) / 100
    return baseFrequency * pow(2, bentSteps / 12); # ET freq for this note

def freq_to_nearest_renold_freq(frequency, a_hz = 432.0):
    # round to nearest frequency on the Renold Temperament, based on C 
    C0 = a_hz * pow(2, -4.75)
    baseFrequency = C0
    rawSteps = 12 * np.log2(frequency / baseFrequency)
    steps = round(rawSteps)
    pc = steps % 12
    bentSteps = steps + (RenoldTemperament[pc]) / 100
    return baseFrequency * pow(2, bentSteps / 12); # ET freq for this note

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
