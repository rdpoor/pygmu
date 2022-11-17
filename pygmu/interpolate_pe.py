import numpy as np
from extent import Extent
from pyg_pe import PygPE

def monofy(frames):
    # Convert stero frames (2 column, N rows) into mono (one row)
    return np.dot(frames, [[0.5], [0.5]]).reshape(-1)

def sterofy(frames):
    # convert horizontal mono array into stero frames (2 columns, N rows)
    return np.dot(frames.reshape(-1, 1), [[1.0, 1.0]])

class InterpolatePE(PygPE):
    """
    crudely resample
    """

    def __init__(self, src_pe:PygPE, speed_mult):
        super(InterpolatePE, self).__init__()
        self._src_pe = src_pe
        self._speed_mult = speed_mult

    def render(self, requested:Extent, n_channels:int):

        intersection = requested.intersect(self.extent())
        if intersection.is_empty():
            # no intersection
            return np.zeros([requested.duration(), n_channels], np.float32)
        elif intersection.equals(requested):
            # full overlap: just grab the corresponding samples and reverse them
            src_extent = Extent(start=int(intersection.start() * self._speed_mult), end=int(intersection.end() * self._speed_mult))
            src_dur = np.round(src_extent.duration()).astype(int)
            src_x = np.linspace(0, src_dur, src_dur)
            src_buf = monofy(self._src_pe.render(src_extent, 1))
            dst_dur = np.round(intersection.duration()).astype(int)
            dst_x = np.linspace(0, dst_dur, dst_dur)
            return sterofy(np.interp(dst_x, src_x, src_buf))
        else:
            # Create dst_buf equal to the length of the request.
            # src frames will come from an extent mirrored around the center of the src extent
            # to produce frames that fall within the intersection, then lay
            # the frames into the dst_buf at the required offset

            dst_buf = np.zeros([requested.duration()], np.float32)
            print(dst_buf)
            src_extent = Extent(start=int(intersection.start() * self._speed_mult), end=int(intersection.end() * self._speed_mult))
            src_dur = np.round(src_extent.duration()).astype(int)
            src_x = np.linspace(0, src_dur, src_dur)
            src_buf = monofy(self._src_pe.render(src_extent, 1))
            dst_dur = np.round(intersection.duration()).astype(int)
            dst_x = np.linspace(0, dst_dur, dst_dur)
            dst_buf = np.interp(dst_x, src_x, src_buf)
            offset = intersection.start() - requested.start()
            dst_buf[offset:int(offset + intersection.duration())] = src_buf
            return sterofy(dst_buf)

    def extent(self):
        return Extent(start=self._src_pe.extent().start(), end=self._src_pe.extent().start() + (self._speed_mult * self._src_pe.extent().duration()))
