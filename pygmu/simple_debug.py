#!/usr/bin/env python

# Simple debug script without imports
frame_rate = 48000
duration = 0.55
attack = 0.01
release = 0.2

print("Input parameters:")
print("  Frame rate: {}".format(frame_rate))
print("  Duration: {}".format(duration))
print("  Attack: {}".format(attack))
print("  Release: {}".format(release))
print()

# Simulate the frame calculations from env_pe.py
duration_frames = duration * frame_rate  # Float for PULSE mode
attack_frames = attack * frame_rate
release_frames = release * frame_rate
total_envelope_frames = attack_frames + release_frames

print("Calculated frame values:")
print("  Duration frames: {}".format(duration_frames))
print("  Attack frames: {}".format(attack_frames))
print("  Release frames: {}".format(release_frames))
print("  Total envelope frames: {}".format(total_envelope_frames))
print()

print("Actual timing:")
print("  Duration in seconds: {}".format(duration_frames / frame_rate))
print("  Attack in seconds: {}".format(attack_frames / frame_rate))
print("  Release in seconds: {}".format(release_frames / frame_rate))
print("  Total envelope in seconds: {}".format(total_envelope_frames / frame_rate))
print()

# Check which code path would be used
if total_envelope_frames > duration_frames:
    print("Code path: COMPRESSION (attack + release > duration)")
    print("  Compression ratio: {}".format(total_envelope_frames / duration_frames))
    print("  This means envelope segments will be compressed to fit within duration")
else:
    print("Code path: NORMAL (attack + release <= duration)")
    zero_fill_frames = duration_frames - total_envelope_frames
    print("  Zero-fill duration: {} seconds".format(zero_fill_frames / frame_rate))
    print("  This means envelope runs normally, then zeros until next cycle")