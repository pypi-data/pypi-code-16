

class DeploymentException(Exception):
    """
    Exception for all deployment errors

    """
    def __init__(self, message):
        self.message = message
