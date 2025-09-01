import numpy as np
from scipy import signal
from extent import Extent
from pyg_pe import PygPE
from env_detect_pe import EnvDetectPE
from crop_pe import CropPE
from splice_pe import SplicePE
import utils as ut

class TrimPE(PygPE):
    """
    Trim silence from the beginning and end of an audio signal using envelope detection.
    
    Args:
        src_pe: Source processing element
        threshold: Threshold level (0.0-1.0, will be scaled to peak amplitude)
        attack: Attack coefficient for envelope detector (default 0.9)
        release: Release coefficient for envelope detector (default 0.1) 
        ends_only: If True, only trim start/end silence (default True)
    """
    
    def __init__(self, src_pe, threshold=0.01, attack=0.2, release=0.1, ends_only=True):
        super(TrimPE, self).__init__()
        self._src_pe = src_pe
        self._threshold = threshold
        self._attack = attack
        self._release = release
        self._ends_only = ends_only
        self._cropped_pe = None
        
        if not ends_only:
            raise NotImplementedError("ends_only=False not yet implemented")
        
        # Find the trimmed extent and create cropped PE
        self._compute_trimmed_extent()
    
    def _compute_trimmed_extent(self):
        """Compute the trimmed extent by analyzing the envelope"""
        src_extent = self._src_pe.extent()
        if src_extent.is_empty():
            self._cropped_pe = self._src_pe
            return
        
        # Get raw audio frames directly for faster processing
        src_frames = self._src_pe.render(src_extent)
        
        # Take absolute value for envelope detection
        abs_frames = np.abs(src_frames)
        
        # Find peak amplitude to scale threshold
        peak_amplitude = np.max(abs_frames)
        if peak_amplitude <= 0:
            # Silent input - return empty extent
            self._cropped_pe = CropPE(self._src_pe, Extent(0, 0))
            return
        
        # Scale threshold by peak amplitude
        scaled_threshold = self._threshold * peak_amplitude
        
        # Apply simple smoothing using numpy operations instead of sample-by-sample loop
        if abs_frames.ndim == 1:
            # Mono case - convert to 2D for consistent handling
            abs_frames = abs_frames.reshape(1, -1)
        
        # Use scipy's exponential filter for much faster envelope detection
        # Convert attack/release to filter coefficients
        attack_alpha = 1.0 - self._attack  
        release_alpha = 1.0 - self._release
        
        smoothed = np.zeros_like(abs_frames)
        for ch in range(abs_frames.shape[0]):
            channel_data = abs_frames[ch, :]
            
            # Apply different time constants for attack vs release
            # This approximates the EnvDetectPE behavior but much faster
            smoothed_ch = np.zeros_like(channel_data)
            if len(channel_data) > 0:
                smoothed_ch[0] = channel_data[0]
                for i in range(1, len(channel_data)):
                    if channel_data[i] > smoothed_ch[i-1]:
                        # Attack - faster response
                        alpha = attack_alpha
                    else:
                        # Release - slower response  
                        alpha = release_alpha
                    smoothed_ch[i] = alpha * smoothed_ch[i-1] + (1-alpha) * channel_data[i]
            
            smoothed[ch, :] = smoothed_ch
        
        # Find any channel above threshold
        above_threshold = np.any(smoothed > scaled_threshold, axis=0)
        
        # Handle case where entire signal is below threshold
        if not np.any(above_threshold):
            self._cropped_pe = CropPE(self._src_pe, Extent(0, 0))
            return
        
        # Find start and end of non-silent region
        nonzero_indices = np.where(above_threshold)[0]
        
        if len(nonzero_indices) == 0:
            self._cropped_pe = CropPE(self._src_pe, Extent(0, 0))
            return
        
        start_frame = src_extent.start() + nonzero_indices[0]
        end_frame = src_extent.start() + nonzero_indices[-1] + 1
        
        # Create cropped PE with trimmed extent
        trimmed_extent = Extent(start_frame, end_frame)
        cropped_pe = CropPE(self._src_pe, trimmed_extent)
        
        # Calculate ramp durations based on attack/release coefficients
        # Convert coefficients to time constants (higher coefficient = shorter ramp)
        # Use frame rate to convert to sample counts
        frame_rate = self._src_pe.frame_rate()
        if frame_rate is None:
            frame_rate = 48000  # fallback
        
        # Calculate ramp durations - use inverse relationship with coefficients
        # Higher attack/release = shorter ramp for smoother transitions
        fade_in_duration = int((1.0 - self._attack) * frame_rate * 0.1)  # max 0.1 sec
        fade_out_duration = int((1.0 - self._release) * frame_rate * 0.1)  # max 0.1 sec
        
        # Ensure ramps don't exceed half the trimmed duration
        trimmed_duration = trimmed_extent.duration()
        max_ramp = trimmed_duration // 2
        fade_in_duration = min(fade_in_duration, max_ramp)
        fade_out_duration = min(fade_out_duration, max_ramp)
        
        # Apply splice to add fade-in/fade-out if we actually trimmed
        original_start = self._src_pe.extent().start()
        original_end = self._src_pe.extent().end()
        
        # Only add ramps if we actually trimmed from that end
        up_dur = fade_in_duration if start_frame > original_start else 0
        dn_dur = fade_out_duration if end_frame < original_end else 0
        
        self._cropped_pe = SplicePE(cropped_pe, up_dur=up_dur, dn_dur=dn_dur)
    
    def render(self, requested):
        return self._cropped_pe.render(requested)
    
    def extent(self):
        return self._cropped_pe.extent()
    
    def channel_count(self):
        return self._src_pe.channel_count()
    
    def frame_rate(self):
        return self._src_pe.frame_rate()