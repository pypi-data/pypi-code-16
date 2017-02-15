import logging

__author__ = 'Martin Borba - borbamartin@gmail.com'


def get_logger(class_name):
    """
    Gets a logger instance for the specified class name
    :param class_name: A string representing the class name
    :return: The logger object
    """
    # create logger
    logger = logging.getLogger(class_name)

    if not len(logger.handlers):
        # create console handler
        ch = logging.StreamHandler()

        # Setting the logger level to 'DEBUG' and the channel level to 'CRITICAL'
        # makes Behave's logging output clean until a test fails. The full logger output
        # for the failing scenario will then be displayed on Behave's failed scenario captured
        # logging

        # Set the level of the logger
        logger.setLevel(logging.DEBUG)

        # Set the level of the channel
        # Set to 'DEBUG' when running locally to get full console output
        ch.setLevel(logging.CRITICAL)

        # Create formatter
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s  ->  [%(name)s]')

        # Add formatter to ch
        ch.setFormatter(formatter)

        # Add ch to logger
        logger.addHandler(ch)

    return logger
