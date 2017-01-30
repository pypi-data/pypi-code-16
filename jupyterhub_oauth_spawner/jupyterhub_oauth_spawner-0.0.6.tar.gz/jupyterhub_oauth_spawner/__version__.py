"""jupyterhub oauth spawner version info"""

version_info = (
    0,
    0,
    6,
    #'dev',  # comment-out this line for a release
)
__version__ = '.'.join(map(str, version_info[:3]))

if len(version_info) > 3:
    __version__ = '%s%s' % (__version__, version_info[3])
