from setuptools import setup

setup(name='bw2dataclient',
      version='0.6.1',
      description='Simple wrapper for accessing data resources over BOSSWAVE',
      url='https://github.com/gtfierro/pybw2dataclient',
      author='Gabe Fierro',
      author_email='gtfierro@cs.berkeley.edu',
      packages=['bw2dataclient'],
      install_requires=[
        'delorean==0.6.0',
        'msgpack-python==0.4.2',
        'bw2python'
      ],
      zip_safe=False)
