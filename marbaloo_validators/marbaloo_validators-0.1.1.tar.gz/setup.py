from setuptools import setup
readme = open('README.rst').read()

setup(name='marbaloo_validators',
      version='0.1.1',
      description='Validators library support for cherrypy.',
      long_description=readme,
      url='http://github.com/marbaloo/marbaloo_validators',
      author='Mahdi Ghane.g',
      license='MIT',
      keywords='validators cherrypy marbaloo marbaloo_validators',
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Intended Audience :: Developers',
          'Framework :: CherryPy',
          'License :: OSI Approved :: MIT License',
          'Operating System :: POSIX :: Linux',
          'Operating System :: Unix',
          'Programming Language :: Python :: 3 :: Only',
          'Topic :: Software Development :: Libraries'
      ],
      install_requires=[
          'cherrypy>=8.1.2',
          'validators>=0.11.2'
      ],
      packages=['marbaloo_validators'],
      )



