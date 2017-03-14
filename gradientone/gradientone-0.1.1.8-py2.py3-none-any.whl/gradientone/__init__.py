import ivi
import gateway_helpers
import gateway_client
import client_controller
import transmitters
import transformers
import coroutine_gateway
import motor_gateway
from version import __version__


__all__ = ['gateway_client', 'gateway_helpers', 'client_controller',
           'transmitters', 'transformers', 'coroutine_gateway'
           'motor_gateway']


def main():
    """kicks off client"""
    client_controller.run()
