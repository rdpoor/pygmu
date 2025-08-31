import os
import sys
script_dir = os.path.dirname(__file__)
pygmu_dir = os.path.join(script_dir, "..", "pygmu")
sys.path.append(pygmu_dir)
import pygmu as pg
import numpy as np

SRATE = 48000

def test_adsr():
    print("Testing ADSR envelope...")
    
    # Create ADSR envelope: 0.1s attack, 0.2s decay, 0.5 sustain, 0.3s release
    # Total duration: 2 seconds
    adsr_env = pg.EnvPE(
        mode=pg.EnvPE.ADSR,
        duration=2.0,
        attack=0.1,
        decay=0.2, 
        sustain=0.5,
        release=0.3,
        frame_rate=SRATE
    )
    
    # Apply to a sine wave
    sine = pg.SinPE(440, frame_rate=SRATE)
    result = pg.MulPE(sine.crop(adsr_env.extent()), adsr_env)
    
    print("Playing ADSR envelope applied to 440Hz sine wave...")
    # Just render a small sample to verify it works
    sample = result.render(pg.Extent(0, 1000))
    print(f"ADSR envelope sample shape: {sample.shape}, max value: {np.max(sample):.3f}")

def test_pulse():
    print("\nTesting PULSE envelope...")
    
    # Create pulsing envelope: 0.05s attack, 0.1s release, loops every 0.5s
    pulse_env = pg.EnvPE(
        mode=pg.EnvPE.PULSE,
        duration=0.5,  # Loop period
        attack=0.05,
        release=0.1,
        frame_rate=SRATE
    )
    
    # Apply to a sine wave for 4 seconds to hear multiple pulses
    sine = pg.SinPE(440, frame_rate=SRATE)
    four_seconds = pg.Extent(0, 4 * SRATE)
    result = pg.MulPE(sine.crop(four_seconds), pulse_env.crop(four_seconds))
    
    print("Playing PULSE envelope applied to 440Hz sine wave (4 seconds)...")
    # Just render a small sample to verify it works
    sample = result.render(pg.Extent(0, int(0.5 * SRATE)))  # First 0.5 seconds
    print(f"PULSE envelope sample shape: {sample.shape}, max value: {np.max(sample):.3f}")

if __name__ == "__main__":
    test_adsr()
    test_pulse()
    print("\nEnvelope tests complete!")