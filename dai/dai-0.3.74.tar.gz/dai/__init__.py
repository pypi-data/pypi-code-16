from pkg_resources import get_distribution, DistributionNotFound

__version__ = None  # required for initial installation

try:
    __version__ = get_distribution('dai').version
except DistributionNotFound:
    VERSION ='dai-(local)'
else:
    VERSION = 'dai-' + __version__

from .worker import Worker
from .taskProcessors import TaskProcessor, ThreadedTaskProcessor, ProcessTaskProcessor
