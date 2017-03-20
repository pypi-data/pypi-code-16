#coding: utf-8


def product_load_images(*args, **kwargs):
    from soap_1c_api.lxml_import import load_images
    from lfs.catalog.models import Product
    errors = {}
    for product_uid in kwargs:
        try:
            product = Product.objects.get(uid=product_uid)
            load_images(product, kwargs[product_uid])
        except Exception as e:
            errors[product_uid] = str(e)
    return errors
