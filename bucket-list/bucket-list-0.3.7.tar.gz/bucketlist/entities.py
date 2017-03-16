class BucketlistItem:
    def __init__(self, item_id, message, is_completed):
        self.id = item_id
        self.message = message
        self.is_completed = is_completed


class BucketlistCategory:
    def __init__(self, name):
        self.name = name
