import ivi
import client_controller
from version import __version__

__all__ = ['gateway_client', 'gateway_helpers', 'client_controller']


def main():
    """kicks off client"""
    client_controller.run()
