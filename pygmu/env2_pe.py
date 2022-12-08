import numpy as np
from extent import Extent
from pyg_pe import PygPE
import utils as ut

class Env2PE(PygPE):
    """
    Ramp up, play src, ramp down.
    """

    def __init__(self, src_pe, up_dur=0, dn_dur=0):
        super(Env2PE, self).__init__()
        self._src_pe = src_pe
        self._up_dur = up_dur
        self._dn_dur = dn_dur
        # print(self.extent())


    def render(self, requested:Extent):
        overlap = requested.intersect(self.extent())
        offset = int(requested.start())

        tu0 = self.extent().start()                 # ramp up start time
        tu1 = self.extent().start() + self._up_dur  # ramp up end time
        td0 = self.extent().end() - self._dn_dur    # ramp down start time
        td1 = self.extent().end()                   # ramp down end time

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

    Case 1: If the ramp up completes before the ramp down starts, it looks like 
    this:

g=1.0         +-------------+
             /|             | \
            / |             |   \
g=0.0 --- +   |             |    +---
          |   |             |    |
         tu0 tu1           td0  td1
           up                down


    Case 2: If the ramp up overlaps with the ramp down, i.e. if td0 < tu1, it 
    looks like this.  We define t as the midpoint between tu1 and td0:

g<1.0        +
            / \
           /   \
g=0.0  ---+     +---
          |  |  |
         tu0 t td1

            """
            # Now it gets fun.
            # print("===== requested=", requested)
            gu0 = 0.0  # ramp up gain at t=tu0
            gu1 = 1.0  # ramp up gain at t=tu1
            gd0 = 1.0  # ramp down gain at t=td0
            gd1 = 0.0  # ramp down gain at t=td1

            if td0 < tu1:
                # Case 2: Ramp down starts before ramp up completes.  Adjust
                # ramp endpoints [tu1, gu1] and [td0, gd0].  Start by finding
                # the time t at which the ramps intersect.
                t = (-tu1 * td1 + tu0 * td0) / (-td1 + td0 - tu1 + td0)
                t_ = int(np.ceil(t))   # end time for up ramp, start for down
                gu1 = ut.lerp(t_, tu0, tu1, gu0, gu1) # ramp up end value
                tu1 = t_                              # ramp up end time
                gd0 = ut.lerp(t, td0, td1, gd0, gd1)  # ramp down start value
                td0 = t_                              # ramp down start time
                # print("Case 2: t={}, [{}, {}], [{}, {}], [{}, {}], [{}, {}]".format(t, tu0, gu0, tu1, gu1, td0, gd0, td1, gd1))

            # At this point, the ramp up is defined by the points:
            # [tu0, gu0], [tu1, gu1] and the ramp down is defined by the points:
            # [td0, gd0], [td1, gd1]

            # Render the source frames and allocate an uninitialized dst buffer
            # into which we'll progressively write frames in five easy steps 
            # (see "Game Plan" below)
            src_buf = self._src_pe.render(overlap)
            dst_buf = ut.uninitialized_frames(requested.duration(), self.channel_count())

            src_index = 0
            dst_index = 0

            r0 = requested.start()
            r1 = requested.end()

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
                # print("Step 1: s=", s, "e=", e, "n=", n)
                dst_buf[dst_index:dst_index+n,:] = ut.const_frames(0.0, n, self.channel_count())
                dst_index += n

            # 2. ramp up from tu0 to tu1 with values (gu0 ... gu1)
            s = max(r0, tu0)
            e = min(r1, tu1)
            n = max(0, e - s)
            if n > 0:
                g0 = ut.lerp(s, tu0, tu1, gu0, gu1)
                g1 = ut.lerp(e, tu0, tu1, gu0, gu1)
                ramp = ut.ramp_frames(g0, g1, n, self.channel_count())
                # print("Step 2: s=", s, "e=", e, "n=", n)
                # print("Step 2: ramp=", ramp)
                dst_buf[dst_index:dst_index+n,:] = src_buf[0:n,:] * ramp
                src_index += n
                dst_index += n

            # 3. steady state from tu1 to td0
            s = max(r0, tu1)
            e = min(r1, td0)
            n = max(0, e - s)
            if n > 0:
                # print("Step 3: s=", s, "e=", e, "n=", n)
                dst_buf[dst_index:dst_index+n,:] = src_buf[src_index:src_index+n]
                src_index += n
                dst_index += n

            # 4. ramp down from td0 to td1 with values (gd0 ... gd1)
            s = max(r0, td0)
            e = min(r1, td1)
            n = max(0, e - s)
            if n > 0:
                g0 = ut.lerp(s, td0, td1, gd0, gd1)
                g1 = ut.lerp(e, td0, td1, gd0, gd1)
                ramp = ut.ramp_frames(g0, g1, n, self.channel_count())
                # print("Step 4: s=", s, "e=", e, "n=", n)
                # print("Step 4: ramp=", ramp)
                dst_buf[dst_index:dst_index+n,:] = src_buf[src_index:src_index+n,:] * ramp
                src_index += n
                dst_index += n

            # 5. generate 0.0 from td1 to r1
            s = max(r0, td1)
            e = r1
            n = max(0, e - s)
            if n > 0:
                # print("Step 5: s=", s, "e=", e, "n=", n)
                dst_buf[dst_index:dst_index+n,:] = ut.const_frames(0.0, n, self.channel_count())
                dst_index += n

            assert(dst_index == requested.duration())

        return dst_buf

    def extent(self):
        return self._src_pe.extent()

    def frame_rate(self):
        return self._src_pe.frame_rate()

    def channel_count(self):
        return self._src_pe.channel_count()
