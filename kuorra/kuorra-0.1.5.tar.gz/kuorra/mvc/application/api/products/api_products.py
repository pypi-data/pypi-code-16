import web
import config
import json

class Api_products:
    #http://api_products?user_hash=12345
    def GET(self):
        user_data = web.input()
        user_hash = user_data.user_hash
        if user_hash == '12345': #user_hash
            result = config.model.get_products()
            products_json = []
            for row in result:
                t= dict(row)
                products_json.append(t)
            web.header('Content-Type', 'application/json')
        else:
            raise web.seeother('/404')
        return json.dumps(products_json)
    
    #http://api_products?user_hash=12345&id_product=1
    def POST(self):
        user_data = web.input()
        user_hash = user_data.user_hash
        id_product = user_data.id_product

        print user_hash
        print id_product
        if user_hash == '12345': #user_hash
            try:
                result = config.model.get_product(int(id_product))
                print result
                products_json = []
                products_json.append(dict(result))
            except:
                products_json = '{}'
        else:
            raise web.seeother('/404')
        return json.dumps(products_json)
