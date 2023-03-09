# pygmu API 

## The `PygPE` base class

All subclasses of PygPE provide the following methods:

### `render(extent)`

### `extent()`

### `channel_count()`

### `frame_rate()`

## Generators

The following are "generators" inasmuch as they they produce a signal rather 
than modify an existing signal:

### `ArrayPE(frames, frame_rate=None)`

A generator with a fixed array of source frames.  

* frames: Either a 1-D array (for single channel) or 2-D array of frame data
with one row per channel.  Note that the first element of the array corresponds 
to time=0.
* frame_rate: (Optional) Declares the frame rate of the output.

#### Example

To create a stream with five stereo frames, you could do this:

```
    pe = ArrayPE([[0, 1, 2, 3, 4], [0, 1, 2, 3, 4]])
```

### `BlitSawPE(frequency=440.0, n_harmonics=0, frame_rate=None)`

### `ConstPE(value, frame_rate=None)`

### `GaneshPE(head_pe, body_pe, extend=True)`

### `IdentityPE(frame_rate=None)`

### `ImpulsePE(frame_rate=None)`

### `NoisePE(gain=1.0, frame_rate=None)`

### `PwmPE(period, duty_cycle, frame_rate=None)`

### `RanpPE(self, start_v, end_v, extent:Extent, frame_rate=None)`

### `SegmentsPE(time_value_pairs, interpolation='ramp', frame_rate=None)`

### `SinPE(requency=440, amplitude=1.0, phase=0.0, frame_rate=None)`

### `TralfamPE(src_pe)`

### `WavReaderPE(filename)`

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

#### AbsdPE
#### BiquadpPE
#### CachePE
#### CombPE
#### CompLimPE
#### CompressorPE
#### ConvolvePE
#### CropPE
#### TimeShiftPE
#### EnvDetectPE
#### FilterPE
#### GainPE
#### GainDbPE
#### GravyPE
#### InterpolatePE
#### LimiterPE
#### LoopPE
#### MixPE
#### MonoPE
#### MulPE
#### PrintPE
#### ReversePE
#### SnippetPE
#### SpatialPE
#### SplicePE
#### SpreadPE
#### TimewarpPE
#### TralfamPE
#### WarpSpeedPE
#### WavWriterPE

## Utilities
     
    .biquad(gain,freq,q,type)

    .time_shift(time)
        shifts the PE by time frames

    .gain(multiplier)

    .splice(fade_in_duration, fade_out_duration)

    .interpolate(speed_multiplier)

    .limit_a(threshold_db=-10, headroom_db=3)
        simple limiter with reasonable defaults

    .loop(length)
        infinite extent looping

    .mono()

    .pan(degree=0, curve='cosine')
        degree: -90 = hard left, 0 = center, 90 = hard right
        curve: one of the following:  As theta goes from hard left to hard right:
          'none' - no amplitude scaling -- time delay only
          'linear' - left amplitude ramps linearly 1.0 to 0.0, right from 0.0 to 1.0, 0.5 at center
          'cosine' - left ramps by cosine from 1.0 to 0.0, right ramps by sin, 0.7 at center

    .reverse(infinite_end=55)
        reverse the frames, for pes of infinite extent, requires a non-infinite ending time (infinite_end) in seconds

    .spread(channel_count=2)


## Status / Checklist

See: 
* https://realpython.com/documenting-python-code/
* https://requests.readthedocs.io/en/master/
* https://github.com/requests/requests/tree/master/docs

Checklist:

* name: name of the module
* doc?: are the functions documented?
* test%: unit test code coverage
* m/s?: does it handle mono only?  or mono/stereo?
* example?: is there example code (separate from unit test)?
* notes: issues, comments, etc.

| name | doc? | test% | m/s? | example? | notes |
| ---- | ---- | ----- | -----| -------- | ----- |
| `abs_pe.py` | y | 100 |   |   |   |
| `array_pe.py` | y | 100 |   |   |   |
| `biquad2_pe.py` | n | -na- |   |   | has glitches |
| `blit_saw_pe.py` | n | 100 |   |   |   |
| `cache_pe.py` | n | 100 |   |   |   |
| `comb_pe.py` | n | 100 |   |   |   |
| `comp_lim_pe.py` | n | 100 |   |   |   |
| `compressor_pe.py` | n | 100 |   |   |   |
| `const_pe.py` | n | 100 |   |   |   |
| `convolve_pe.py` | n | 100 |   |   |   |
| `crop_pe.py` | n | 100 |   |   |   |
| `time_shift_pe.py` | n | 100 |   |   |   |
| `env_detect_pe.py` | n | 100 | ms  |   |   |
| `filter_pe.py` | n | 42 |   |   | deprecated?  |
| `gain_db_pe.py` | n | n |   |   | replaced by gain_pe |
| `gain_pe.py` | n | 100 |   |   |   |
| `ganesh_pe.py` | n | 32 |   |   |   |
| `gravy_pe.py` | n | 31 |   |   | deprecated? |
| `identity_pe.py` | n | 100 |   |   |   |
| `impulse_pe.py` | n | 100 |   |   |   |
| `interpolate_pe.py` | n | 32 |   |   | replaced by timewarp? |
| `limiter_a_pe.py` | n | 58 |   |   |   |
| `limiter_pe.py` | n | 38 |   |   |   |
| `loop_pe.py` | n | 100 |   |   |   |
| `map_pe.py` | n | 50 |   |   |   |
| `mix_pe.py` | n | 32 |   |   |   |
| `mono_pe.py` | n | 100 |   |   |   |
| `mul_pe.py` | n | 32 |   |   |   |
| `noise_pe.py` | n | 100 |   |   |   |
| `print_pe.py` | n | 50 |   |   |   |
| `pwm_pe.py` | n | 100 |   |   |   |
| `pyg_pe.py` | n | 62 |   |   |   |
| `ramp_pe.py` | n | 91 |   |   |   |
| `reverse_pe.py` | n | 29 |   |   |   |
| `segments_pe.py` | n | 100 |   |   |   |
| `sin_pe.py` | n | 100 |   |   |   |
| `snippet_pe.py` | n | 50 |   |   |   |
| `spatial_pe.py` | n | 41 |   |   |   |
| `splice_pe.py` | n | 100 |   |   |   |
| `spread_pe.py` | n | 100 |   |   |   |
| `timewarp_pe.py` | n | 31 |   |   |   |
| `tralfam_pe.py` | n | 19 |   |   |   |
| `wav_reader_pe.py` | n | 32 |   |   |   |
| `wav_writer_pe.py` | n | 36 |   |   |   |
