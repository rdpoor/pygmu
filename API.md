# pygmu API 

## Sources

Wav_Reader_PE

    source = pg.WavReaderPE("samples/Tamper_MagnifyingFrame1.wav")
    pg.Transport(source).play()

BlitsigPE   

    pg.BlitsigPE(frequency=f, n_harmonics=h, channel_count=1, frame_rate=48000, waveform=w)

BlitsawPT

    pg.BlitSawPE(frequency=freq, n_harmonics=n_harmonics, frame_rate=frame_rate)



## Processing

## Utilities

    .gain(multiplier)

    