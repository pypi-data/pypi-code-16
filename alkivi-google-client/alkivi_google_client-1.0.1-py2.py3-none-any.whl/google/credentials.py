from oauth2client.service_account import ServiceAccountCredentials


def get_service_credentials(key, scopes=[]):
    """Return a ServiceAccountCredentials filled."""
    credentials = ServiceAccountCredentials.from_json_keyfile_name(key, scopes)
    return credentials


def get_oauth_credentials():
    """TODO."""
