from distutils.core import setup

setup(
    name='aianalytics-client',
    packages = ['analytics'],
    version='0.1.1',
    description='This project enables quering the Application Insights Analytics API while parsing the results for furthur processing using data analysis tools, such as numpy',

    url='https://github.com/asafst/ApplicationInsightsAnalyticsClient-Python',
    download_url='https://github.com/asafst/ApplicationInsightsAnalyticsClient-Python',

    author='Asaf Strassberg',
    author_email='asafst@microsoft.com',

    classifiers=[
        'Development Status :: 4 - Beta',

        'Intended Audience :: Science/Research',
        'Intended Audience :: Developers',

        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Software Development :: Libraries :: Python Modules',

        'Operating System :: OS Independent',

        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
    ],

    license='MIT',
    keywords='analytics applicationinsights telemetry appinsights numpy IPython'
)

