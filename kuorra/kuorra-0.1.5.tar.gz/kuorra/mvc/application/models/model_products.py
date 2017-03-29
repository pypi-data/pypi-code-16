import web
import config

db = config.db


def get_products():
    try:
        return db.select('products')
    except:
        return None

def get_product(id_product):
    try:
        return db.select('products', where='id_product=$id_product', vars=locals())[0]
    except:
        return None

def delete_product(id_product):
    try:
        return db.delete('products', where='id_product=$id_product', vars=locals())
    except:
        return None

def insert_product(product, description, stock, purchase_price, price_sale, product_image):
    try:
        db.insert('products',
                  product=product,
                  description=description,
                  stock=stock,
                  purchase_price=purchase_price,
                  price_sale=price_sale,
                  product_image=product_image)
    except:
        return None

def edit_product(id_products, product, description, stock, purchase_price, price_sale, product_image):
    try:
        db.update('products',
                  product=product,
                  description=description,
                  stock=stock,
                  purchase_price=purchase_price,
                  price_sale=price_sale,
                  product_image=product_image,
                  where='id_product=$id_product',
                  vars=locals())
    except:
        return None
