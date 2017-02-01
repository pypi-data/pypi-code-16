# Copyright (c) 2016, Science and Technology Facilities Council
# This software is distributed under a BSD licence. See LICENSE.txt.
"""
mrcfile
-------

Module which exports the :class:`MrcFile` class.

Classes:
    :class:`MrcFile`: An object which represents an MRC file.

"""

# Import Python 3 features for future-proofing
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)


import os
import warnings

from .mrcinterpreter import MrcInterpreter


class MrcFile(MrcInterpreter):
    
    """An object which represents an MRC file.
    
    The header and data are handled as numpy arrays - see
    :class:`~mrcfile.mrcobject.MrcObject` for details.
    
    Usage:
        To create a new MrcFile object, pass a file name and optional mode. To
        ensure the file is written to disk and closed correctly, it's best to
        use the 'with' statement:
        
        >>> with MrcFile('tmp.mrc', 'w+') as mrc:
        >>>     mrc.set_data(np.zeros((10, 10), dtype=np.int8))
        
        In mode 'r' or 'r+', the named file is opened from disk and read. In
        mode 'w+' a new empty file is created and will be written to disk at the
        end of the 'with' block (or when flush() or close() is called).
    
    """
    
    def __init__(self, name, mode='r', overwrite=False, **kwargs):
        """Initialise a new :class:`MrcFile` object.
        
        The given file name is opened in the given mode. For mode 'r' or 'r+'
        the header, extended header and data are read from the file. For mode
        'w+' a new file is created with a default header and empty extended
        header and data arrays.
        
        Args:
            name: The file name to open.
            mode: The file mode to use. This should be one of the following:
                'r' for read-only, 'r+' for read and write, or 'w+' for a new
                empty file. The default is 'r'.
            overwrite: Flag to force overwriting of an existing file if the mode
                is 'w+'. If False and a file of the same name already exists,
                the file is not overwritten and an exception is raised. The
                default is False.
        
        Raises:
            ValueError: If the mode is not one of 'r', 'r+' or 'w+', the file is
                not a valid MRC file, or if the mode is 'w+', the file already
                exists and overwrite is False.
            OSError: If the mode is 'r' or 'r+' and the file does not exist.
        
        Warns:
            RuntimeWarning: The file appears to be a valid MRC file but the data
                block is longer than expected from the dimensions in the header.
        """
        super(MrcFile, self).__init__(**kwargs)
        
        if mode not in ['r', 'r+', 'w+']:
            raise ValueError("Mode '{0}' not supported".format(mode))
        
        if ('w' in mode and os.path.exists(name) and not overwrite):
            raise ValueError("File '{0}' already exists; set overwrite=True "
                          "to overwrite it".format(name))
        
        self._mode = mode
        self._read_only = (self._mode == 'r')
        
        self._open_file(name)
        
        try:
            if 'w' in mode:
                self._create_default_attributes()
            else:
                self._read()
        except Exception:
            self._close_file()
            raise
    
    def __repr__(self):
        return "MrcFile('{0}', mode='{1}')".format(self._iostream.name,
                                                   self._mode)
    
    def _open_file(self, name):
        """Open a file object to use as the I/O stream."""
        self._iostream = open(name, self._mode + 'b')
    
    def _read(self):
        """Override _read() to move back to start of file first."""
        self._iostream.seek(0)
        super(MrcFile, self)._read()
        
        # Check if the file is the expected size.
        actual_size = self._get_file_size()
        expected_size = (self.header.nbytes
                         + self.extended_header.nbytes
                         + self.data.nbytes)
        
        if actual_size > expected_size:
            msg = ("MRC file is {0} bytes larger than expected"
                   .format(actual_size - expected_size))
            warnings.warn(msg, RuntimeWarning)
    
    def _get_file_size(self):
        """Return the size of the underlying file object, in bytes."""
        pos = self._iostream.tell()
        self._iostream.seek(0, os.SEEK_END)
        size = self._iostream.tell()
        self._iostream.seek(pos, os.SEEK_SET)
        return size
    
    def close(self):
        """Flush any changes to disk and close the file.
        
        This override calls super() to ensure the stream is flushed and closed,
        then closes the file object.
        """
        super(MrcFile, self).close()
        self._close_file()
    
    def _close_file(self):
        """Close the file object."""
        self._iostream.close()
    
    def validate(self, print_file=None):
        """Validate this MRC file.
        
        The tests are:
        
        #. File size: The size of the file on disk should match the expected
           size calculated from the MRC header.
        #. Map and cell dimensions: The header fields ``nx``, ``ny``, ``nz``,
           ``mx``, ``my``, ``mz``, ``cella.x``, ``cella.y`` and ``cella.z`` must
           all be positive numbers.
        #. Axis mapping: Header fields ``mapc``, ``mapr`` and ``maps`` must
           contain the values 1, 2, and 3 (in any order).
        #. Volume stack dimensions: If the spacegroup is in the range 401--630,
           representing a volume stack, the ``nz`` field should be exactly
           divisible by ``mz`` to represent the number of volumes in the stack.
        #. Header labels: The ``nlabl`` field should be set to indicate the
           number of labels in use, and the labels in use should appear first in
           the label array.
        #. MRC format version: The ``nversion`` field should be 20140 for
           compliance with the MRC2014 standard.
        #. Extended header type: If an extended header is present, the
           ``exttyp`` field should be set to indicate the type of extended
           header.
        #. Data statistics: The statistics in the header should be correct for
           the actual data in the file, or marked as undetermined.
        
        Args:
            name: The file name to open and validate.
            print_file: The output text stream to use for printing messages 
                about the validation. This is passed directly to the ``file``
                argument of Python's ``print()`` function. The default is
                ``None``, which means output will be printed to ``sys.stdout``.
        
        Returns:
            True if the file is valid, False if the file does not meet the MRC
            format specification in any way.
        """
        valid = super(MrcFile, self).validate(print_file=print_file)
        
        # Check file size
        file_size = self._get_file_size()
        mrc_size = (self.header.nbytes
                    + self.extended_header.nbytes
                    + self.data.nbytes)
        if (file_size != mrc_size):
            print("File is larger than expected. Actual size: {0} bytes; "
                  "expected size: {1} bytes (calculated from header)"
                  .format(file_size, mrc_size),
                  file=print_file)
            valid = False
        
        return valid
