from distutils.core import setup
import os,qscan.__init__
from glob import glob

#del os.link
setup(
    name="qscan",
    version=qscan.__version__,
    author="Vincent Dumont",
    author_email="vincentdumont@gmail.com",
    packages=["qscan"],
    requires=["numpy","matplotlib","scipy","astropy"],
    include_package_data=True,
    scripts = glob('scripts/*'),
    url="https://vincentdumont.github.io/qscan/",
    description="Quasar spectra scanner",
    install_requires=[]
)
