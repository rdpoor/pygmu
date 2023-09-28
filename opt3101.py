import serial
from serial.tools import list_ports

"""
Module to support interfacing to the TI OPT3101EVM evaluation module.

        +--------+--------+--------+--------+--------+--------+--------+--------+
    bit |       7|       6|       5|       4|       3|       2|       1|       0|
        +--------+--------+--------+--------+--------+--------+--------+--------+
data[0] |                              phase_lo                                 |
        +--------+--------+--------+--------+--------+--------+--------+--------+
data[1] |                              phase_hi                                 |
        +--------+--------+--------+--------+--------+--------+--------+--------+
data[2] |frameCt0| ambOvl |deAlFreq|framStat|   ledChannel    |illumDac|phaseOv1|
        +--------+--------+--------+--------+--------+--------+--------+--------+
data[3] |                               ampli_lo                                |
        +--------+--------+--------+--------+--------+--------+--------+--------+
data[4] |                               ampli_hi                                |
        +--------+--------+--------+--------+--------+--------+--------+--------+
data[5] |            dealiasBin             |phaseOv2| sigOvl |frameCt2|frameCt1|
        +--------+--------+--------+--------+--------+--------+--------+--------+
"""

class OPT3101(object):
    '''
    Find the control and data ports for the OPT3101EVM, return as a duple:

    >>> (p_control, p_data) = OPT3101.find_ports()
    >>> p_control.device
    'COM5'
    >>> p_data.device
    'COM6'
    '''

    VID=0x2047
    PID=0x0A3C

    @classmethod
    def find_ports(cls):
        """
        Return a duple with the first element as the control port and the second
        as the data port.
        """
        ports = []
        for port in serial.tools.list_ports.comports():
            if((port.vid==cls.VID) and (port.pid==cls.PID)):
                ports.append(port)
        if len(ports) != 2:
            raise RuntimeError('expected two opt3101 ports')
        pa = ports[0]
        pb = ports[1]
        if pa.hwid.endswith('x.2'):
            return (pb, pa)
        elif pa.hwid.endswith('x.2'):
            return (pa, pb)
        else:
            raise RuntimeError('expected one of the ports to be data port')

    @classmethod
    def start(cls, control_port, data_port):
        print(f'control port = {control_port.device}, data port = {data_port.device}', flush=True)
        with serial.Serial(control_port.device, 460800, timeout=1) as ctrl:
            ctrl.write(b'CAPS\r\n')
        with serial.Serial(data_port.device, 460800, timeout=1) as data:
            while True:
                pkt = data.read(10)
                # print(' '.join(f'{b:02X}' for b in pkt), flush=True)
                dist = (pkt[1]<<8) + pkt[0]
                print(f'{dist}', flush=True)


if __name__ == '__main__':
    OPT3101.start(*OPT3101.find_ports())
