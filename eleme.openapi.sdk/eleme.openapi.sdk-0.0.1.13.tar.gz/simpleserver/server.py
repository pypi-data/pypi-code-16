# -*- coding: utf-8 -*-
import json
import web
from sdk.util.callback_signature_util import CallbackValidationUtil
from sdk.oauth.oauth_client import OAuthClient
from sdk.config import Config
from sdk.protocol.rpc_client import RpcClient
import uuid

urls = (
        '/listenMessage', 'ListenMessage',
        '/callback', 'CallBack',
        '/getInfo', 'GetUserInfo',
        )


class ListenMessage(object):
    def GET(self):
        return '{"message":"ok"}'

    def POST(self):
        message = web.data()
        if not CallbackValidationUtil.is_valid_message(message):
            return '{"message":"InvalidSignature"}'
        return '{"message":"ok"}'


class CallBack(object):
    def GET(self):
        render = web.template.render('templates')
        params = web.input()
        if not params:
            return render.demo()
        auth_code = params.code
        if auth_code:
            oauth_client = OAuthClient(Config.get_app_key(), Config.get_secret(), Config.get_callback_url())
            response = oauth_client.get_token_by_auth_code(auth_code)
            #response = oauth_client.get_token_in_client_credentials()
            token = json.loads(response)['access_token']
            rpc_client = RpcClient(token)
            user_info = rpc_client.call("eleme.user.getUser", {})
            user_id = user_info['userId']
            f = open("mapping.txt", "a")
            f.write(str(user_id)+token+'\n')
            f.close()
            return render.redirect(user_id,user_info['authorizedShops'][0]['id'])
        else:
            return render.demo()


class GetUserInfo(object):
    def POST(self):
        data = web.data()
        print data
        result = {}
        params = json.loads(data)
        user_id = params['userId']
        shop_id = params['shopId']
        file = open("mapping.txt", "r")
        while 1:
            line = file.readline()
            if not line:
                oauth_client = OAuthClient(Config.get_app_key(), Config.get_secret(), Config.get_callback_url())
                auth_url = oauth_client.get_auth_url(str(uuid.uuid4()), 'all')
                result['authUrl'] = auth_url
                return result
            if user_id == line.split(':')[0]:
                token = line.split(':')[1]
                rpc_client = RpcClient(token)
                user_info = rpc_client.call("eleme.user.getUser", {})
                result['userInfo'] = user_info
                authorized_shops = user_info['authorizedShops']
                for shop in authorized_shops:
                    if shop['id'] == int(shop_id):
                        shop_info = rpc_client.call("eleme.shop.getShop", {"shopId": int(shop_id)})
                        result['shopInfo'] = shop_info
                        return result
        return result


def start_server():
    app = web.application(urls, globals())
    app.run()

if __name__ == "__main__":
    # config = Config(True, 'avGYo8TAFL', 'fc6e4922bda4148ab4a734f5acbe58a7ce3a684a', None,
    #                 "https://open-api-sandbox-shop.alpha.elenet.me")
    Config(True, 'ja7rOj8Zkj', '4573a5f70a349661a8ce6489696e07d0e7d5a9b9',
           'http://vpca-phoenix-buttonwood-service-1.vm.elenet.me:8080/callback', "https://open-api-sandbox-shop.alpha.elenet.me")
    start_server()
