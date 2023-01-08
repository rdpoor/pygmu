// A familiar little ditty.  The original "score" consisted of 20,000
// lines of code.  This one is around 100 (w/o the comments).  Times
// change.
//
// Thanks, Andy!!
//
// Robert Poor <r@alum.mit.edu>, 26 April 2009

class Voice {

    0.1 => float PITCH_EPSILON;

    BlitSaw _ug;		// use bandlimited sawtooth

    // We keep everything in terms of pitch until the final setting
    // of the voice frequency.
    float _curr_pitch;
    float _random_pitch;
    float _final_pitch;

    // Patch the voice into the DAC output and initialize a few other
    // things
    fun void setup(float final_pitch) {
	final_pitch => _final_pitch;
	_ug => dac;
	_ug.harmonics(8);
	_ug.gain(0.2);
	pick_random_pitch() => _random_pitch => _curr_pitch;
    }

    // Compute some output.  Damping determines how quickly the voice
    // can glissando (measured in semitones per second).  Obedience is
    // how closely it adheres to the final pitch: 1.0 is strict
    // obedience, at 0.0, the voice randomly picks its own pitches.
    // 
    fun void step(float damping, float obedience) {
	// pick a new random pitch if needed
	if (Std.fabs(_curr_pitch - _random_pitch) < PITCH_EPSILON) {
	    pick_random_pitch() => _random_pitch;
	}
	
	_random_pitch * (1 - obedience) + _final_pitch * obedience 
	    => float target_pitch;
	
	// Move _curr_pitch towards the target pitch at a rate
	// determined by damping (semitones per second)
	_curr_pitch * (1.0 - damping) + target_pitch * damping => _curr_pitch;

	// Set the frequency already...
	_ug.freq(Std.mtof(_curr_pitch));
    }

    fun float pick_random_pitch() {
	return Std.ftom(Std.rand2f(200.0, 400.0));
    }

} // voice

// Returns a value as a function of time, using linear interpolation
// between the given time/value pairs.  Stick on the (first/last)
// value if time falls outside the range.
class LinSeg {

    float _x[];
    float _y[];
    int _cursor;

    fun void setup(float x[], float y[]) {
	if (x.size() != y.size()) {
	    <<< "LinSeg error: arrays are different length" >>>;
	} else if (x.size() < 2) {
	    <<< "LinSeg error: arrays must be at least 2 elements long" >>>;
	}
	x @=> _x;
	y @=> _y;
	0 => _cursor;
    }

    fun float step(float u) {
	if (u < _x[0]) {
	    return _y[0];
	} else if (u > _x[_x.size()-1]) {
	    return _y[_y.size()-1];
	} else if (u > _x[_cursor+1]) {
	    _cursor + 1 => _cursor;
	    return step(u);
	} 

	// barring pathological inputs, now
	// x[cursor] < u < x[cursor+1]

	// simple linear interpolation
	_x[_cursor] => float x0;
	_x[_cursor+1] => float x1;
	_y[_cursor] => float y0;
	_y[_cursor+1] => float y1;
	return y0 + (u - x0) * (y1 - y0) / (x1 - x0);
    }
}

// ================================================================
// performance parameters

Voice @ voices[0];
LinSeg amplitude;
LinSeg damping;
LinSeg obedience;

// how often we update freq and amplitude
0.05::second => dur dt;
dt/(1::second) => float ds;

// The original is not quite 150Hz, nor is it quote D...
50.2 => float TONIC;
// How much we randomize the final pitches (in semitones)
0.1 => float PITCH_FUZZ;

[TONIC-24, TONIC-24, TONIC-24, TONIC-24, TONIC-12, TONIC-12, 
 TONIC-12, TONIC-12, TONIC-5, TONIC-5, TONIC, TONIC, 
 TONIC, TONIC, TONIC+7, TONIC+7, TONIC+7, TONIC+7, 
 TONIC+12, TONIC+12, TONIC+19, TONIC+19, TONIC+24, TONIC+24,
 TONIC+31, TONIC+31,  TONIC+36, TONIC+36] @=> 
    float final_pitches[];

amplitude.setup([0.0, 12.0, 20.0, 28.0], [0.0, 1.0, 1.0, 0.0]);
damping.setup([0.0, 8.0, 16.0, 28.0], [0.5*ds, 3.0*ds, 2.0*ds, 1.0*ds]);
obedience.setup([0.0, 8.0, 16.0, 28.0], [0.0, 0.0, 1.0, 1.0]);

// ================================================================
// Assemble the orchestra...

for (0=>int i; i<final_pitches.size(); i++) {
    voices << new Voice;
    voices[i].setup(final_pitches[i] + Std.rand2f(-PITCH_FUZZ, PITCH_FUZZ));
}

// ================================================================
// Write to a sound file is an argument is given

if (me.args() > 0) {
    dac => Gain g => WvOut w => blackhole;
    0.5 => g.gain;
    me.arg(0) => w.wavFilename;
    <<< "writing output to file", w.filename() >>>;
}

// ================================================================
// And let the show begin...

now => time t0;
now + 30::second => time t1;

while (now < t1) {
    // step the control parameters
    (now - t0)/(1::second) => float t;
    amplitude.step(t) => float amp;
    damping.step(t) => float damp;
    obedience.step(t) => float obey;

    // set gain and frequencies
    dac.gain(amp);
    for (0=>int i; i<voices.size(); i++) {
	voices[i].step(damp, obey);
    }

    // advance the time
    now+dt => now;
}
