from setuptools import setup
setup(name='quantumworld',
      version='1.0b',
      description='Basic library for the QuantumWorldX course',
#      url='https://github.com/username/repo',
      author='Benjamin Sanchez Lengeling',
      author_email='beangoben@gmail.com',
      license='MIT',
      packages=['quantumworld'],
      install_requires=['numpy>=1.11',
                        'matplotlib>=1.5',
                        'scipy>=0.12.0',
                        ],
      # download_url = 'https://github.com/peterldowns/mypackage/tarball/0.1',
      keywords=['Quantum Chemistry', 'edX',
                'Quantum Mechanics'],  # arbitrary keywords
      classifiers=[],
      )
