from distutils.core import setup

setup(
    name='aianalytics-client',
    version='0.1.0',
    description='This project enables quering the Application Insights Analytics API while parsing the results for furthur processing using data analysis tools, such as numpy',

    # The project's main homepage.
    url='https://github.com/asafst/ApplicationInsightsAnalyticsClient-Python',
    download_url='https://github.com/asafst/ApplicationInsightsAnalyticsClient-Python',

    # Author details
    author='Asaf Strassberg',
    author_email='asafst@microsoft.com',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 4 - Beta',

        # Indicate who your project is intended for
        'Intended Audience :: Science/Research',
        'Intended Audience :: Developers',

        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Software Development :: Libraries :: Python Modules',

        # operating systems
        'Operating System :: OS Independent',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
    ],

    # Choose your license
    license='MIT',

    # What does your project relate to?
    keywords='analytics applicationinsights telemetry appinsights numpy IPython'
)

