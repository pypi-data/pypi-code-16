#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from distutils.core import setup, Extension

tcpinfo = Extension('tcpinfo', sources = ['tcpinfo.c'])

version = "0.2.2"
desc = "TCPinfo is a Python3 extension written in C to collect information about TCP-sockets via Linux's inet_diag interface"

setup(
        name='tcpinfo',
        version = version,
        description = desc,
        long_description = desc,
        author = "Karlsruhe Institute of Technology - Institute of Telematics",
        author_email = "telematics@tm.kit.edu",
        maintainer = "Michael Koenig",
        maintainer_email = "michael.koenig2@student.kit.edu",
        url = "https://git.scc.kit.edu/CPUnetLOG/TCPinfo/",
        license = "BSD",
        ext_modules=[tcpinfo],
        platforms = "Linux",
        keywords = ['tcp', 'flow', 'log', 'analyze', 'network', 'traffic', 'linux', 'inet_diag', 'extension', 'module', 'kernel', 'socket'],
        classifiers = [
            'Development Status :: 4 - Beta',
            'License :: OSI Approved :: BSD License',
            'Programming Language :: C',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.5',
            'Operating System :: POSIX :: Linux',
            'Intended Audience :: Developers',
            'Topic :: Internet',
            'Topic :: System :: Logging',
            'Topic :: System :: Networking',
            'Topic :: System :: Networking :: Monitoring',
            'Topic :: System :: Operating System Kernels :: Linux',
        ]
        )
