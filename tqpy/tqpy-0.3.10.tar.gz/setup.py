from setuptools import setup, find_packages


setup(name='tqpy',
      version='0.3.10',
      description="""A compact, scalable, statistical analysis, and reporting package built on top of
                     pandas, and bokeh.""",
      author='Rashad Alston',
      author_email='ralston@yahoo-inc.com',
      url='https://www.github.com/notslar-ralston/tqpy',
      packages=find_packages(),
      package_data={'': ['LICESNSE.txt', 'README.md', 'requirements.txt']},
      include_package_data=True,
      platforms='any',
      license='BDS 3 Clause',
      install_requires=['numpy>=1.7.1', 'matplotlib>=1.5.2', 'pandas>=0.17.1', 'bokeh==0.12.3'],
      zip_safe=False,
      long_description="""

            A compact, scalable, statistical analysis, and reporting package built on top of
            pandas, and bokeh.

            Contact
            -------
            If you have any questions or comments about tqpy, please feel free to contact me via
            email at ralston@yahoo-inc.com.
            This project is hosted at: https://www.github.com/notslar-ralston/tqpy
            The documentation can be found at: https://www.github.com/notslar-ralston/tqpy
      """)
