from os.path import join, dirname

from setuptools import setup, find_packages

import easy_lang_GUI



setup(
    name='easy_lang_GUI',
    version=easy_lang_GUI.__version__,
    packages=find_packages(),
	description="GUI addon for easy_languages.",
	long_description="...",
	author="Larty",
    include_package_data=True,
    install_requires=['easy_languages>=0.1.4']
)