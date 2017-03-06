import slumber
from oauthlib.oauth2 import LegacyApplicationClient
from requests_oauthlib import OAuth2Session

class CloudFoundrySlumberClient(slumber.API):
    def __init__(self, username, password, endpoint="https://api.run.pivotal.io/", verify=None):
        session = OAuth2Session(client=LegacyApplicationClient(client_id="cf"))

        if verify is not None:
            session.verify = verify

        super(CloudFoundrySlumberClient, self).__init__(endpoint, append_slash=False, session=session)
        session.fetch_token(token_url=self._auth_token_url(),
                            username=username,
                            password=password,
                            client_id='cf')

    def _auth_token_url(self):
        cf_info = self.v2.info.get()
        return '%s/oauth/token' % (cf_info['authorization_endpoint'],)
