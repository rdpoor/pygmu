"""
ENV - Envelope generator test with ADSR and PULSE modes

"""
import numpy as np
import os
import sys
import random

script_dir = os.path.dirname(__file__)
pygmu_dir = os.path.join(script_dir, "..", "pygmu")
sys.path.append(pygmu_dir)
import pygmu as pg
import utils as ut

def stof(seconds):
    """Convert seconds to frames at 48kHz"""
    return int(seconds * 48000)

def main(mode="pulse", duration=0.5, attack=0.01, decay=0.2, sustain=0.02, release=0.13):

    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    # Load source audio
    src = pg.WavReaderPE(input_file).stereo()
    
    # Create envelope based on mode
    envelope = pg.EnvPE(
        mode=pg.EnvPE.PULSE if mode == "pulse" else pg.EnvPE.ADSR,
        duration=duration,
        attack=attack,
        decay=decay if mode == "adsr" else 0.0,
        sustain=sustain if mode == "adsr" else 0.0,
        release=release,
        frame_rate=48000
    )
    
    # For testing, crop source to reasonable length
    if mode == "pulse":
        test_duration = 8.0  # 8 seconds to hear multiple pulses
    else:
        test_duration = max(duration * 2, 3.0)  # At least 2x envelope duration
    
    src_extent = pg.Extent(0, stof(test_duration))
    src = src.crop(src_extent)
    
    # Apply envelope to source
    enveloped = pg.MulPE(src, envelope).crop(src_extent)
    
    # Write output
    dst = pg.WavWriterPE(enveloped, output_file)
    pg.FtsTransport(dst).play()

if __name__ == "__main__":
    main()