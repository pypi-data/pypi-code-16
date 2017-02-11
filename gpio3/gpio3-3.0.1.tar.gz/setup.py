from setuptools import setup, find_packages
pkg = "gpio3"
ver = '3.0.1'
setup(name             = pkg,
      version          = ver,
      description      = "GPIO access module",
      author           = "Eduard Christian Dumitrescu",
      author_email     = "eduard.c.dumitrescu@gmail.com",
      license          = "LGPLv3",
      url              = "https://hydra.ecd.space/f/gpio3/",
      packages         = find_packages(),
      install_requires = [],
      classifiers      = ["Programming Language :: Python :: 3 :: Only"])

