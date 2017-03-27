#!/usr/bin/env python
# encoding: utf-8

# The MIT License (MIT)

# Copyright (c) 2017 CNRS

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# AUTHORS
# Hervé BREDIN - http://herve.niderb.fr


from ._version import get_versions
__version__ = get_versions()['version']
del get_versions


from pyannote.database import Database
from pyannote.database.protocol import SpeakerDiarizationProtocol
from pyannote.parser import UEMParser, MDTMParser
import os.path as op


class EsterSpeakerDiarizationProtocol(SpeakerDiarizationProtocol):
    """Base speaker diarization protocol for ESTER database"""

    def __init__(self, preprocessors={}, **kwargs):
        super(EsterSpeakerDiarizationProtocol, self).__init__(
            preprocessors=preprocessors, **kwargs)
        self.uem_parser_ = UEMParser()
        self.mdtm_parser_ = MDTMParser()

    def _subset(self, protocol, subset):

        data_dir = op.join(op.dirname(op.realpath(__file__)), 'data')

        # load annotated parts
        # e.g. /data/{tv|radio|all}.{train|dev|test}.uem
        path = op.join(data_dir, '{protocol}.{subset}.uem'.format(subset=subset, protocol=protocol))
        uems = self.uem_parser_.read(path)

        # load annotations
        path = op.join(data_dir, '{protocol}.{subset}.mdtm'.format(subset=subset, protocol=protocol))
        mdtms = self.mdtm_parser_.read(path)

        for uri in sorted(uems.uris):
            annotated = uems(uri)
            annotation = mdtms(uri)
            current_file = {
                'database': 'Ester',
                'uri': uri,
                'annotated': annotated,
                'annotation': annotation}
            yield current_file


class Ester1(EsterSpeakerDiarizationProtocol):
    """Speaker diarization protocol using Ester1 subset of ESTER database"""

    def trn_iter(self):
        return self._subset('ester1', 'trn')

    def dev_iter(self):
        return self._subset('ester1', 'dev')

    def tst_iter(self):
        return self._subset('ester1', 'tst')


class Ester2(EsterSpeakerDiarizationProtocol):
    """Speaker diarization protocol using Ester2 subset of ESTER"""

    def trn_iter(self):
        return self._subset('ester2', 'trn')

    def dev_iter(self):
        return self._subset('ester2', 'dev')

    def tst_iter(self):
        return self._subset('ester2', 'tst')



class Ester(Database):
    """ESTER corpus

Website
-------
www.afcp-parole.org/ester/
    """

    def __init__(self, preprocessors={}, **kwargs):
        super(Ester, self).__init__(preprocessors=preprocessors, **kwargs)

        self.register_protocol(
            'SpeakerDiarization', 'Ester1', Ester1)

        self.register_protocol(
            'SpeakerDiarization', 'Ester2', Ester2)
