class FlaskAssistantError(Exception):
    """Base exception for the library"""
    def __init__(self, msg=None):
        if msg is not None:
            msg = "An error occured within Flask-Assistant"
        super().__init__(msg)


class HomeAssistantImportError(ImportError):
    def __init__(self, name):
        if name == 'homeassistant':
            msg = """You are trying to import HassRemote but do not have homeassistant installed.
                    Ensure you have homeinstall installed in the current environment.
                    pip install homeassistant
                    {}""".format(args)
        super().__init__(msg)

