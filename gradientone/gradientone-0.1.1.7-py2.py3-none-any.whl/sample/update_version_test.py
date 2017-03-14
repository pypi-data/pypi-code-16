from pkg_resources import DistributionNotFound, get_distribution

from gradientone import client_controller


cc = client_controller.ClientController()

client_controller().check_for_updates()

try:
    _dist = get_distribution('gradientone')
except DistributionNotFound:
    __version__ = 'Please install this project with setup.py'
else:
    __version__ = _dist.version
