from future.builtins.misc import input
from oauth2client import client

import json
import webbrowser
import argparse


class Credulous:
  """
    Class created to complete the oauth2 flow with a standard brainlabs
    client secret and scopes file
  """

  JSON = 'json'
  BROWSER = 'browser'
  LINK = 'link'
  DEFAULT_FILE_FORMAT = JSON
  DEFAULT_INTERACTION = LINK

  def __init__(self, client_secret_path, scopes_path, file_format=None):
    self.client_secret_path = client_secret_path
    self.scopes_path = scopes_path
    self.file_format = file_format or self.DEFAULT_FILE_FORMAT

  def authenticate(self):
    secrets = self._load(self.client_secret_path)
    scopes = self._load(self.scopes_path)
    credentials = self._create_credentials(secrets, scopes)
    secrets = self._update_secrets(secrets, credentials)
    self._store_secrets(secrets)
    print("Credentials are saved in your secrets file")

  def _load(self, file_path):
    if self.file_format == self.JSON:
      with open(file_path) as fh:
        return json.loads(fh.read())

  def _create_credentials(self, secrets, scopes):
    flow = self._make_flow(secrets, scopes)
    auth_uri = flow.step1_get_authorize_url()
    auth_code = self._interact(auth_uri)
    credentials = flow.step2_exchange(auth_code)
    return credentials

  def _make_flow(self, secrets, scopes):
    flow = client.OAuth2WebServerFlow(
      client_id=secrets['installed']['client_id'],
      client_secret=secrets['installed']['client_secret'],
      scope=scopes['scopes']['google'],
      user_agent='Brainlabs',
      redirect_uri='urn:ietf:wg:oauth:2.0:oob')
    return flow

  def _interact(self, uri):
    if self.DEFAULT_INTERACTION == self.LINK:
      print("Click here: ")
      print(uri)
    else:
      webbrowser.open(uri)
    auth_code = input('Enter the auth code: ')
    return auth_code

  def _update_secrets(self, secrets, credentials):
    secrets['access_token'] = credentials.access_token
    secrets['refresh_token'] = credentials.refresh_token
    secrets['expires_in'] = 3600
    # @change: also add 'created' attribute
    return secrets

  def _store_secrets(self, secrets):
    with open(self.client_secret_path, 'w') as fh:
      json.dump(secrets, fh)


def main():
  parser = argparse.ArgumentParser(
    description="""
  Tool for generating API credentials. Google API is supported.
  <scopes> is a json with a list of scope URL. The list should be under 
  scopes.google""")
  parser.add_argument('--secret',
    required=True,
    help='Path to your client secret json file')
  parser.add_argument('scopes')
  args = parser.parse_args()
  credulous = credulous.Credulous(args.secret, args.scopes)
  credulous.authenticate()