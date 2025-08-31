import os
import sys
script_dir = os.path.dirname(__file__)
pygmu_dir = os.path.join(script_dir, "..", "pygmu")
sys.path.append(pygmu_dir)
import pygmu as pg

SRATE = 48000

def pulsed_gate_example():
    """
    Demonstrate using EnvPE to create a pulsed gate effect.
    This applies regular pulses to gate audio on and off rhythmically.
    """
    print("Creating pulsed gate effect...")
    
    # Load source audio (or create a test tone)
    try:
        src = pg.WavReaderPE("samples/music/TamperFrame18.wav").stereo().normalize()
        print("Using audio file as source")
    except:
        # Fallback to generated tone if no audio file
        src = pg.SinPE(440, frame_rate=SRATE)
        four_seconds = pg.Extent(0, 4 * SRATE)
        src = src.crop(four_seconds)
        print("Using 440Hz sine wave as source")
    
    # Create pulsed gate envelope
    # Pulse every 0.25 seconds (4Hz), with 0.01s attack and 0.08s release
    pulse_gate = pg.EnvPE(
        mode=pg.EnvPE.PULSE,
        duration=0.25,     # Pulse every quarter second
        attack=0.01,       # Quick attack
        release=0.08,      # Longer release for smooth fade
        frame_rate=SRATE
    )
    
    # Apply the pulsed gate to the source
    gated_audio = pg.MulPE(src, pulse_gate)
    
    # Render a sample to verify
    sample = gated_audio.render(pg.Extent(0, SRATE))  # First second
    print(f"Gated audio sample shape: {sample.shape}")
    print(f"Max level: {sample.max():.3f}, Min level: {sample.min():.3f}")
    
    print("Pulsed gate effect created successfully!")
    print("To hear it, replace the sample render with: pg.Transport(gated_audio).play()")

if __name__ == "__main__":
    pulsed_gate_example()