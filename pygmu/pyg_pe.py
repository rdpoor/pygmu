import numpy as np
from extent import Extent

class PygPE(object):
    """
    PygPE is the abstract base class for all Processing Elements.
    """

    def render(self, requested: Extent) -> np.ndarray:
        """
        Instructs this Processing ELement to return a Buffer of sample data
        with the given extent.  May return None if there is no overlap.

        Rules of render:

        [1] The caller may not modify the data returned by render(): it is owned
        by the callee.

        [2] The caller may not request frames outside of the callee's extent,
        i.e. callee.extent().spans(requested) must be true.

        [3] The `requested` argument may be a finite extent or None.  If it is
        None, the callee doesn't need to produce any data.
        """
        return None

    def channel_count(self) -> int:
        """
        Return the number of channels for this processing element's output.
        This will usually be overridden.
        """
        return 1

    def extent(self) -> Extent:
        """
        Return the time span of this processing element.
        This will usually be overridden.
        """
        return Extent()
