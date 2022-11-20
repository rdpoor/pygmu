import numpy as np
from extent import Extent
from pyg_pe import PygPE

class Env2PE(PygPE):
    """
    Ramp up, play src, ramp down.
    """

    def __init__(self, src_pe, up_dur=0, dn_dur=0):
        super(Env2PE, self).__init__()
        self._src_pe = src_pe
        self._up_dur = up_dur
        self._dn_dur = dn_dur
        print(self.extent())


    def render(self, requested:Extent):
        overlap = requested.intersect(self.extent())
        offset = int(requested.start())
        tu0 = self.extent().start()
        tu1 = self.extent().start() + self._up_dur
        td0 = self.extent().end() - self._dn_dur
        td1 = self.extent().end()

        # optimize common cases
        if overlap.precedes(self.extent()) or overlap.follows(self.extent()):
            # src_pe hasn't started or has already ended
            dst_buf = np.zeros([requested.duration(), self.channel_count()], dtype=np.float32)

        elif Extent(tu1, td0).spans(overlap):
            # src is fully on (g=1.0) for the entire request.  dst_buf = src
            dst_buf = self._src_pe.render(requested)

        else:
            """
    To understand the variables:

    If the ramp up completes before the ramp down starts, it looks like this.
    Note that max_g is greater than 1.0:

max_g:               +
                    / \
                   /   \
                  /     \
                 /       \
                /         \
               /           \
g=1.0         +-------------+
             /|             | \
            / |             |   \
g=0.0 --- +   |             |    +---
          |   |      |      |    |
         tu0 tu1     t     td0  td1
           up                down


    If the ramp up overlaps with the ramp down, it looks like this.  Note that
    max_g < 1.0:

max_g        +
            / \
           /   \
g=0.0  ---+     +---
          |  |  |
         tu0 t td1
            """

            # Now it gets fun.
            if (tu0 == tu1) or (td0 == td1):
                # instant ramp up or ramp down -- no chance for ramps to overlap
                max_g = 1.0

            else:
                # Compute the time t where the up ramp intersects the down ramp.
                # If up(t) (or dn(t)) is less than 1.0, that means that the down
                # ramp started before the up ramp ended.  We'll need to account
                # for that.  Crunching a little algrebra to compute t (the time
                # at which the two ramps intersect) and max_g (tha value of the
                # ramps at time t).
                mu = 1 / (tu1 - tu0)   # slope of up ramp
                md = -1 / (td1 - td0)  # slope of down ramp
                t = (mu + mu * td0 + md * tu0) / (mu + md)
                max_g = lerp(t, tu0, tu1, 0.0, 1.0)

                if max_g > 1.0:
                    # up ramp and down ramp do not overlap.  simple case with
                    # some amount of unity gain between the two ramps.
                    max_g = 1.0   # clamp gain to 1.0 (we'll use g below)
                else:
                    # up ramp and down ramp collide at t (with value = g), so
                    # there won't be any unity gain between the two ramps
                    tu1 = int(t)
                    td0 = int(t)

            r0 = requested.start()
            r1 = requested.end()

            # Generate the source frames we'll use and progressively replace
            # frames in dst_buf in five easy steps (see "Game Plan")
            src_buf = self._src_pe.render(overlap)
            src_index = 0
            dst_buf = gen_uninitialized_frames(requested.duration(), self.channel_count())
            dst_index = 0

            # Game Plan
            #
            # r0 ... r1 defines the extent of the request.  Note that any of the
            # following segments may have zero length:
            #
            # 1. generate 0.0 from r0 to tu0
            # 2. ramp up from tu0 to tu1 with values (0.0 ... max_g)
            # 3. steady state from tu1 to td0
            # 4. ramp down from td0 to td1 with value (max_g ... 0.0)
            # 5. generate 0.0 from td1 to r1

            # 1. generate 0.0 from r0 to tu0
            s = r0
            e = min(r1, tu0)
            n = max(0, e - s)
            if n > 0:
                dst_buf[dst_index:dst_index+n,:] = gen_const_frames(0.0, n, self.channel_count())
                dst_index += n

            # 2. ramp up from tu0 to tu1 with values (0.0 ... max_g)
            s = max(r0, tu0)
            e = min(r1, tu1)
            n = max(0, e - s)
            if n > 0:
                g0 = lerp(s, tu0, tu1, 0, max_g)
                g1 = lerp(e, tu0, tu1, 0, max_g)
                print(dst_index, s, e, n, r1, tu1)
                dst_buf[dst_index:dst_index+n,:] = src_buf[0:n,:] * gen_ramp_frames(g0, g1, n, self.channel_count())
                src_index += n
                dst_index += n

            # 3. steady state from tu1 to td0
            s = max(r0, tu1)
            e = min(r1, td0)
            n = max(0, e - s)
            if n > 0:
                dst_buf[dst_index:dst_index+n,:] = src_buf[src_index:src_index+n]
                src_index += n
                dst_index += n

            # 4. ramp down from td0 to td1 with value (max_g ... 0.0)
            s = max(r0, td0)
            e = min(r1, td1)
            n = max(0, e - s)
            if n > 0:
                g0 = lerp(s, td0, td1, max_g, 0)
                g1 = lerp(e, td0, td1, max_g, 0)
                dst_buf[dst_index:dst_index+n,:] = src_buf[0:n,:] * gen_ramp_frames(g0, g1, n, self.channel_count())
                src_index += n
                dst_index += n

            # 5. generate 0.0 from td1 to r1
            s = max(r0, td1)
            e = r1
            n = max(0, e - s)
            if n > 0:
                dst_buf[dst_index:dst_index+n,:] = gen_const_frames(0.0, n, self.channel_count())
                dst_index += n

            assert(dst_index == requested.duration())

        return dst_buf

    def extent(self):
        return self._src_pe.extent()

    def frame_rate(self):
        return self._src_pe.frame_rate()

    def channel_count(self):
        return self._src_pe.channel_count()

# ******************************************************************************
# candidates for a utility module
# TODO: use from utils module

def lerp(x, x0, x1, y0, y1):
    return y0 + (x - x0) * (y1 - y0) / (x1 - x0)

def clamp(xlo, x, xhi):
    if x < xlo:
        return xlo
    elif x > xhi:
        return xhi
    else:
        return x

def gen_uninitialized_frames(n_frames, n_channels):
    """
    Create an uninitialized array of frames.
    """
    return np.ndarray([n_frames, n_channels], dtype=np.float32) # emtpy

def gen_const_frames(value, n_frames, n_channels):
    """
    Create an array of frames containing a constant value.
    """
    return np.full([n_frames, n_channels], value, dtype=np.float32)

def gen_ramp_frames(v0, v1, n_frames, n_channels):
    """
    Create an array of frames containing values ramping from v0 (inclusive) to
    v1 (exclusive).
    """
    ramp = np.linspace(v0, v1, num=n_frames, endpoint=False, dtype=np.float32)
    return np.tile(ramp.reshape(-1, 1), (1, n_channels))
