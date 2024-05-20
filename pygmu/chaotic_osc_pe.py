import numpy as np
from extent import Extent
from pyg_pe import PygPE
from pyg_gen import PygGen, FrequencyMixin

class ChaoticOscPE(PygGen, PygPE):
    def __init__(self, rho=28.0, sigma=10.0, beta=8.0/3.0, scale=0.1, x0=0.1, y0=0.0, z0=0.0, frame_rate=48000):
        super(ChaoticOscPE, self).__init__()
        self._frame_rate = frame_rate
        self.rho = rho
        self.sigma = sigma
        self.beta = beta
        self.scale = scale
        self.x = x0
        self.y = y0
        self.z = z0

    def render(self, requested: Extent):
        num_frames = requested.duration()
        samples = np.zeros(num_frames, dtype=np.float32)
        dt = 1.0 / self._frame_rate

        for i in range(num_frames):
            dx = self.sigma * (self.y - self.x) * dt
            dy = (self.x * (self.rho - self.z) - self.y) * dt
            dz = (self.x * self.y - self.beta * self.z) * dt

            self.x += dx
            self.y += dy
            self.z += dz

            samples[i] = self.x * self.scale

        return samples.reshape(1, -1)

    def extent(self):
        return Extent()

    def frame_rate(self):
        return self._frame_rate

    def channel_count(self):
        return 1
