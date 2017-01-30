"""
cloud_sptheme setup script
"""
#=========================================================
#init script env
#=========================================================
import sys,os
from os.path import abspath, join
root_path = abspath(join(__file__, ".."))
os.chdir(root_path)
lib_path = '.'
#=========================================================
#imports
#=========================================================
import re
from setuptools import setup, find_packages
import subprocess
import time
#=========================================================
#inspection
#=========================================================
with open(os.path.join("cloud_sptheme", "__init__.py")) as fh:
    version = re.search(r"""(?m)^__version__\s*=\s*['"](.*?)['"]\s*$""", fh.read()).group(1)
if os.environ.get("CLOUD_SETUP_TAG_RELEASE", "y").lower() in "yes y true t 1".split():
    try:
        # NOTE: for py26 compat, using Popen() instead of check_output()
        proc = subprocess.Popen(["hg", "tip", "--template", "{date(date, '%Y%m%d%H%M%S')}+hg.{node|short}"],
                                stdout=subprocess.PIPE)
        stamp, _ = proc.communicate()
        if proc.returncode:
            raise subprocess.CalledProcessError(1, [])
        stamp = stamp.decode("ascii")
    except (OSError, subprocess.CalledProcessError):
        stamp = time.strftime("%Y%m%d%H%M%S")
    version += ".post" + stamp

#=========================================================
#setup
#=========================================================
setup(
    #package info
    packages = find_packages(),
    package_data = { "cloud_sptheme": ["themes/*/*.*", "themes/*/static/*.*", "ext/*.css"] },
    zip_safe=False,

    install_requires=["sphinx>=1.4"],

    # metadata
    name = "cloud_sptheme",
    version = version,
    author = "Eli Collins",
    author_email = "elic@assurancetechnologies.com",
    description = "a nice sphinx theme named 'Cloud', and some related extensions",
    long_description="""\
This is a small package containing a Sphinx theme named "Cloud",
along with some related Sphinx extensions. To see an example
of the theme in action, check out it's documentation
at `<http://packages.python.org/cloud_sptheme>`_.
    """,
    license = "BSD",
    keywords = "sphinx extension theme",
    url = "https://bitbucket.org/ecollins/cloud_sptheme",
    download_url = "http://pypi.python.org/pypi/cloud_sptheme",
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Framework :: Sphinx :: Extension',
        'Framework :: Sphinx :: Theme',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Topic :: Documentation',
        'Topic :: Software Development :: Documentation',
    ],
    entry_points={
        'sphinx_themes': [
            'path = cloud_sptheme:get_theme_dir',
        ],
    },
)
#=========================================================
#EOF
#=========================================================
