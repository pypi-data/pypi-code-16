import config

class Edit:
    
    def GET(self, id_product):
        result = config.model.get_product(int(id_product))
        return config.render.edit(result)

    def POST(self, id_product):
        form = config.web.input()
        image = config.web.input(product_image={})

        filedir = 'static/files'
        filepath = image.product_image.filename.replace('\\', '/')
        filename = filepath.split('/')[-1]
        fout = open(filedir + '/' + filename, 'w')
        fout.write(image.product_image.file.read())
        fout.close()
        product_image = filename

        config.model.edit_product(
            form['id_product'],
            form['product'],
            form['description'],
            form['stock'],
            form['purchase_price'],
            form['price_sale'],
            product_image
        )
        raise config.web.seeother('/')