class APIException(Exception):
    def __init__(self, error, message, data=None):
        self.error = error
        self.message = message
        self.data = data

    def __str__(self):
        return self.error + ': ' + self.message

    def get_data(self):
        data = {'error': self.__class__.__name__, 'message': self.message}
        if self.data:
            data.update({'data': self.data})
        return data
