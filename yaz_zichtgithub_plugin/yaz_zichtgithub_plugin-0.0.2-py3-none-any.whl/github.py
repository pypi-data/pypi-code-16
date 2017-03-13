import github
import yaz

class Github(yaz.BasePlugin):
    login = None
    password = None

    def __init__(self):
        if not (self.login and self.password):
            raise RuntimeError("The login and password must be specified, please add a Github plugin override in your user directory")

        self.service = github.Github(self.login, self.password)

    def get_service(self):
        return self.service

