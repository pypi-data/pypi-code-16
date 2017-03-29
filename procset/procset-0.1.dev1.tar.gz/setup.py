# -*- coding: utf-8 -*-

from setuptools import setup


# All packaging information is located in the setup.cfg file.
setup(
    py_modules=[  # should be in setup.cfg, but it is not supported
        'procset',
        'intsetwrap',  # transition module, planned for removal
    ],
)
