from setuptools import setup, find_packages

setup(name='dict_paths',
      version='0.6',
      description='Get all paths on a given dictionary',
      classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Topic :: Utilities',
      ],
      keywords='dictionary paths keys',
      url='https://github.com/ulisesojeda/dictionary_paths',
      author='Ulises Ojeda',
      license='MIT',
      packages=find_packages(),
      install_requires=[],
      include_package_data=True,
      zip_safe=False)
