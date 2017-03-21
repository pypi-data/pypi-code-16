# FlightReportManager
#
# Copyright (C) 2016 Johannes Kinzig
# Author: Johannes Kinzig <johannes_kinzig@icloud.com>
# URL: <https://johanneskinzig.de/software-development/python-parser-bebop-logs.html>
#
# $Id: __init__.py 0001 20016-06-11 jokinzig $

"""
When flying the Parrot Bebop Quadcopter (and the Bebop 2 Quadcaopter) stores all flight information in a log file. This is a so called pud file and has a json structure.
This application stores the content in a human readble way in an SQLite database in a way the user has access to it. The user can track his fights without the need to upload the flights to the Parrot Cloud
(know as ArDrone Academ, Drone Academy, etc.).
The flight can be exported as gpx, csv, and kml. The application uses the underlying library "DroneDataConversion".
The application seems to work but is still in beta phase.

Data which is stored in the sqlite database:
	- FlightID
	- event_name
	- city_nearby
	- pilot_location
	- date_time
	- total_distance
	- max_altitude
	- avg_speed
	- flight_duration
	- controller_type
	- drone_type
	- battery_usage
	- raw_data_file_name


Python Interpreter:
This library was written using legacy Python 2.7.10. At the current state it is untested under Python 3 and will most likely run under Python 2.7. only

Package Organization
====================

@author: `Johannes Kinzig <johannes_kinzig@icloud.com>`__
@requires: Python 2.7.10+
@version: 0.1
@see: `The documentation webpage <https://johanneskinzig.de/software-development/python-parser-bebop-logs.html>`__

@todo: Implement kml export
@todo: Improve documentation and epydoc generation


@license: Apache License, Version 2.0
@copyright: |copy| 2016 Johannes Kinzig

@newfield contributor: Contributor, Contributors (Alphabetical Order)
@contributor: `Johannes Kinzig  <mailto:johannes_kinzig@icloud.com>`__

"""
__docformat__ = 'epytext en'

__version__ = '0.1'
"""The version of FlightReportManager"""

__author__ = 'Johannes Kinzig <johannes_kinzig@icloud.com>'
"""The primary author of FlightReportManager"""

__url__ = 'https://johanneskinzig.de/software-development/python-parser-bebop-logs.html'
"""The URL for FlightReportManager's homepage"""

__license__ = 'Apache License, Version 2.0'
"""The license governing the use and distribution of DroneDataConversion"""

# [xx] this should probably be a private variable:
DEBUG = False
"""True if debugging is turned on."""