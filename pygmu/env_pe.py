import numpy as np
from extent import Extent
from pyg_gen import PygGen
import pyg_exceptions as pyx
import utils as ut

class EnvPE(PygGen):
    """
    Envelope generator with ADSR and PULSE modes.
    
    ADSR mode: Attack-Decay-Sustain-Release envelope that plays once
    PULSE mode: Attack-Release envelope that loops continuously
    
    All timing parameters are in seconds.
    """
    
    ADSR = "adsr"
    PULSE = "pulse"
    
    def __init__(self, mode, duration, attack=0.01, decay=0.1, sustain=0.7, release=0.2, frame_rate=None):
        """
        Initialize envelope generator.
        
        Args:
            mode: Either EnvPE.ADSR or EnvPE.PULSE
            duration: Total duration of envelope in seconds (ADSR) or loop period (PULSE)
            attack: Attack time in seconds
            decay: Decay time in seconds (ADSR only)
            sustain: Sustain level (0.0-1.0, ADSR only)
            release: Release time in seconds
            frame_rate: Sample rate in Hz
        """
        super(EnvPE, self).__init__(frame_rate=frame_rate)
        if frame_rate is None:
            raise pyx.FrameRateMismatch("frame_rate must be specified")
        
        self._mode = mode
        self._duration = duration
        self._attack = attack
        self._decay = decay
        self._sustain = sustain
        self._release = release
        self._frame_rate = frame_rate
        
        # Validate parameters
        if mode not in [self.ADSR, self.PULSE]:
            raise ValueError(f"Mode must be '{self.ADSR}' or '{self.PULSE}'")
        if duration <= 0:
            raise ValueError("Duration must be positive")
        if not (0 <= sustain <= 1):
            raise ValueError("Sustain must be between 0 and 1")
        
        # Pre-calculate envelope shape for optimization
        self._envelope_cache = None
        self._cache_duration_frames = None
        self._generate_envelope_cache()
    
    def _generate_envelope_cache(self):
        """Pre-generate envelope shape for efficiency."""
        duration_frames = int(self._duration * self._frame_rate)
        self._cache_duration_frames = duration_frames
        
        if self._mode == self.ADSR:
            self._envelope_cache = self._generate_adsr_envelope(duration_frames)
        else:  # PULSE mode
            self._envelope_cache = self._generate_pulse_envelope(duration_frames)
    
    def _generate_adsr_envelope(self, duration_frames):
        """Generate ADSR envelope shape."""
        attack_frames = int(self._attack * self._frame_rate)
        decay_frames = int(self._decay * self._frame_rate)
        release_frames = int(self._release * self._frame_rate)
        
        # Calculate sustain duration
        sustain_frames = max(0, duration_frames - attack_frames - decay_frames - release_frames)
        
        envelope = np.zeros(duration_frames, dtype=np.float32)
        idx = 0
        
        # Attack phase: 0 to 1
        if attack_frames > 0:
            attack_end = min(idx + attack_frames, duration_frames)
            envelope[idx:attack_end] = np.linspace(0, 1, attack_end - idx)
            idx = attack_end
        
        # Decay phase: 1 to sustain level
        if idx < duration_frames and decay_frames > 0:
            decay_end = min(idx + decay_frames, duration_frames)
            envelope[idx:decay_end] = np.linspace(1, self._sustain, decay_end - idx)
            idx = decay_end
        
        # Sustain phase: constant sustain level
        if idx < duration_frames and sustain_frames > 0:
            sustain_end = min(idx + sustain_frames, duration_frames)
            envelope[idx:sustain_end] = self._sustain
            idx = sustain_end
        
        # Release phase: sustain level to 0
        if idx < duration_frames and release_frames > 0:
            envelope[idx:] = np.linspace(self._sustain, 0, duration_frames - idx)
        
        return envelope.reshape(1, -1)
    
    def _generate_pulse_envelope(self, duration_frames):
        """Generate PULSE envelope shape (attack-release)."""
        attack_frames = int(self._attack * self._frame_rate)
        release_frames = int(self._release * self._frame_rate)
        
        # Ensure we don't exceed duration
        total_env_frames = attack_frames + release_frames
        if total_env_frames > duration_frames:
            # Scale down proportionally
            scale = duration_frames / total_env_frames
            attack_frames = int(attack_frames * scale)
            release_frames = duration_frames - attack_frames
        
        envelope = np.zeros(duration_frames, dtype=np.float32)
        idx = 0
        
        # Attack phase: 0 to 1
        if attack_frames > 0:
            envelope[idx:idx + attack_frames] = np.linspace(0, 1, attack_frames)
            idx += attack_frames
        
        # Release phase: 1 to 0
        if idx < duration_frames and release_frames > 0:
            envelope[idx:idx + release_frames] = np.linspace(1, 0, release_frames)
        
        return envelope.reshape(1, -1)
    
    def render(self, requested: Extent):
        """Render envelope for the requested extent."""
        t0 = requested.start()
        t1 = requested.end()
        duration_samples = t1 - t0
        
        if self._mode == self.ADSR:
            # ADSR mode: envelope plays once, then silence
            if t0 >= self._cache_duration_frames:
                # Past the envelope duration, return silence
                return ut.const_frames(0.0, 1, duration_samples)
            
            # Clip to envelope duration
            effective_t1 = min(t1, self._cache_duration_frames)
            effective_duration = effective_t1 - t0
            
            if effective_duration <= 0:
                return ut.const_frames(0.0, 1, duration_samples)
            
            # Extract the relevant portion of the cached envelope
            result = self._envelope_cache[:, t0:effective_t1].copy()
            
            # Pad with zeros if needed
            if effective_duration < duration_samples:
                padding = ut.const_frames(0.0, 1, duration_samples - effective_duration)
                result = np.concatenate([result, padding], axis=1)
            
            return result
            
        else:  # PULSE mode
            # PULSE mode: envelope loops continuously
            result = np.zeros((1, duration_samples), dtype=np.float32)
            
            for i in range(duration_samples):
                sample_time = (t0 + i) % self._cache_duration_frames
                result[0, i] = self._envelope_cache[0, sample_time]
            
            return result
    
    def extent(self):
        """Return the extent of this generator."""
        if self._mode == self.ADSR:
            # ADSR has finite duration
            return Extent(0, self._cache_duration_frames)
        else:
            # PULSE mode is infinite
            return Extent(0, Extent.PINF)
    
    def channel_count(self):
        return 1
    
    def frame_rate(self):
        return self._frame_rate