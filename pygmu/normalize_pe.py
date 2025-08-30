import numpy as np
from extent import Extent
from pyg_pe import PygPE
import utils as ut
from gain_pe import GainPE

class NormalizePE(PygPE):
    """
    Normalizes audio to a target peak level by analyzing the entire source.
    
    This PE first renders the entire source to find the peak amplitude,
    then applies gain to reach the target level. Only works with fixed-length
    sources that have a definite extent.
    """
    
    def __init__(self, src_pe, target_db=-3.0, headroom_db=0.1):
        """
        Initialize the normalize PE.
        
        Args:
            src_pe: Source processing element (must have finite extent)
            target_db: Target peak level in dB (default -3dB for safety)
            headroom_db: Additional headroom to prevent clipping (default 0.1dB)
        """
        self._src_pe = src_pe
        self._target_db = target_db
        self._headroom_db = headroom_db
        self._target_linear = ut.db_to_ratio(target_db - headroom_db)
        
        # Check that source has finite extent
        if self._src_pe.extent().is_indefinite():
            raise ValueError("NormalizePE requires a source with finite extent")
        
        # Cached values
        self._gain_pe = None
        self._analyzed = False
        
    def _analyze_peak(self):
        """Analyze the source to find peak amplitude and calculate normalization gain."""
        if self._analyzed:
            return
            
        # Render entire source to find peak
        src_extent = self._src_pe.extent()
        src_frames = self._src_pe.render(src_extent)
        
        # Find peak amplitude across all channels
        peak_amplitude = np.max(np.abs(src_frames))
        
        if peak_amplitude == 0.0:
            # Silent source - no normalization needed
            gain_ratio = 1.0
        else:
            # Calculate gain needed to reach target level
            gain_ratio = self._target_linear / peak_amplitude
            
        # Create gain PE with calculated gain
        self._gain_pe = GainPE(self._src_pe, gain_ratio)
        self._analyzed = True
        
    def render(self, requested: Extent):
        # Ensure analysis is done
        self._analyze_peak()
        
        # Delegate to gain PE
        return self._gain_pe.render(requested)
        
    def extent(self):
        return self._src_pe.extent()
        
    def frame_rate(self):
        return self._src_pe.frame_rate()
        
    def channel_count(self):
        return self._src_pe.channel_count()