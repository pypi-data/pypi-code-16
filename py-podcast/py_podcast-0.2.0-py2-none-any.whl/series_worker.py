import threading
import csv
from models.series import Series
from series_crawler import SeriesCrawler
import time
import os

class SeriesWorker(threading.Thread):

  def __init__(self, directory, tups, i):
    """
    Constructor - `tups` contains two-element
    tuples, containing the name of the genre,
    along with a url with podcasts related to
    that genre
    """
    super(SeriesWorker, self).__init__()
    self.directory = directory
    self.tups      = tups
    self.i         = i
    self.crawler   = SeriesCrawler()
    # Make this ...
    if not os.path.exists('./' + self.directory):
      os.makedirs('./' + self.directory)


  def run(self):
    """Requests, parses series, writes to appropriate CSV"""
    while self.i < len(self.tups):
      # Grab fields
      name = self.tups[self.i][0]
      url  = self.tups[self.i][1]
      namestamp = name + '-' + \
        str(int(round(time.time()))) + '.csv' # For timestamping the CSV

      # GET request
      print "Attempting to request " + name
      self.crawler.set_url(url)
      series = self.crawler.get_series()
      print "Attempting to write " + name

      # Grab writer -> writes series
      writer = csv.writer(open('./' + self.directory + '/' + namestamp, 'wb'))
      writer.writerow(Series.fields)
      for s in series:
        writer.writerow(s.to_line())

      # Move onto the next one
      self.i += 10
      print("Wrote " + name)
