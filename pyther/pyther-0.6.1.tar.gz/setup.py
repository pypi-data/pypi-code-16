from distutils.core import setup

EXTRA_INFO = dict(
	install_requires=['django>=1.7,<1.8', 'one==0.2.1', 'django-picklefield==0.3.0',
                      'numpy>=1.8', 'matplotlib>=1.3', 'quantities'],
    classifiers=['Development Status :: 3 - Alpha',
                 'Intended Audience :: Developers',
                 'Intended Audience :: Science/Research',
                 'License :: Free To Use But Restricted',
                 'Topic :: Scientific/Engineering']
)


def find_data_files(source, target, patterns):
    """
    Locates the specified data-files and returns the matches
    in a data_files compatible format.
    source is the root of the source data tree.
    	Use '' or '.' for current directory.
    target is the root of the target data tree.
        Use '' or '.' for the distribution directory.
    patterns is a sequence of glob-patterns for the
        files you want to copy.
    """
    if glob.has_magic(source) or glob.has_magic(target):
        raise ValueError("Magic not allowed in src, target")
    ret = {}
    for pattern in patterns:
        pattern = os.path.join(source,pattern)
        for filename in glob.glob(pattern):
            if os.path.isfile(filename):
                targetpath = os.path.join(target,os.path.relpath(filename,source))
                path = os.path.dirname(targetpath)
                ret.setdefault(path,[]).append(filename)
    return sorted(ret.items())


setup(
	name = "pyther",
	packages = ["pyther"],
	version = "0.6.1",
	description = "A open source library for processing thermodynamics data",
	author = "pysg",
	author_email = "andres.pyther@gmail.com",
	url = "https://github.com/pysg/pyther",
	include_package_data=True,
	keyword = ["data analytics", "phases diagram", "thermodynamics"]

)