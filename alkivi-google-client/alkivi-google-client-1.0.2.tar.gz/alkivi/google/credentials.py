from oauth2client.service_account import ServiceAccountCredentials
from oauth2client.client import OAuth2Credentials


def get_service_credentials(key, scopes=[]):
    """Return a ServiceAccountCredentials filled."""
    credentials = ServiceAccountCredentials.from_json_keyfile_name(key, scopes)
    return credentials


def get_oauth_credentials(client_id, client_secret, refresh_token):
    """Return an OAuth2Credentials refreshed."""
    token_uri = 'https://accounts.google.com/o/oauth2/token'
    credentials = OAuth2Credentials(access_token=None,
                                    client_id=client_id,
                                    client_secret=client_secret,
                                    refresh_token=refresh_token,
                                    token_expiry=None,
                                    token_uri=token_uri,
                                    user_agent=None)
    return credentials
