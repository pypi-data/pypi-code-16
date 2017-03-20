"""A corpus of object images."""

import hashlib
import os
from setuptools import setup
import shutil
import urllib
import zipfile

# Download the corpus.
corpus = urllib.URLopener()
url = "https://bradylab.ucsd.edu/stimuli/ObjectsAll.zip"
corpus.retrieve(url, "corpus.zip")
hash = hashlib.md5(open("corpus.zip", 'rb').read()).hexdigest()

# Check the md5 hash.
if hash != "34361346f8f1a39dc48d42fc6bb3b413":
    raise Exception("md5 hash of downloaded corpus is incorrect.")

# Extract the images.
zf = zipfile.ZipFile("corpus.zip", 'r')
zf.extractall()
zf.close()

# Clean up the directory structure.
for f in os.listdir("OBJECTSALL"):
    shutil.move(
        os.path.join("OBJECTSALL", f),
        os.path.join("objects", f)
    )

os.remove("corpus.zip")
os.remove(os.path.join("objects", "Thumbs.db"))
shutil.rmtree("__MACOSX")
shutil.rmtree("OBJECTSALL")

# Rename the images.
for i, f in enumerate(os.listdir("objects")):
    if f.endswith((".jpg", ".JPG")):
        new_f = "{i}.jpg".format(i=i).zfill(4 + 4)
        os.rename(
            os.path.join("objects", f),
            os.path.join("objects", new_f)
        )

setup_args = dict(
    name='objects',
    packages=['objects'],
    version="0.2.2",
    description='A corpus of object images',
    url='http://github.com/suchow/Objects',
    maintainer='Jordan Suchow',
    maintainer_email='suchow@berkeley.edu',
    keywords=['objecs'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ],
    include_package_data=True,
    zip_safe=False,
)

setup(**setup_args)
