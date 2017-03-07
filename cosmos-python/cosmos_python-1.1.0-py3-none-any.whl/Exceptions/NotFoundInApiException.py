
class NotFoundInApiException(Exception):

    def __init__(self):

        super(NotFoundInApiException, self).__init__("API couldn't resolve anything. Please check your API-Key and API-Name.")
