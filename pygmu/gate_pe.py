import numpy as np
from extent import Extent
from pyg_pe import PygPE
import utils as ut

class GatePE(PygPE):
    """
    Audio gate that attenuates signals below a threshold with smooth attack and release.

    A traditional audio gate:
    - Opens smoothly when signal level exceeds threshold (attack time)
    - Closes smoothly when signal level falls below threshold (release time)
    - Uses envelope detection to track signal level over time
    """

    def __init__(self, src_pe, threshold_db=-20, attack=0.01, release=0.1):
        """
        Initialize the gate.

        Args:
            src_pe: Source processing element
            threshold_db: Threshold in dB below which gate closes
            attack: Attack time in seconds (how quickly gate opens)
            release: Release time in seconds (how quickly gate closes)
        """
        self._src_pe = src_pe
        self._threshold_db = threshold_db
        self._threshold_linear = ut.db_to_ratio(threshold_db)
        self._attack = attack
        self._release = release
        
        # Initialize state for envelope tracking
        self._envelope_state = 0.0
        self._gate_state = 0.0
        self._coefficients_calculated = False

    def render(self, requested: Extent):
        overlap = self._src_pe.extent().intersect(requested)
        if overlap.is_empty():
            return ut.const_frames(0.0, self.channel_count(), requested.duration())

        # Calculate coefficients on first render (when frame rate is available)
        if not self._coefficients_calculated:
            frame_rate = self.frame_rate()
            if frame_rate is None:
                frame_rate = 48000  # Default frame rate
            self._attack_coeff = 1.0 - np.exp(-1.0 / (self._attack * frame_rate))
            self._release_coeff = 1.0 - np.exp(-1.0 / (self._release * frame_rate))
            self._coefficients_calculated = True

        # Get source audio
        src_frames = self._src_pe.render(requested)
        
        # Calculate instantaneous envelope (maximum across channels for each sample)
        if src_frames.ndim == 1:
            # Handle 1D mono case
            instant_envelope = np.abs(src_frames)
        else:
            # Multi-channel: use maximum across channels
            instant_envelope = np.max(np.abs(src_frames), axis=0)
        
        # Apply envelope smoothing and gate control sample by sample
        gate_control = np.zeros_like(instant_envelope)
        
        for i in range(len(instant_envelope)):
            current_level = instant_envelope[i]
            
            # Update envelope with attack/release smoothing
            if current_level > self._envelope_state:
                # Attack: follow signal up quickly
                self._envelope_state += (current_level - self._envelope_state) * self._attack_coeff
            else:
                # Release: follow signal down slowly
                self._envelope_state += (current_level - self._envelope_state) * self._release_coeff
            
            # Determine gate state based on smoothed envelope
            if self._envelope_state > self._threshold_linear:
                # Above threshold: open gate
                target_gate = 1.0
            else:
                # Below threshold: close gate
                target_gate = 0.0
            
            # Smooth gate control to avoid clicks
            if target_gate > self._gate_state:
                # Opening gate
                self._gate_state += (target_gate - self._gate_state) * self._attack_coeff
            else:
                # Closing gate
                self._gate_state += (target_gate - self._gate_state) * self._release_coeff
            
            gate_control[i] = self._gate_state
        
        # Apply gate control to source audio
        if src_frames.ndim == 1:
            # Mono case
            return src_frames * gate_control
        else:
            # Multi-channel: broadcast gate control to all channels
            return src_frames * gate_control[np.newaxis, :]

    def extent(self):
        return self._src_pe.extent()

    def frame_rate(self):
        return self._src_pe.frame_rate()

    def channel_count(self):
        return self._src_pe.channel_count()

    # is there a way to migrate these to a different file?
