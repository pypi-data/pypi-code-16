from setuptools import setup


setup(
    name='gripit_capture',
    version='1.0.5',
    description='A webcam extension package for GripIt App - Add GOPRO Support',
    url='http://github.com/agilefreaks',
    author='Agilefreaks',
    author_email='agilefreaks@agilefreaks.com',
    license='MIT',
    packages=[
        'gopro',
        'webcam',
        'webcam.data',
        'webcam.jobs',
        'webcam.services'
    ],
    install_requires=[
        'imutils >= 0.3.10'
    ],
    tests_require=['pytest', 'mock'],
    zip_safe=False
)
