import numpy as np

def lerp(x, x0, x1, y0, y1):
    """
    Linear interpolation (aka two point line function): as x goes from x0 to x1,
    lerp(x) goes from y0 to y1.
    """
    return y0 + (x - x0) * (y1 - y0) / (x1 - x0)

def clamp(xlo, x, xhi):
    """
    Limit x such that xlo <= x <= xhi
    """
    if x < xlo:
        return xlo
    elif x > xhi:
        return xhi
    else:
        return x

def uninitialized_frames(n_frames, n_channels):
    """
    Create an uninitialized array of frames.
    """
    return np.ndarray([n_frames, n_channels], dtype=np.float32) # empty

def const_frames(value, n_frames, n_channels):
    """
    Create an array of frames containing a constant value.
    """
    return np.full([n_frames, n_channels], value, dtype=np.float32)

def ramp_frames(v0, v1, n_frames, n_channels):
    """
    Create an array of frames containing values ramping from v0 (inclusive) to
    v1 (exclusive).
    """
    ramp = np.linspace(v0, v1, num=n_frames, endpoint=False, dtype=np.float32)
    return ramp.repeat(n_channels).reshape(-1, n_channels)

def complex_to_magphase(c):
    """
    Convert a complex into magnitude and phase components, returned as a duple.
    """
    return np.abs(c), np.angle(c)

def magphase_to_complex(mag, phase):
    """
    Convert magnitude and phase into a complex.
    """
    return mag * np.exp(1j*phase)
