from distutils.core import setup
import os,nuri.__init__
from glob import glob

#del os.link
setup(
    name="nuri",
    version=nuri.__version__,
    author="Vincent Dumont",
    author_email="vincentdumont@gmail.com",
    packages=["nuri"],
    requires=["numpy","matplotlib","scipy","pylab","obspy","mlpy","smtplib"],
    include_package_data=True,
    scripts = glob('scripts/*'),
    url="https://vincentdumont.github.io/nuri/",
    description="NURI Urban Magnetometry",
    install_requires=[]
)
