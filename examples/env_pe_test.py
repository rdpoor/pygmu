"""
ENV - Envelope generator test with ADSR and PULSE modes

"""
import sys
import os
script_dir = os.path.dirname(__file__)
pygmu_dir = os.path.join(script_dir, "..", "pygmu")
sys.path.append(pygmu_dir)
import pygmu as pg
import utils as ut


def stof(seconds):
    """Convert seconds to frames at 48kHz"""
    return int(seconds * 48000)

def main(mode="adsr", duration=2.0, attack=0.1, decay=0.2, sustain=0.7, release=0.3):
    if len(sys.argv) < 3:
        print("Usage: python env_pe_test.py <input_file> <output_file> [mode] [duration] [attack] [decay] [sustain] [release]")
        print("  mode: 'adsr' or 'pulse' (default: adsr)")
        print("  duration: envelope duration in seconds (default: 2.0)")
        print("  attack: attack time in seconds (default: 0.1)")
        print("  decay: decay time in seconds (default: 0.2)")
        print("  sustain: sustain level 0-1 (default: 0.7)")
        print("  release: release time in seconds (default: 0.3)")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    # Parse optional arguments
    if len(sys.argv) > 3:
        mode = sys.argv[3].lower()
    if len(sys.argv) > 4:
        duration = float(sys.argv[4])
    if len(sys.argv) > 5:
        attack = float(sys.argv[5])
    if len(sys.argv) > 6:
        decay = float(sys.argv[6])
    if len(sys.argv) > 7:
        sustain = float(sys.argv[7])
    if len(sys.argv) > 8:
        release = float(sys.argv[8])
    
    print("ENV: Input file: ", input_file)
    print("ENV: Output file: ", output_file)
    print(f"ENV: Mode: {mode}")
    print(f"ENV: Duration: {duration}s")
    print(f"ENV: Attack: {attack}s")
    if mode == "adsr":
        print(f"ENV: Decay: {decay}s")
        print(f"ENV: Sustain: {sustain}")
    print(f"ENV: Release: {release}s")

    # Load source audio
    src = pg.WavReaderPE(input_file).stereo()
    
    # Create envelope based on mode
    if mode == "pulse":
        envelope = pg.EnvPE(
            mode=pg.EnvPE.PULSE,
            duration=duration,
            attack=attack,
            release=release,
            frame_rate=48000
        )
        # For pulse mode, crop to reasonable length
        test_duration = 8.0  # 8 seconds to hear multiple pulses
        src_extent = pg.Extent(0, stof(test_duration))
        src = src.crop(src_extent)
        # Also crop the envelope to the same duration
        envelope = envelope.crop(src_extent)
    else:  # ADSR mode
        envelope = pg.EnvPE(
            mode=pg.EnvPE.ADSR,
            duration=duration,
            attack=attack,
            decay=decay,
            sustain=sustain,
            release=release,
            frame_rate=48000
        )
        # For ADSR, use the envelope's natural extent
        src = src.crop(envelope.extent())
    
    # Apply envelope to source
    enveloped = pg.MulPE(src, envelope)
    
    # Write output
    dst = pg.WavWriterPE(enveloped, output_file)
    pg.FtsTransport(dst).play()

if __name__ == "__main__":
    main()