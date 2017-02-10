"""
Botman specific errors and exceptions
"""

class BotmanError(Exception):
    """
    Generic Botman exception
    """

class ConfigurationError(BotmanError):
    """
    Botman configuration error
    """

class CommandUsageError(BotmanError):
    """
    Thrown when a user incorrectly uses a command
    """

