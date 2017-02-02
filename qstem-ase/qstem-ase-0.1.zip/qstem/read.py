"""
QSTEM - image simulation for TEM/STEM/CBED
    Copyright (C) 2000-2010  Christoph Koch
    Copyright (C) 2010-2013  Christoph Koch, Michael Sarahan

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import numpy as np
import struct

headerlength = 4

def binread(filename, print_flag=False, full_output=False):
    """
    Read binary QSTEM image
    
    Args:
        filename: string
            name of file
        print_flag: bool
            0: non-verbose, 1: verbose (default)
    Returns:
        img: numpy array
            (complex) image
        t: float
            thickness of simulated unit cell
        dx, dy: float
            pixel size in Angstrom
    """
    
    comment=''
    # open the file and define the file ID (fid):
    f=open(filename,'rb')
    #with open(filename,'rb') as f:
    if True:
        # there are 8 ints followed by 3 doubles
        header = struct.unpack('iiiiiiiiddd',f.read(56))

        header_size = header[0]

        # read additional parameters from file, if any exist:
        param_size = header[1]

        comment_size = header[2]

        nx = header[3]
        ny = header[4]

        complex_flag = header[5]
        data_size = header[6]
        double_flag = (data_size==8*(complex_flag+1))
        complex_flag = bool(complex_flag)

        version = header[7]
        
        t=header[8]

        dx = header[9]
        dy = header[10]

        if (param_size > 0):
            params = np.fromfile(file=f, dtype=np.float64, count=param_size);
            if print_flag:
                print('{0} parameters:'.format(param_size))
                print(params)

        # read comments from file, if any exist:
        if (comment_size > 0):
            comment = struct.unpack('{0}s'.format(comment_size),f.read(comment_size))[0]

    if print_flag:
        print('binread {0}: {1} x {2} pixels'.format(filename,nx,ny))

    if complex_flag:
        if double_flag:
            if print_flag:
                print('64-bit complex data, {0} MB'.format(nx*ny*16/1048576))
            img = np.fromfile(file=f, dtype=np.complex128, count=nx*ny)
        else:
            if print_flag:
                print('32-bit complex data, {0} MB'.format(nx*ny*8/1048576))
            img = np.fromfile(file=f, dtype=np.complex64, count = nx*ny)
    else:
        if double_flag:
            if print_flag:
                print('64-bit real data, {0} MB'.format(nx*ny*8/1048576))
            img = np.fromfile(file=f, dtype=np.float64, count=nx*ny)
        else:
            if print_flag:
                print('32-bit real data, {0} MB'.format(nx*ny*4/1048576))
            img = np.fromfile(file=f, dtype=np.float32, count=nx*ny)
    img=img.reshape(nx,ny)
    
    if full_output:
        return img, comment, t, dx, dy
    else:
        return img, dx, dy
