from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='J_box',
      version='0.1.3.2',
      description='This is a compilation of the tools that I use from day-to-day',
      long_description = readme(),
      classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7'
      ],
      keywords='DavidJuboor DavidNJuboor Statistics ML MachineLearning',
      url='http://github.com/Djuboor/J_Box',
      author='David N Juboor',
      author_email='dnjuboor@gmail.com',
      license='MIT',
      packages=['J_Box'],
      include_package_data=True,
      zip_safe=False,

      test_suite='nose.collector',
      tests_require=['nose'],
      )

# In order to update metadata, and publish a new build in a single step:
#    python setup.py register sdist upload

# In order to run tests:
#	 python setup.py test