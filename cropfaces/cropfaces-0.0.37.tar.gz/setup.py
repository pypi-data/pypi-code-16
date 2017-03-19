# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name='cropfaces',
    version='0.0.37',
    url='https://github.com/tuaplicacionpropia/cropfaces',
    download_url='https://github.com/tuaplicacionpropia/cropfaces/archive/master.zip',
    author=u'tuaplicacionpropia.com',
    author_email='tuaplicacionpropia@gmail.com',
    description='Librería Python: Recorta imágenes dejando las caras para adaptarse a una escala concreta.',
    long_description='Librería Python: Recorta imágenes dejando las caras para adaptarse a una escala concreta.',
    keywords='jpg, png',
    classifiers=[
      'Development Status :: 4 - Beta',
      'License :: OSI Approved :: MIT License',
      'Programming Language :: Python', 
      'Programming Language :: Python :: 2.7', 
      'Intended Audience :: Developers', 
      'Topic :: Multimedia :: Graphics',
    ],
    scripts=['bin/cropfaces', 'bin/cropfaces.cmd',],
    packages=find_packages(exclude=['tests']),
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    license='MIT',
    install_requires=[
        'numpy==1.12.0b1', 
        'opencv-python==3.1.0.3', 
        'Pillow==3.4.2',
    ],
)

