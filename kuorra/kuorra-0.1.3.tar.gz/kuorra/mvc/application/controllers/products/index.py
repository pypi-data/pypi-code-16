import config

class Index:

    def GET(self):
        result = config.model.get_products()
        return config.render.index(result)
