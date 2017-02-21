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


class REPERESpeakerDiarizationProtocol(SpeakerDiarizationProtocol):
    """Base speaker diarization protocol for REPERE database

    This class should be inherited from, not used directly.

    Parameters
    ----------
    preprocessors : dict or (key, preprocessor) iterable
        When provided, each protocol item (dictionary) are preprocessed, such
        that item[key] = preprocessor(**item). In case 'preprocessor' is not
        callable, it should be a string containing placeholder for item keys
        (e.g. {'wav': '/path/to/{uri}.wav'})
    """

    def __init__(self, preprocessors={}, **kwargs):
        super(REPERESpeakerDiarizationProtocol, self).__init__(
            preprocessors=preprocessors, **kwargs)
        self.uem_parser_ = UEMParser()
        self.mdtm_parser_ = MDTMParser()

    def _subset(self, protocol, subset):

        data_dir = op.join(op.dirname(op.realpath(__file__)), 'data')

        # load annotated parts
        # e.g. /data/speaker/{dryrun|phase1|phase2}.{trn|dev|tst}.uem
        path = op.join(data_dir,
                       'speaker',
                       '{protocol}.{subset}.uem'.format(subset=subset, protocol=protocol))
        uems = self.uem_parser_.read(path)

        # load annotations
        path = op.join(data_dir,
                       'speaker',
                       '{protocol}.{subset}.mdtm'.format(subset=subset, protocol=protocol))
        mdtms = self.mdtm_parser_.read(path)

        for uri in sorted(uems.uris):
            annotated = uems(uri)
            annotation = mdtms(uri)
            current_file = {
                'database': 'REPERE',
                'uri': uri,
                'annotated': annotated,
                'annotation': annotation}
            yield current_file


class DryRun(REPERESpeakerDiarizationProtocol):
    """REPERE dry-run speaker diarization protocol"""

    def dev_iter(self):
        return self._subset('dryrun', 'dev')

    def tst_iter(self):
        return self._subset('dryrun', 'tst')


class Phase1(REPERESpeakerDiarizationProtocol):
    """REPERE phase 1 speaker diarization protocol"""

    def trn_iter(self):
        return self._subset('phase1', 'trn')

    def dev_iter(self):
        return self._subset('phase1', 'dev')

    def tst_iter(self):
        return self._subset('phase1', 'tst')


class Phase2(REPERESpeakerDiarizationProtocol):
    """REPERE phase 2 speaker diarization protocol"""

    def trn_iter(self):
        return self._subset('phase2', 'trn')

    def dev_iter(self):
        return self._subset('phase2', 'dev')

    def tst_iter(self):
        return self._subset('phase2', 'tst')

class All(REPERESpeakerDiarizationProtocol):
    """All REPERE data

    * Phase1 test
    * Phase2 train
    * Phase2 development
    * Phase2 test
    """

    def trn_iter(self):
        return self._subset('all', 'trn')

class REPERE(Database):
    """REPERE corpus

Reference
---------

Citation
--------
@inproceedings{REPERE,
}

Website
-------
    """

    def __init__(self, preprocessors={}, **kwargs):
        super(REPERE, self).__init__(preprocessors=preprocessors, **kwargs)

        self.register_protocol(
            'SpeakerDiarization', 'DryRun', DryRun)

        self.register_protocol(
            'SpeakerDiarization', 'Phase1', Phase1)

        self.register_protocol(
            'SpeakerDiarization', 'Phase2', Phase2)

        self.register_protocol(
            'SpeakerDiarization', 'All', All)
