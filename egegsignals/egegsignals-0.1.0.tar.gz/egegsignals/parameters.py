# egegsignals - Software for processing electrogastroenterography signals.

# Copyright (C) 2013 -- 2017 Aleksandr Popov, Aleksey Tyulpin, Anastasia Kuzmina

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import numpy as np
from scipy.fftpack import fft

egeg_fs = {
    'colon' : (0.01, 0.03),
    'stomach' : (0.03, 0.07),
    'ileum' : (0.07, 0,13),
    'nestis' : (0.13, 0.18),
    'duodenum' : (0.18, 0.25),
}

def dominant_frequency(x, dt, fs, spectrum=[]):
    """
    Return dominant frequency of signal in band of frequencies.

    Parameters
    ----------
    x : numpy.ndarray
        Signal
    dt : float 
        Sampling period
    fs : array_like
        Two frequencies bounds
    spectrum : array_like
        Pre-calculated spectrum.
    
    """
    if len(spectrum) == 0:
        spectrum = abs(fft(x))
        
    f = np.fft.fftfreq(len(x), dt)
    ind = (f>=fs[0]) & (f<=fs[1])
    df_ind = spectrum[ind].argmax()
    return f[ind][df_ind]
