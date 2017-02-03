class EcrCleaner():
    def __init__(self, connection, tag):
        self.connection = connection
        self.tag = tag

    def delete_all_repositories(self):
        if self.tag == None:
            return "jojo"

