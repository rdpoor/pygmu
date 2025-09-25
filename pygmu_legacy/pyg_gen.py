import numpy as np
from pyg_pe import PygPE
from extent import Extent

class PygGen(PygPE):
    """
    PygGen is the abstract base class for all Generator Processing Elements.
    """

    def __init__(self, frame_rate=None):
        super(PygGen, self).__init__()
        self._frame_rate = frame_rate

    def frame_rate(self):
        """
        Return the frame rate of this PE.
        """        
        return self._frame_rate


class DynamicParameterMixin:
    def set_dynamic_parameter(self, name, value):
        if isinstance(value, PygGen):
            if value.channel_count() != 1:
                raise pyx.ChannelCountMismatch(f"Dynamic {name} source must be single channel")
            setattr(self, f"_dynamic_{name}", value)
            setattr(self, f"_static_{name}", None)
        else:
            setattr(self, f"_dynamic_{name}", None)
            setattr(self, f"_static_{name}", value)

    def get_dynamic_parameter(self, name, requested=None):
        dynamic_value = getattr(self, f"_dynamic_{name}", None)
        if dynamic_value is not None:
            return dynamic_value.render(requested).reshape(-1)  # convert to 1D array
        return getattr(self, f"_static_{name}", None)
