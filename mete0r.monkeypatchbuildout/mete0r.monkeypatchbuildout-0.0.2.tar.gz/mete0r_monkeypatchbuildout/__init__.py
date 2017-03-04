# -*- coding: utf-8 -*-
#
#   mete0r.monkeypatchbuildout: monkeypatch buildout for some reason
#   Copyright (C) 2015-2016 mete0r <mete0r@sarangbang.or.kr>
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
from __future__ import absolute_import
import logging
import os.path


__version__ = '0.0.2'


logger = logging.getLogger('zc.buildout.monkeypatched')
patched = False


def monkeypatch_distsig(buildout):
    logger.info('Monkey-patching buildout _dists_sig: version %s', __version__)

    def dists_sig(dists):
        logger.debug('Running monkey-patched _dists_sig()')

        from zc.buildout.buildout import _dir_hash
        import pkg_resources
        seen = set()
        result = []
        for dist in dists:
            if dist in seen:
                continue
            seen.add(dist)
            logger.debug(
                'Distribution: %s at %s',
                dist.project_name,
                dist.location
            )
            location = dist.location

            # http://setuptools.readthedocs.io/en/latest/pkg_resources.html#distribution-attributes
            #
            #   "System" and "Development" eggs (i.e., ones that use the
            #   .egg-info format), however, are automatically given a
            #   precedence of DEVELOP_DIST.
            #
            if dist.precedence == pkg_resources.DEVELOP_DIST:
                egg_info_dir = os.path.join(
                    dist.location,
                    pkg_resources.to_filename(dist.project_name) + '.egg-info',
                )
                if os.path.isdir(egg_info_dir):
                    result.append(dist.project_name + '-' + dist_hash(dist))
                else:
                    result.append(dist.project_name + '-' +
                                  _dir_hash(location))
            else:
                result.append(os.path.basename(location))
        return result

    def dist_hash(dist):
        ''' Hash distribution files specified in SOURCES.txt '''

        from hashlib import md5
        import io
        from zc.buildout.buildout import text_type
        from zc.buildout.buildout import ignore_directories
        import zc.buildout.configparser
        import pkg_resources

        logger.info('Hashing a Distribution: %s', dist.project_name)
        location = dist.location
        egg_info_dir = os.path.join(
            location,
            pkg_resources.to_filename(dist.project_name) + '.egg-info',
        )
        SOURCES_txt = os.path.join(egg_info_dir, 'SOURCES.txt')
        source_paths = []
        with io.open(SOURCES_txt) as f:
            for line in f:
                line = line.strip()
                source_path = os.path.join(location, line)
                source_paths.append(source_path)
                logger.debug('Source file: %s', source_path)

        hash = md5()
        for_hash = ' '.join(source_paths)
        if isinstance(for_hash, text_type):
            for_hash = for_hash.encode()
        hash.update(for_hash)
        for path in source_paths:
            with io.open(path, 'rb') as f:
                data = f.read()
            hash.update(data)

        for (dirpath, dirnames, filenames) in os.walk(egg_info_dir):
            logger.debug('Hashing a directory: %s', dirpath)
            dirnames[:] = sorted(
                n for n in dirnames if n not in ignore_directories
            )
            filenames[:] = sorted(
                f for f in filenames
                if (not (f.endswith('pyc') or f.endswith('pyo'))
                    and os.path.exists(os.path.join(dirpath, f)))
            )
            for_hash = ' '.join(dirnames + filenames)
            if isinstance(for_hash, text_type):
                for_hash = for_hash.encode()
            hash.update(for_hash)
            for name in filenames:
                path = os.path.join(dirpath, name)
                if name == 'entry_points.txt':
                    f = open(path)
                    # Entry points aren't written in stable order. :(
                    try:
                        sections = zc.buildout.configparser.parse(f, path)
                        data = repr(
                            [(sname, sorted(sections[sname].items()))
                             for sname in sorted(sections)]
                        ).encode('utf-8')
                    except Exception:
                        f.close()
                        f = open(path, 'rb')
                        data = f.read()
                else:
                    f = open(path, 'rb')
                    data = f.read()
                f.close()
                hash.update(data)
        return hash.hexdigest()

    global patched
    if patched:
        return
    from zc.buildout import buildout
    patched = buildout._dists_sig
    buildout._dists_sig = dists_sig
