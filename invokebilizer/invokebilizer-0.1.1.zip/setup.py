from setuptools import setup

# Version info -- read without importing
_locals = {}
with open('invokebilizer/_version.py') as fp:
    exec (fp.read(), None, _locals)
__version__ = _locals['__version__']

"""
This library provides compatible interface subset between multiple `invoke` versions.
I.e. you can use invoke 0.13 interface while you have only invoke 0.10 installed in your system.
It also provides additional helpful methods, like `run_all`, which may be used for running multiple tasks (with individula failure handling) inside of single task.
"""
setup(name='invokebilizer',
      version=__version__,
      url='https://github.com/mirasrael/pyinvokebilizer',
      license='MIT',
      author='Alexander Bondarev',
      author_email='alexander.i.bondarev@gmail.com',
      description='INVOKE staBILIZER - wrapper lib to work with any invoke version through requested interface',
      long_description=__doc__,
      zip_safe=True,
      packages=[
          'invokebilizer',
      ],
      platforms='any',
      install_requires=[
          'invoke>=0.10,<0.16',
          'six'
      ],
      tests_require=[
          'nose',
          'tox',
      ],
      classifiers=[
          'Environment :: Console',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3.5',
          'Topic :: Software Development :: Libraries :: Python Modules',
      ]
      )
