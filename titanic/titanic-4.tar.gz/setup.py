
from setuptools import setup
setup(name='titanic',
      version='4',
      description='Practice ML & travis/coveralls with titanic data set',
      long_description='',
      author='Brooke V Mosby',
      author_email='brooke.mosby.byu@gmail.com',
      url='https://github.com/brookemosby/titanic',
      license='MIT',
      setup_requires=['pytest-runner',],
      tests_require=['pytest', 'python-coveralls'],
      install_requires=[
          "pandas",
          "numpy",
          "sklearn"
      ],
      packages=['TitanicAttempt'],
      include_package_data=True,
      scripts=['TitanicAttempt/TitanicAttempt.py'],
              
      classifiers=[
          'Development Status :: 2 - Pre-Alpha',
          'Intended Audience :: Other Audience',
          'Natural Language :: English',
          'Operating System :: MacOS',
          'Operating System :: Microsoft :: Windows',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.5',
      ],
)
