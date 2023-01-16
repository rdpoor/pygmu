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
#### DelayPE
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
#### WavWriterPE

## Utilities

    .gain(multiplier)

    