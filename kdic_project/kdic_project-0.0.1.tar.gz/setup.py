from setuptools import setup

setup(
    name='kdic_project',
    version='0.0.1',
    packages=['kdic_project'],
    description = 'A simple search in dictionary sizte on terminal for Korean',
    url='http://www.coupang.com',
    author='sonic',
    author_email='ultrakain@gmail.com',
    license='MIT',
    keywords='simple english dictionary korean',
    install_requires=[
        'requests>=2.13.0',
        'beautifulsoup4>=2.1.3'
    ],
    entry_points={
      'console_scripts': [
          'kdic = kdic_project.__main__:main'
      ]
    },
)