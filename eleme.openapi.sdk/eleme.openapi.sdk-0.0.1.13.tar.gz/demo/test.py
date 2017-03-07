from sdk.config import Config
from sdk.oauth.oauth_client import OAuthClient
from sdk.protocol.rpc_client import RpcClient
from sdk.apis.user_service import UserService
import json

config = Config(True, 'avGYo8TAFL', 'fc6e4922bda4148ab4a734f5acbe58a7ce3a684a', None, "https://open-api-sandbox-shop.alpha.elenet.me")

#config = Config(True, 'ja7rOj8Zkj', '4573a5f70a349661a8ce6489696e07d0e7d5a9b9', None, "https://open-api-sandbox-shop.alpha.elenet.me")


def get_token():
    oauth_client = OAuthClient(config.get_app_key(), config.get_secret())
    return oauth_client.get_token_in_client_credentials()


def get_token_by_auth_code():
    oauth_client = OAuthClient(config.get_app_key(), config.get_secret(),'http://vpca-phoenix-buttonwood-service-1.vm.elenet.me:8080/callback')
    auth_url = oauth_client.get_token_by_auth_code('864e688f17b624f866ab509009ef782e')
    print auth_url


def user_get_user(token):
    client = RpcClient(token)
    user_service = UserService(client)
    response=user_service.get_user()
    print response

if __name__ == '__main__':
    token = json.loads(get_token())['access_token']
    #print token
    #########test user_service#########
    user_get_user(token)
    #get_token_by_auth_code()


