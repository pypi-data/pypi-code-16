from setuptools import setup

setup(name='blended_google_fonts',
      version='1.0',
      description='Easy Google Fonts import for Blended',
      url='http://jmroper.com/blended/',
      author='John Roper',
      author_email='johnroper100@gmail.com',
      license='GPL3.0',
      packages=['google_fonts'],
      install_requires=[
          'blended',
      ],
      zip_safe=False)
