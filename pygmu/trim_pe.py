import numpy as np
from extent import Extent
from pyg_pe import PygPE
from env_detect_pe import EnvDetectPE
from crop_pe import CropPE
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
    
    def __init__(self, src_pe, threshold=0.01, attack=0.9, release=0.1, ends_only=True):
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
        
        # Get envelope using EnvDetectPE
        env_pe = EnvDetectPE(self._src_pe, attack=self._attack, release=self._release)
        env_frames = env_pe.render(src_extent)
        
        # Find peak amplitude to scale threshold
        peak_amplitude = np.max(env_frames)
        if peak_amplitude <= 0:
            # Silent input - return empty extent
            self._cropped_pe = CropPE(self._src_pe, Extent(0, 0))
            return
        
        # Scale threshold by peak amplitude
        scaled_threshold = self._threshold * peak_amplitude
        
        # Find first and last samples above threshold
        above_threshold = env_frames > scaled_threshold
        
        # Handle case where entire signal is below threshold
        if not np.any(above_threshold):
            self._cropped_pe = CropPE(self._src_pe, Extent(0, 0))
            return
        
        # Find start and end of non-silent region
        if env_frames.ndim == 1:
            # Mono case
            nonzero_indices = np.where(above_threshold)[0]
        else:
            # Multi-channel case - find any channel above threshold
            any_channel_above = np.any(above_threshold, axis=0)
            nonzero_indices = np.where(any_channel_above)[0]
        
        if len(nonzero_indices) == 0:
            self._cropped_pe = CropPE(self._src_pe, Extent(0, 0))
            return
        
        start_frame = src_extent.start() + nonzero_indices[0]
        end_frame = src_extent.start() + nonzero_indices[-1] + 1
        
        # Create cropped PE with trimmed extent
        trimmed_extent = Extent(start_frame, end_frame)
        self._cropped_pe = CropPE(self._src_pe, trimmed_extent)
    
    def render(self, requested):
        return self._cropped_pe.render(requested)
    
    def extent(self):
        return self._cropped_pe.extent()
    
    def channel_count(self):
        return self._src_pe.channel_count()
    
    def frame_rate(self):
        return self._src_pe.frame_rate()