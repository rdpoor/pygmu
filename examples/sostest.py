import os
import sys
import numpy as np
from scipy import signal

script_dir = os.path.dirname( __file__ )
pygmu_dir = os.path.join( script_dir, '..', 'pygmu' )
sys.path.append( pygmu_dir )
import pygmu as pg
import utils as ut

# channel 0 is a 1.0 impulse, channel 1 is a 10.0 impulse...
# NP: this is transposed from the canonical pygmu order
x = np.array([[1, 0, 0, 0, 0],
              [10, 0, 0, 0, 0]], dtype=np.float32)

n_channels = x.shape[0]
n_frames = x.shape[1]
print("n_channels=", n_channels, "n_frames=", n_frames)

# coefficients: [b0, b1, b2, a0, a1, a2]
# These specific coefficients define a first-order low pass filter
sos = [[0.01414656919729207, 0.0, 0.0, 1, -0.9858534308027079, 0.0]]

# create initial state
zi = np.zeros((1, n_channels, 2), dtype=np.float32)

# apply filter to transposed input, capture output and next initial state
y, zo = signal.sosfilt(sos, x, zi=zi)

# observe that channel 1 is 10x the values in channel 0
print(y)
