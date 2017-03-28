from setuptools import setup

setup(name='risk_hedger',
      version='0.1',
      description='Risk Hedger powered by SliceMatrix-IO',
      url='http://www.slicematrix.com/',
      author='Hekaton LLC',
      author_email='tynan@slicematrix.com',
      license='MIT',
      packages=['risk_hedger'],
      install_requires=[
          'numpy>=1',
          'pandas',
          'requests==2.5.3'
      ],
      zip_safe=False)
