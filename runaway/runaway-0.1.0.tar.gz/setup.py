"""Setup script."""


# [ Imports ]
from setuptools import find_packages, setup


# [ Setup ]
setup(
    name='runaway',
    version='0.1.0',
    description='Coroutine runner',
    url='https://gitlab.com/toejough/runaway',
    author='toejough',
    author_email='toejough@gmail.com',
    license='Apache 2.0',
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: Apache Software License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
    ],
    keywords="coroutine generator executor execute test run",
    packages=find_packages(),
    install_requires=[],
    extras_require={
        'checkers': [
            'pocketwalk',
            'dodgy',
            'flake8-bugbear', 'flake8-docstrings', 'flake8-import-order',
            'mypy',
            'pylint',
            'vulture',
            'otter',
        ]
    }
)
