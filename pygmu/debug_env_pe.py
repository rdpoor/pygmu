#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from env_pe import EnvPE

# Test with your parameters
frame_rate = 48000
duration = 0.55
attack = 0.01  # Adjust these to your actual values
release = 0.2  # Adjust these to your actual values

print("Input parameters:")
print("  Frame rate: {}".format(frame_rate))
print("  Duration: {}".format(duration))
print("  Attack: {}".format(attack))
print("  Release: {}".format(release))
print()

# Create envelope
env = EnvPE(EnvPE.PULSE, duration, attack=attack, release=release, frame_rate=frame_rate)

print("Calculated frame values:")
print("  Duration frames: {}".format(env._duration_frames))
print("  Attack frames: {}".format(env._attack_frames))
print("  Release frames: {}".format(env._release_frames))
print("  Total envelope frames: {}".format(env._attack_frames + env._release_frames))
print()

print("Actual timing:")
print("  Duration in seconds: {}".format(env._duration_frames / frame_rate))
print("  Attack in seconds: {}".format(env._attack_frames / frame_rate))
print("  Release in seconds: {}".format(env._release_frames / frame_rate))
print("  Total envelope in seconds: {}".format((env._attack_frames + env._release_frames) / frame_rate))
print()

# Check which code path is being used
total_envelope_frames = env._attack_frames + env._release_frames
if total_envelope_frames > env._duration_frames:
    print("Code path: COMPRESSION (attack + release > duration)")
    print("  Compression ratio: {}".format(total_envelope_frames / env._duration_frames))
else:
    print("Code path: NORMAL (attack + release <= duration)")
    print("  Zero-fill duration: {} seconds".format((env._duration_frames - total_envelope_frames) / frame_rate))