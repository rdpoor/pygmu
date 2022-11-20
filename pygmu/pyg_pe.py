import numpy as np
from extent import Extent

class PygPE(object):
    """
    PygPE is the abstract base class for all Processing Elements.
    """

    DEFAULT_FRAME_RATE = 48000
    DEFAULT_CHANNEL_COUNT = 2

    def render(self, requested:Extent) -> (np.ndarray, int):
        """
        Instructs this Processing ELement to return an np.ndarray of sample data
        that falls within the requested Extent, and an offset that aligns the
        resulting data with the request.  May return

        Rules of render:

        [1] The caller may not modify the data returned by render(): it is owned
        by the callee.

        [2] The caller MAY request frames outside of the callee's extent.  The
        callee will normally return 0's for such frames.
        """
        return None

    def extent(self) -> Extent:
        """
        Return the time span of this processing element.  Unless overridden,
        subclasses of PygPE will return the indefinite extent.
        """
        return Extent()

    def frame_rate(self):
        """
        Return the frame rate of this PE.  If the PE has an input, it will 
        typically override this method and return the frame rate of its 
        input, but it's free to override this method as needed.
        """        
        return PygPE.DEFAULT_FRAME_RATE

    def channel_count(self):
        """
        Return the number of channels produced by this PE.  If the PE has an 
        input, it will typically override this method and return the channel
        count of its input, but it's free to override this method as needed.
        """        
        return PygPE.DEFAULT_CHANNEL_COUNT
