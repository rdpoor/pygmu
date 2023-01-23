# pygmu API 

## Sources

Wav_ReaderPE

    source = pg.WavReaderPE("samples/Tamper_MagnifyingFrame1.wav")
    pg.Transport(source).play()

BlitsigPE   

    pg.BlitsigPE(frequency=f, n_harmonics=h, channel_count=1, frame_rate=48000, waveform=w)

BlitsawPE

    pg.BlitSawPE(frequency=freq, n_harmonics=n_harmonics, frame_rate=frame_rate)

GaneshPE

    pg.GaneshPE(head_pe, body_pe, extend=True)

    Use the phase info from one PE and the magnitude into from another PE to 
	create an 'elephant head on a human body' (or any other combination).  

	NOTE: Since it is performing FFT of entire PEs in memory, the extent
	of the input PEs can't be too large...

TralfamPE

    takes a (finite) PE and spreads its spectrum randomly across the entire time
    span of the PE.

mogrify()

    Read in an entire sound file, take its fft, randomize the phase, and convert
    back into the time domain.


## Processing

## Utilities

    .gain(multiplier)

    