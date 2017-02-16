from demands import JSONServiceClient


class HubApiClient(object):
    """
    Client for Hub Service (registration and changes).

    :param str auth_token:

        An access token.

    :param str api_url:
        The full URL of the API.

    """

    def __init__(self, auth_token, api_url, session=None):
        headers = {'Authorization': 'Token ' + auth_token}
        if session is None:
            session = JSONServiceClient(url=api_url,
                                        headers=headers)
        self.session = session

    def get_registrations(self, params=None):
        """
        Filter params can include
        'stage', 'mother_id', 'validated', 'source', 'created_before'
        'created_after' """
        return self.session.get('/registrations/', params=params)

    def get_registration(self, registration):
        return self.session.get('/registrations/%s/' % registration)

    def create_registration(self, registration):
        return self.session.post('/registration/', data=registration)

    def get_changes(self, params=None):
        """
        Filter params can include
        'action', 'mother_id', 'validated', 'source', 'created_before'
        'created_after' """
        return self.session.get('/changes/', params=params)

    def get_change(self, change):
        return self.session.get('/changes/%s/' % change)

    def create_change(self, change):
        return self.session.post('/change/', data=change)
