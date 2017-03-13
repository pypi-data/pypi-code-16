class RepositoryListeners(object):
    def __init__(self):
        self.listeners = []  # type: list[RepositoryListener]

    def add_listener(self, obj):
        if obj not in self.listeners:
            self.listeners.append(obj)

    def add_listeners(self, obj_list):
        for obj in obj_list:
            self.add_listener(obj)

    def register_repository(self, repo):
        for listener in self.listeners:
            if repo not in listener.repositories.values():
                listener.register_new_repo(repo)

    def load_config(self, config):
        for listener in self.listeners:
            listener.load_config(config)

    def start(self):
        for listener in self.listeners:
            listener.start()


class RepositoryListener(object):
    def __init__(self):
        self.repositories = {}

    def start(self):
        raise NotImplementedError

    def load_config(self, config):
        pass

    def register_new_repo(self, repo):
        self.repositories[repo.name] = repo

