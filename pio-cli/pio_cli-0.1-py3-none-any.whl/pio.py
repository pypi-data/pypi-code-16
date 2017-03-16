# -*- coding: utf-8 -*-

__version__ = "0.1"

import sys
import subprocess
import requests
from optparse import OptionParser

url = "http://prediction-tensorflow-aws.demo.pipeline.io/evaluate-tensorflow-java-image/tensorflow_inception/00000001"
api_url = "http://api.demo.pipeline.io/prediction-tensorflow/evaluate-tensorflow-java-image/tensorflow_inception/00000001"

def main():
  print("PipelineIO CLI version %s." % __version__)
  print("Argument strings: %s" % sys.argv[1:])
  print("")
  print("Usage:")
  print("  pipelineio [options] <command> <args>") 
  print("")
  parser = OptionParser()
  parser.add_option("-t", "--target", dest="target", help="target host:port", default="prediction-tensorflow-aws.demo.pipeline.io")
  parser.add_option("-v", "--version", dest="version", help="version", default="00000001")
#  parser.add_option("-f", "--filename", dest="filename", help="filename", metavar="FILE")

  (options, args) = parser.parse_args()

  command = args[0]
  filename = args[1]
 
  classify(target=options.target, version=options.version, filename=filename)

def classify(_sentinel=None, target=None, version=None, filename=None):
  print("Classifying image '%s'" % filename)
  print("")

  files = [('image', (filename, open(filename, 'rb')))]

  url = "http://%s/evaluate-tensorflow-java-image/tensorflow_inception/%s" % (target, version)
  print(url)
  print("")

  response = requests.post(url, files=files, timeout=5)
  print(response.text)

#main()
