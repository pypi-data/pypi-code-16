#!/usr/bin/env python
# encoding: utf-8

# Copyright (C) 2015-2017 Chintalagiri Shashank
# Released under the MIT license.

"""
Configuration parameters for the :mod:`fs_server` package.

This package was written for tendril. The default configuration attempts
to obtain the FILESYSTEMS to expose from the local tendril configuration,
if available.

If you want something else to happen, set the :data:`FILESYSTEMS` list
accordingly.

.. rubric:: Usage Example

>>> from fs_server import config
>>> config.FILESYSTEMS = ['root_folder', '/']
>>> config.SERVER_PORT = 1079

.. warning:: Don't actually do this. Use a real, safe path instead.

"""

from twisted.python import log

try:
    from tendril.utils import config
except ImportError:
    config = None

SERVER_PORT = 1080

FILESYSTEMS = []

FTP_ENABLE = True
FTP_PORT = 2021
FTP_FILESYSTEMS = []

if config:
    log.msg("Adding Wallet to FILESYSTEMS")
    FILESYSTEMS.append(('wallet', config.DOCUMENT_WALLET_ROOT))
    log.msg("Adding Docstore to FILESYSTEMS")
    FILESYSTEMS.append(('docstore', config.DOCSTORE_ROOT))
    if FTP_ENABLE is True:
        FTP_FILESYSTEMS.append(('docstore', config.DOCSTORE_ROOT))
    log.msg("Adding Refdocs to FILESYSTEMS")
    FILESYSTEMS.append(('refdocs', config.REFDOC_ROOT))
    if FTP_ENABLE is True:
        FTP_FILESYSTEMS.append(('refdocs', config.REFDOC_ROOT))
