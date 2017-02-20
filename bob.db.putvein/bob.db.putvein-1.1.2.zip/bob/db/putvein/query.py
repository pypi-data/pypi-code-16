#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

"""This module provides the Dataset interface allowing the user to query the
PUT Vein database in the most obvious ways.
"""

import os
import six
from .models import File


class Database(object):

    def __init__(self):
        self.protocols = ('L', 'R', 'LR', 'RL')
        self.purposes = ('enroll', 'probe')
        self.kinds = ('palm', 'wrist')
        self.groups = ('train', 'dev', 'eval')


    def check_validity(self, l, obj, valid, default):
        """Checks validity of user input data against a set of valid values"""
        if not l:
            return default
        elif isinstance(l, six.string_types) or isinstance(l, six.integer_types):
            return self.check_validity((l,), obj, valid, default)

        for k in l:
            if k not in valid:
                raise RuntimeError('Invalid %s "%s". Valid values are %s, or lists/tuples of those' % (obj, k, valid))

        return l


    def check_ids_validity(self, ids, max_value):
        """Checks validity of client ids"""
        if not ids:
            return range(1, max_value + 1)

        invalid_ids = [ x for x in ids if (x > max_value) or (x < 1) ]
        if invalid_ids:
            raise RuntimeError('Invalid ids "%s". Valid values are between 1 and %d' % (invalid_ids, max_value))

        return ids


    def objects(self, protocol=None, purposes=None, ids=None, groups=None, kinds=None):
        """Returns a set of Files for the specific query by the user.

        Keyword Parameters:

        protocol
          One of the PUT protocols ('L', 'R', 'LR', 'RL').

        purposes
          The purposes required to be retrieved ('enroll', 'probe') or a tuple
          with several of them. If 'None' is given (this is the default), it is
          considered the same as a tuple with all possible values. This field is
          ignored for the data from the "train" group.

        ids
          Only retrieves the files for the provided list of client ids.  If 'None'
          is given (this is the default), no filter over the ids is performed.

        groups
          One of the groups ('train', 'dev', 'eval') or a tuple with several of them.
          If 'None' is given (this is the default), it is considered the same as a
          tuple with all possible values.

        kinds
          One of the protocolar kinds of data ('palm', 'wrist'), or a
          tuple with several of them.  If 'None' is given (this is the default),
          it is considered the same as a tuple with all possible values.

        Returns: A list of :py:class:`.File` objects.
        """

        # Check the parameters
        if protocol not in self.protocols:
            raise RuntimeError('Invalid protocol "%s". Valid values are %s' % (protocol, self.protocols))

        purposes = self.check_validity(purposes, "purposes", self.purposes, self.purposes)
        groups = self.check_validity(groups, "groups", self.groups, self.groups)
        kinds = self.check_validity(kinds, "kinds", self.kinds, self.kinds)

        if protocol in ('L', 'R'):
            ids = self.check_ids_validity(ids, 50)
        else:
            ids = self.check_ids_validity(ids, 100)

        # Create the result list of files
        result = []

        if protocol in ('L', 'R'):
            filtered_ids = [ (x, x) for x in ids ]
            result.extend(self._get_protocol(protocol, purposes, groups, filtered_ids, kinds, False, True))
        elif protocol == 'LR':
            if ('train' in groups) or ('dev' in groups):
                filtered_ids = [ (x, x) for x in ids if x <= 50 ]
                result.extend(self._get_protocol('L', purposes, groups, filtered_ids, kinds, False, False))
            if 'eval' in groups:
                filtered_ids = [ (x, x - 50) for x in ids if x > 50 ]
                result.extend(self._get_protocol('R', purposes, groups, filtered_ids, kinds, True, False))
        elif protocol == 'RL':
            if ('train' in groups) or ('dev' in groups):
                filtered_ids = [ (x, x) for x in ids if x <= 50 ]
                result.extend(self._get_protocol('R', purposes, groups, filtered_ids, kinds, False, False))
            if 'eval' in groups:
                filtered_ids = [ (x, x - 50) for x in ids if x > 50 ]
                result.extend(self._get_protocol('L', purposes, groups, filtered_ids, kinds, True, False))

        return result


    def _get_protocol(self, protocol, purposes, groups, ids, kinds, mirrored, split):
        result = []

        if protocol == 'L':
            side = 'Left'
        else:
            side = 'Right'

        train_processed = False

        for group in groups:

            for purpose in purposes:
                if group == 'train':
                    if train_processed:
                        continue
                    series = [1, 2, 3]
                    train_processed = True
                elif purpose == 'enroll':
                    series = [1]
                else:
                    series = [2, 3]

                if split:
                    if group == 'eval':
                        filtered_ids = [ x for x in ids if x[1] >= 26 ]
                    else:
                        filtered_ids = [ x for x in ids if x[1] <= 25 ]
                else:
                    filtered_ids = ids

                for kind in kinds:
                    kind = kind[0].upper() + kind[1:]
                    result.extend(self._get_files(kind, side, filtered_ids, series, mirrored))

        return result


    def _get_files(self, kind, side, filtered_ids, series, mirrored):
        result = []

        for id in filtered_ids:
            for serie in series:
                for n in range(1, 5):
                    result.append(
                        File(
                            os.path.join(
                                kind,
                                'o_%03d' % id[1],
                                side,
                                'Series_%d' % serie,
                                '%s_o%03d_%s_S%d_Nr%d.bmp' % (kind[0], id[1], side[0], serie, n)
                            ),
                            id[0],
                            mirrored
                        )
                    )

        return result
