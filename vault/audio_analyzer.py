import librosa
import yaml
import os
import time
import numpy as np
import scipy
import soundfile as sf
from wavinfo import WavInfoReader

# this expects to find our samples folder (or more likely a symbolic link to it) in the directory from which we invoke the script

# Function to truncate floating point values, just saving file size
def trunc(values, decs=0):
    return np.trunc(values*10**decs)/(10**decs)

# Function to compute the autocorrelation of a single frame's worth of audio
def autocorrelation(x):
    """
    Compute the autocorrelation of the signal, and find the lag at which the
    autocorrelation first reaches a maximum.
    """
    xp = x-np.mean(x)
    f = np.fft.fft(xp)
    f = np.array([np.real(v)**2+np.imag(v)**2 for v in f])
    pi = np.fft.ifft(f)

    denominator = np.sum(xp**2)
    if denominator != 0:
        acf = np.real(pi)[:x.size//2]/denominator
    else:
        acf = np.zeros_like(np.real(pi)[:x.size//2])  # or some other appropriate value
    
    # Exclude the zero-lag value by starting from 1
    # Add 1 because the argmax function returns a 0-based index
    dominant_period = np.argmax(acf[1:]) + 1
    strength = acf[dominant_period]
    
    return dominant_period, strength


# Frame and hop sizes.
frame_size = 1024 # Bigger is better to detect lower frequencies - 1024 can detect 85hz
hop_size = 256 # Smaller is better to detect onsets quickly

def analyze_file(filepath):

    # Get the file creation date
    stat = os.stat(filepath)
    modified_date = time.ctime(stat.st_atime)

    info = WavInfoReader(filepath)
    if info.bext:
        modified_date = info.bext.originator_date
    if info.info:
        if info.info.created_date:
            modified_date = info.info.created_date

    try:
        # Load audio file with librosa.
        # This automatically resamples everything to 22050, which is fine for our use case.
        y, sr = librosa.load(filepath) 
    except Exception as e:
        print(f"Error loading file {filepath}: {e}")
        return None

    duration = librosa.get_duration(y=y, sr=sr)
    sig_digits = 5

    # Analyzing tempo
    tempo = librosa.feature.tempo(y=y, sr=sr, max_tempo=220.0)
    tempogram = trunc(librosa.feature.tempogram(y=y, sr=sr), decs=sig_digits)
    tempogram_ratio = librosa.feature.tempogram_ratio(tg=tempogram, sr=sr)
    avg_tempogram_ratio = np.mean(np.array(tempogram_ratio), axis=1)

    # Computing the RMS and spectral properties.
    rms = trunc(librosa.feature.rms(y=y, frame_length=frame_size, hop_length=hop_size), decs=sig_digits)
    spectral_centroids = trunc(librosa.feature.spectral_centroid(y=y, sr=sr, n_fft=frame_size, hop_length=hop_size), decs=sig_digits)
    spectral_contrast = trunc(librosa.feature.spectral_contrast(y=y, n_fft=frame_size, hop_length=hop_size), decs=sig_digits)
    spectral_flatness = trunc(librosa.feature.spectral_flatness(y=y, n_fft=frame_size, hop_length=hop_size), decs=sig_digits)

    # Chroma feature extraction.
    chroma = trunc(librosa.feature.chroma_stft(y=y, sr=sr, n_fft=frame_size, hop_length=hop_size), decs=sig_digits)
    chroma_cens = trunc(librosa.feature.chroma_cens(y=y, sr=sr), decs=sig_digits)

    # Onset detection.
    S = librosa.feature.melspectrogram(y=y, sr=sr)
    onset_env = librosa.onset.onset_strength(S=S, sr=sr)
    onsets = librosa.onset.onset_detect(onset_envelope=onset_env, sr=sr, delta=0.31, wait=4)
    onset_times = trunc(librosa.frames_to_time(onsets, sr=sr), decs=sig_digits)

    # Chroma filter, harmonic extraction, and smoothing.
    # smoothing based on https://librosa.org/doc/main/auto_examples/plot_chroma.html#sphx-glr-auto-examples-plot-chroma-py
    chroma_orig = librosa.feature.chroma_cqt(y=y, sr=sr,  hop_length=hop_size)
    y_harm = librosa.effects.harmonic(y=y, margin=8)
    chroma_harm = librosa.feature.chroma_cqt(y=y_harm, sr=sr, hop_length=hop_size)
    chroma_filter = np.minimum(chroma_harm,
                              librosa.decompose.nn_filter(chroma_harm,
                                                          aggregate=np.median,
                                                          metric='cosine'))
    chroma_smooth = scipy.ndimage.median_filter(chroma_filter, size=(1, 9))

    # Convert chroma and tempogram ratio to list.
    hsl_list = chroma_to_list(chroma_smooth, sig_digits)
    # tgr_list = tgr_to_list(tempogram_ratio, sig_digits)


 # Divide the audio signal into frames

    # Frame size for autocorrelation.
    autocorr_frame_size = frame_size * 20
    autocorr_hop_size = hop_size * 20 * 4

    # Divide the audio signal into frames
    frames = librosa.util.frame(y, frame_length=autocorr_frame_size, hop_length=autocorr_hop_size)
    #print('frames', frames.shape)

    if len(y) >= autocorr_frame_size:
        frames = librosa.util.frame(y, frame_length=autocorr_frame_size, hop_length=autocorr_hop_size)
        autocorr = [autocorrelation(frame) for frame in frames.T]
    else:
        autocorr = [(0,0.001)]  

    autocorr_periods = [int(v[0]) for v in autocorr]
    autocorr_strengths = [float(v[1]) for v in autocorr]



    result = {
        'file': filepath,
        'modified_date': modified_date,
        'duration': round(float(duration), sig_digits),
        'bpm_est': round(float(tempo.tolist()[0]), sig_digits),
        'rms': [round(float(v), sig_digits) for v in rms.tolist()[0]],
        # 'tempogram_ratio': tgr_list,
        'avg_tempogram_ratio': avg_tempogram_ratio.tolist(),
        'spectral_centroids': [round(float(v), sig_digits) for v in spectral_centroids.tolist()[0]],
        'spectral_contrast': [round(float(v), sig_digits) for v in spectral_contrast.tolist()[0]],
        'spectral_flatness': [round(float(v), sig_digits) for v in spectral_flatness.tolist()[0]],
        'chroma': [round(float(v), sig_digits) for v in chroma.tolist()[0]],
        'chroma_cens': [round(float(v), sig_digits) for v in chroma_cens.tolist()[0]],
        'chroma_smooth': hsl_list,
        'onset_times': [round(float(v), sig_digits) for v in onset_times.tolist()],
        'autocorrelation_periods': autocorr_periods,
        'autocorrelation_strengths': autocorr_strengths,
      }
    return result

# Converts chroma_smooth to a list of hsl tuples, mapping the chroma values to hue, dist from low to high as saturation, and max as lightness
def chroma_to_list(chroma_smooth, sig_digits):
    hsl_list = []
    swapped_chroma = list(zip(*chroma_smooth))

    for chroma_vector in swapped_chroma:
        normalized_chroma = chroma_vector
        strongest_bin_index = np.argmax(normalized_chroma)
        delta = np.max(normalized_chroma) - np.min(normalized_chroma)
        saturation = delta
        lightness = np.max(normalized_chroma)
        hue = strongest_bin_index * (360 / len(chroma_vector))
        hsl_tuple = [round(float(v), sig_digits) for v in [hue,saturation,lightness]]
        hsl_list.append(hsl_tuple)
    
    return hsl_list

# Converts tempogram_ratio to a list by just taking the average of all the frames
# def tgr_to_list(tempogram_ratio, sig_digits):
#     tgr_list = []
#     swapped_tgv = list(zip(*tempogram_ratio))

#     for tgv in swapped_tgv:
#         normalized_v = tgv
#         tgrv = [round(float(v), sig_digits) for v in normalized_v]
#         tgr_list.append(tgrv)

#     return tgr_list

def analyze_directory(directory):
    n = 0
    for filename in os.listdir(directory):
        if filename.endswith('.wav'):
            filepath = os.path.join(directory, filename)
            n = n + 1
            print(n,filepath)
            result = analyze_file(filepath)
            if result is not None:
                with open('{}.yaml'.format(filepath), 'w') as outfile:
                  yaml.dump(result, outfile)
            else:
                print(f"Failed to analyze {filepath}")

analyze_directory('samples/music')
