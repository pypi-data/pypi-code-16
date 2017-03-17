"""Integration with Facebook Messenger API"""
__all__ = 'Message',
__version_info__ = 1, 0, 1
__version__ = '.'.join(str(v) for v in __version_info__)

from fbmessage.message import Message
from fbmessage.constants import GRAPH_API
