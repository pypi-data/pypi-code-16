import os
from distutils.core import setup
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()
setup(
    name = "CanvasGraph",
    version = "0.0.1",
    scripts = ['CanvasGraph.py','canvas.html','KB.js'],
    author = "Volodymyr Kopei",
    author_email = "vkopey@gmail.com",
    url = "",
    description = "Simple graphs editor based on HTML5 canvas",
    long_description="",
    license = "MIT",
    keywords=['graph','HTML5'],
    classifiers=[
    'Development Status :: 3 - Alpha',
    'License :: OSI Approved :: MIT License',
    'Natural Language :: Ukranian',
    'Operating System :: Microsoft :: Windows',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.7'
    ]
    )