from setuptools import setup
readme = open('README.rst').read()

setup(name='marbaloo_schedule',
      version='0.1.0',
      description='Schedule support for cherrypy.',
      long_description=readme,
      url='http://github.com/marbaloo/marbaloo_schedule',
      author='Mahdi Ghane.g',
      license='MIT',
      keywords='schedule cherrypy marbaloo marbaloo_schedule',
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
          'schedule>=0.4.2'
      ],
      packages=['marbaloo_schedule'],
      )
