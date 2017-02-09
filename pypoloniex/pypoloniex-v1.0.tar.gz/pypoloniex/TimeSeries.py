import time
import csv
import json
import requests
import datetime as dt
import pandas as pd

def toUnix(stringdate):
	date = dt.datetime.strptime(stringdate, "%d/%m/%Y")
	return int(time.mktime(date.timetuple()))

def toDate(unixdate):
	date = dt.datetime.fromtimestamp(int(unixdate))
	return date.strftime('%d/%m/%Y %H:%M:%S')

def validPair(pair):
	with open('pairs.json', 'r') as infile:    
		pairs = json.load(infile)
	if '%s_%s' % (pair[0], pair[1]) not in pairs:
		print "Pair Error: Invalid trading pairs."
		return False
	return True
	
def validPeriod(period):
	periods = [300, 900, 1800, 7200, 14400, 86400]
	if period not in periods:
		print "Period Error: Period must be one of the following: %s." % \
		(str([300, 900, 1800, 7200, 14400, 86400]).strip('[]'))
		return False
	return True

def validDates(start, end):
	start = dt.datetime.strptime(start, "%d/%m/%Y")
	end = dt.datetime.strptime(end, "%d/%m/%Y")
	if (start > end):
		print "Date Error: Start date must come before end date."
		return False
	if (end-start).days > 365:
		print "Date Error: The time period must be less than a year."
		return False
	return True

def buildURL(pair, period, start, end):
	base = 'https://poloniex.com/public?command=returnChartData&currencyPair='
	return '%s%s_%s&start=%s&end=%s&period=%s' % \
	(base, pair[0], pair[1], toUnix(start), toUnix(end), period)

class TimeSeries(object):

	def __init__(self):
		self.empty = True
		self.data = None
		self.pair = ("None", "None")
		self.period = "None"
		self.start = "None"
		self.end = "None"

	def show(self):
		if self.empty:
			print "No data loaded!"
		else:
			print "Variables"
			print "Pair: ('%s', '%s')" % (self.pair[0], self.pair[1])
			print "Period: %s" % (self.period)
			print "Start: %s" % (self.start)
			print "End: %s" % (self.end)
			print
			print self.data

	def getData(self, pair, period, start, end):
		if not validPair(pair):
			return
		
		if not validPeriod(period):
			return
		
		if not validDates(start, end):
			return

		url = buildURL(pair, period, start, end)
		datapoints = requests.get(url)
		datapoints = datapoints.json()

		fields = ['date', 'open', 'low', 'high', 'close', 'weightedAverage', 'volume', 'quoteVolume']
		data = []
		for dtp in datapoints:
			row = []
			for fld in fields:			
				if fld == 'date':
					row.append(toDate(dtp[fld]))
				else:
					row.append(dtp[fld])
			data.append(row)
		
		self.data = pd.DataFrame(data, columns = fields)
		self.empty = False
		self.pair = pair
		self.period = period
		self.start = start
		self.end = end

	def toCSV(self, filename, sep = ','):
		if self.empty:
			print "No data loaded!"
			return
		self.data.to_csv(filename, sep = sep)

	def fromCSV(self, filename,  sep = ','):
		self.data = pd.read_csv(filename, sep = sep)
		self.empty = False
