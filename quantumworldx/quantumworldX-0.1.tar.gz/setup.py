from setuptools import setup
setup(name='quantumworldX',
      version='0.1',
      description='Basic library for the QuantumWorld edX course',
      url='https://pypi.python.org/pypi/quantumworld/0.1',
      author='Benjamin Sanchez Lengeling',
      author_email='beangoben@gmail.com',
      license='MIT',
      packages=['quantumworldX'],
      install_requires=['numpy>=1.11',
                        'matplotlib>=2.0',
                        'scipy>=0.12.0',
                        'ipython'
                        ],
      # download_url = 'https://github.com/peterldowns/mypackage/tarball/0.1',
      keywords=['Quantum Chemistry', 'edX',
                'Quantum Mechanics'],  # arbitrary keywords
      classifiers=[],
      )
