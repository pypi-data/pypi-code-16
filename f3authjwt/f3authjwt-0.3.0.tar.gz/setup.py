from setuptools import setup

setup(name='f3authjwt',
      version='0.3.0',
      description='Module to secure endpoints using jwt token in ferris 3 framework',
      url='https://github.com/handerson2014/f3authjwt',
      author='Handerson Contreras',
      author_email='handerson.contreras@gmail.com',
      license='MIT',
      packages=['f3authjwt'],
      install_requires=['PyJWT', 'ferris'],
      zip_safe=False)
