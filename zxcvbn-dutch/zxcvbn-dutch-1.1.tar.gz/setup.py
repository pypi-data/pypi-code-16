from setuptools import setup

setup(name='zxcvbn-dutch',
      version='1.1',
      description='Password strength estimator with Dutch support',
      author='Erik Romijn',
      author_email='github@erik.io',
      url='https://www.github.com/erikr/python-zxcvbn',
      packages=['zxcvbn'],
      package_data={
        'zxcvbn': ['generated/frequency_lists.json',
                   'generated/adjacency_graphs.json',
                   ],
        },
      classifiers=[
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        ],
     )
