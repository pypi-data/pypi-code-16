from setuptools import setup

setup(name='happiest',
      version='0.1',
      description='I am the happiest person in my own world.',
      long_description='Really, the happiest around.',
      classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Topic :: Text Processing :: Linguistic',
      ],
      keywords='funniest joke comedy flying circus',
      author='Lina Jung',
      author_email='jinghuayi.lina@gmail.com',
      license='MIT',
      install_requires=[
          'markdown', 'Python>=2.7'
      ],
      include_package_data=True,
      zip_safe=False)