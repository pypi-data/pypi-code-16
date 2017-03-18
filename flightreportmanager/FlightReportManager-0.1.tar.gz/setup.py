from setuptools import setup
 
setup(
	name='FlightReportManager',
	packages = ['FlightReportManager'],
	scripts=['scripts/RunFlightReportManager'],
	version='0.1',
	description = 'Store and manage your Parrot Bebop flights. Viusalise your flight and export it to many different formats.',
	author = 'Johannes Kinzig',
	author_email = 'johannes_kinzig@icloud.com',
	url = 'https://johanneskinzig.de/software-development/flightreportmanager.html',
	include_package_data=True,
	license='LICENSE.txt',
	install_requires=[
        "DroneDataConversion",
        "matplotlib",
        "appdirs",
    ]
	)
