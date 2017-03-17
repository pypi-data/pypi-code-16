# -*- coding: utf-8 -*-

__version__ = "0.2"

import sys
import subprocess
import requests
from optparse import OptionParser

#url = "http://prediction-tensorflow-aws.demo.pipeline.io/evaluate-tensorflow-java-image/tensorflow_inception/00000001"
#api_url = "http://api.demo.pipeline.io/prediction-tensorflow/evaluate-tensorflow-java-image/tensorflow_inception/00000001"

def main():
  print("PipelineIO CLI version %s." % __version__)
  print("Argument strings: %s" % sys.argv[1:])
  print("")
  print("Usage:")
  print("  pipelineio [options] <command> <args>") 
  print("")
  parser = OptionParser()
  parser.add_option("-t", "--target", dest="target", help="target host:port", default="prediction-tensorflow-aws.demo.pipeline.io")
  parser.add_option("-m", "--model", dest="model", help="model", default="tensorflow_inception")
  parser.add_option("-v", "--version", dest="version", help="version", default="00000001")

  (options, args) = parser.parse_args()

  command = args[0]
  print("Command: %s" % command)
  
  filename = args[1]
  print("Filename: %s" % filename)

  if (command == "classify"):
    classify(target=options.target, model=options.model, version=options.version, filename=filename)
  elif (command == "update"): 
    update(target=options.target, model=options.model, version=options.version, filename=filename)
  else:
    print("Invalid command.")
 
def classify(_sentinel=None, target=None, model=None, version=None, filename=None):
  print("Classifying image '%s'" % filename)
  print("")

  files = [('image', (filename, open(filename, 'rb')))]

  url = "http://%s/evaluate-tensorflow-java-image/%s/%s" % (target, model, version)
  print(url)
  print("")

  response = requests.post(url, files=files, timeout=60)
  print(response.text)

def update(_sentinel=None, target=None, model=None, version=None, filename=None):
  print("Update model '%s'" % model)
  print("")

  files = [('model', (filename, open(filename, 'rb')))]

  url = "http://%s/update-tensorflow-model/%s/%s" % (target, model, version)
  print(url)
  print("")

  response = requests.post(url, files=files, timeout=120)
  print(response.text)

main()
