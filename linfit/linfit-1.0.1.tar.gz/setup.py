from distutils.core import setup

setup(
  name = 'linfit',
  packages = ['linfit'], # this must be the same as the name above
  version = '1.0.1',
  description = 'Linear regression with MCMC',
  author = 'Jinyi Shangguan',
  author_email = 'shangguan@pku.edu.cn',
  license="MIT",
  url = 'https://github.com/darkbear9494/LinFit',
  download_url = 'https://github.com/darkbear9494/LinFit/tarball/1.0',
  keywords = ['fitting', 'MCMC', 'linear regression'],
  install_requires=["numpy", "matplotlib", "emcee"],
  classifiers = [],
)
