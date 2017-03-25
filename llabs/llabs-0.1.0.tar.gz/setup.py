from distutils.core import setup
import os,llabs.__init__
from glob import glob

#del os.link
setup(
    name="llabs",
    version=llabs.__version__,
    author="Vincent Dumont",
    author_email="vincentdumont@gmail.com",
    packages=["llabs"],
    requires=["numpy","matplotlib","scipy"],
    include_package_data=True,
    scripts = glob('scripts/*'),
    url="https://vincentdumont.github.io/LLabs/",
    description="LLabs - Automatic DLA finder algorithm for D/H candidates",
    install_requires=[]
)
