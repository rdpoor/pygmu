import numpy as np
from extent import Extent
from pyg_gen import PygGen
import pyg_exceptions as pyx

class EnvPE(PygGen):
    """
    Envelope generator with ADSR and PULSE modes, following RampPE's idiomatic patterns.
    
    ADSR mode: Attack-Decay-Sustain-Release envelope that holds final value after completion
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
        
        # Convert times to frames
        self._duration_frames = int(self._duration * self._frame_rate)
        self._attack_frames = int(self._attack * self._frame_rate)
        self._decay_frames = int(self._decay * self._frame_rate)
        self._release_frames = int(self._release * self._frame_rate)
        
        # Calculate ADSR phase boundaries and final value
        self._attack_end = self._attack_frames
        self._decay_end = self._attack_end + self._decay_frames
        self._sustain_end = max(self._decay_end, self._duration_frames - self._release_frames)
        self._release_end = self._duration_frames
        
        # Determine final envelope value for ADSR mode
        self._final_value = self._calculate_final_value()
    
    def _calculate_final_value(self):
        """Calculate the final envelope value at the end of the duration."""
        if self._mode == self.PULSE:
            return 0.0  # PULSE always ends at 0
        
        # For ADSR, determine where we end up at duration_frames
        if self._duration_frames <= self._attack_end:
            # Ends during attack phase
            return self._lerp_attack(self._duration_frames)
        elif self._duration_frames <= self._decay_end:
            # Ends during decay phase
            return self._lerp_decay(self._duration_frames)
        elif self._duration_frames <= self._sustain_end:
            # Ends during sustain phase
            return self._sustain
        else:
            # Ends during release phase
            return self._lerp_release(self._duration_frames)
    
    def _lerp_attack(self, frame):
        """Linear interpolation during attack phase."""
        if self._attack_frames == 0:
            return 1.0
        progress = frame / self._attack_frames
        return progress
    
    def _lerp_decay(self, frame):
        """Linear interpolation during decay phase."""
        if self._decay_frames == 0:
            return self._sustain
        progress = (frame - self._attack_end) / self._decay_frames
        return 1.0 + progress * (self._sustain - 1.0)
    
    def _lerp_release(self, frame):
        """Linear interpolation during release phase."""
        if self._release_frames == 0:
            return 0.0
        progress = (frame - self._sustain_end) / self._release_frames
        return self._sustain + progress * (0.0 - self._sustain)
    
    def _lerp_pulse_attack(self, frame):
        """Linear interpolation during pulse attack phase."""
        if self._attack_frames == 0:
            return 1.0
        progress = frame / self._attack_frames
        return progress
    
    def _lerp_pulse_release(self, frame):
        """Linear interpolation during pulse release phase."""
        if self._release_frames == 0:
            return 0.0
        progress = (frame - self._attack_frames) / self._release_frames
        return 1.0 + progress * (0.0 - 1.0)
    
    def _envelope_value_at(self, frame):
        """Calculate envelope value at a specific frame."""
        if self._mode == self.ADSR:
            return self._adsr_value_at(frame)
        else:
            return self._pulse_value_at(frame)
    
    def _adsr_value_at(self, frame):
        """Calculate ADSR envelope value at a specific frame."""
        if frame < 0:
            return 0.0
        elif frame >= self._duration_frames:
            return self._final_value
        elif frame <= self._attack_end:
            return self._lerp_attack(frame)
        elif frame <= self._decay_end:
            return self._lerp_decay(frame)
        elif frame <= self._sustain_end:
            return self._sustain
        else:
            return self._lerp_release(frame)
    
    def _pulse_value_at(self, frame):
        """Calculate PULSE envelope value at a specific frame (with looping)."""
        # Apply modulo to create looping behavior
        local_frame = frame % self._duration_frames
        
        if local_frame <= self._attack_frames:
            return self._lerp_pulse_attack(local_frame)
        elif local_frame <= self._attack_frames + self._release_frames:
            return self._lerp_pulse_release(local_frame)
        else:
            return 0.0
    
    def render(self, requested: Extent):
        """Render envelope for the requested extent."""
        t0 = requested.start()
        t1 = requested.end()
        duration_samples = t1 - t0
        
        if self._mode == self.ADSR:
            # ADSR mode: finite envelope, pad with zeros outside extent
            overlap = requested.intersect(self.extent())
            if overlap.is_empty():
                # No overlap - return zeros
                return np.zeros((1, requested.duration()), dtype=np.float32)
            
            # Generate frame positions for overlap
            frames = np.arange(overlap.start(), overlap.end(), dtype=np.float32)
            overlap_buf = np.zeros(len(frames), dtype=np.float32)
            
            for i, frame in enumerate(frames):
                overlap_buf[i] = self._adsr_value_at(frame)
            
            # Pad with zeros to match requested duration
            dst_buf = np.zeros(requested.duration(), dtype=np.float32)
            offset = overlap.start() - requested.start()
            dst_buf[offset:offset + len(overlap_buf)] = overlap_buf
            
        else:  # PULSE mode
            # PULSE mode: infinite extent, loop the envelope pattern
            frames = np.arange(t0, t1, dtype=np.float32)
            dst_buf = np.zeros(duration_samples, dtype=np.float32)
            
            for i, frame in enumerate(frames):
                dst_buf[i] = self._pulse_value_at(frame)
        
        # Reshape to 2D array
        dst_buf.shape = (1, -1)
        return dst_buf
    
    def extent(self):
        """Return the extent of this generator."""
        if self._mode == self.ADSR:
            # ADSR has finite extent - exactly the duration specified
            return Extent(0, self._duration_frames)
        else:
            # PULSE mode has infinite extent and loops the pattern
            return Extent(0, Extent.PINF)
    
    def channel_count(self):
        return 1
    
    def frame_rate(self):
        return self._frame_rate