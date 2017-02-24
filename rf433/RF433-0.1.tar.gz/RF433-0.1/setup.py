
from distutils.core import setup

setup(
    name='RF433',
    packages=['RF433'],
    version='0.1',
    description='RF433 library to send signals for various protocols using \
                    an arduino',
    author='Bruno Silva',
    author_email='brunomiguelsilva@ua.pt',
    url='https://github.com/bsilvr/pyRF433',
    download_url='https://github.com/bsilvr/pyRF433/tarball/0.1',
    keywords=['rf433', 'arduino'],
    classifiers=[],
)

install_requires = [
   'pyserial==3.1.1'
]
