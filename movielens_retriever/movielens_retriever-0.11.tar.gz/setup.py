from setuptools import setup, find_packages

setup(name='movielens_retriever',
      version='0.11',
      description='A package to download movielens dataset and create interactions matrices',
      author='Datrik Intelligence, S.A.',
      author_email='info@datrik.com',
      url='https://github.com/datrik/movielens_retrivever',
      download_url='https://github.com/datrik/movielens_retrivever/tarball/0.11',
      packages=find_packages(),
      license='MIT',
      keywords='datrik movielens dataset interaction matrix',
      classifiers=["Operating System :: OS Independent",
                   "Programming Language :: Python",
                   "Topic :: Software Development :: Libraries :: Python Modules"
                   ],
     )
