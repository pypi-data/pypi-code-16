from setuptools import setup, find_packages

setup(name='worm-dao',
      version='0.1.3',
      description='Worst or wonderful DAO library',
      classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Topic :: Database :: Front-Ends",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Intended Audience :: Developers",
        ],
      author='Marcin Nowak',
      author_email='marcin.j.nowak@gmail.com',
      url='https://github.com/marcinn/worm',
      keywords='dao orm database',
      packages=find_packages('.'),
      include_package_data=True,
      zip_safe=True,
      )

