from setuptools import setup

setup(name='blended_html_comment_box',
      version='1.0',
      description='Easy comments plugin for Blended powered by HTML Comment Box',
      url='http://jmroper.com/blended/',
      author='John Roper',
      author_email='johnroper100@gmail.com',
      license='GPL3.0',
      packages=['html_comment_box'],
      install_requires=[
          'blended',
      ],
      zip_safe=False)
