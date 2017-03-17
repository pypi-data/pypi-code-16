from setuptools import setup
##from distutils.core import setup
import pip, sys
setup(
  name = 'superspider',
  packages = ['superspider'], # this must be the same as the name above
  version = '0.2.1',
  description = 'A web scraper that adapts to any web page structure, and design.',
  author = 'Calder White',
  author_email = 'calderwhite1@gmail.com',
  url = 'https://github.com/CalderWhite/superspider', # use the URL to the github repo
  download_url = 'https://github.com/CalderWhite/superspider/archive/master.zip', # I'll explain this in a second
  keywords = [], # arbitrary keywords
  classifiers = [],
  include_package_data=True
)
if "install" in sys.argv or "build" in sys.argv:
    print("Checking dependancies")
    #Yes, I know this isn't the best way to do this, but it works.
    dep = ["nltk","bs4"]
    nltkDep = ["brown","averaged_perceptron_tagger","stopwords","punkt"]
    for i in dep:
        r = pip.main(["install",i])
        # if the package is already installed, attempt to update it.
        if r:
            r = pip.main(["install",i,"--upgrade"])
    # some custom stuff for nltk
    import nltk
    print("Grabbing required nltk packages")
    for i in nltkDep:
        nltk.download(i)
