

class Resource:

    def __init__(self, *, service, name):
        self.service = service
        self.name    = name

    @property
    def http_client(self):
        return self.service.http_client
