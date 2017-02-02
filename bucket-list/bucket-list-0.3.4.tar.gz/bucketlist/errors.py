class BucketlistError(Exception):
    def __init__(self, description, error_code=None):
        Exception.__init__(self)
        self.description = description
        self.error_code = error_code

    def jsonify(self):
        return {
            'description': self.description
        }

    def __str__(self):
        return "{}".format(self.description)
