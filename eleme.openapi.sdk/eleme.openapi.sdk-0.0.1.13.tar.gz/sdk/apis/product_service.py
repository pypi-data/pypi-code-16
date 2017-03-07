# -*- coding: utf-8 -*-


class ProductService:

    __client = None

    def __init__(self, client):
        self.__client = client

    def item(self, category_id):
        return self.__client.call("eleme.product.item.getItemsByCategoryId", {"categoryId": category_id})

    def item(self, item_id):
        return self.__client.call("eleme.product.item.getItem", {"itemId": item_id})

    def item(self, item_ids):
        return self.__client.call("eleme.product.item.batchGetItems", {"itemIds": item_ids})

    def item(self, category_id, properties):
        return self.__client.call("eleme.product.item.createItem", {"categoryId": category_id, "properties": properties})

    def item(self, category_id, items):
        return self.__client.call("eleme.product.item.batchCreateItems", {"categoryId": category_id, "items": items})

    def item(self, item_id, category_id, properties):
        return self.__client.call("eleme.product.item.updateItem", {"itemId": item_id, "categoryId": category_id, "properties": properties})

    def item(self, spec_ids):
        return self.__client.call("eleme.product.item.batchFillStock", {"specIds": spec_ids})

    def item(self, spec_ids):
        return self.__client.call("eleme.product.item.batchClearStock", {"specIds": spec_ids})

    def item(self, spec_ids):
        return self.__client.call("eleme.product.item.batchOnShelf", {"specIds": spec_ids})

    def item(self, spec_ids):
        return self.__client.call("eleme.product.item.batchOffShelf", {"specIds": spec_ids})

    def item(self, item_id):
        return self.__client.call("eleme.product.item.removeItem", {"itemId": item_id})

    def item(self, item_ids):
        return self.__client.call("eleme.product.item.batchRemoveItems", {"itemIds": item_ids})

    def category(self, shop_id):
        return self.__client.call("eleme.product.category.getShopCategories", {"shopId": shop_id})

    def category(self, category_id):
        return self.__client.call("eleme.product.category.getCategory", {"categoryId": category_id})

    def category(self, shop_id, name, description):
        return self.__client.call("eleme.product.category.createCategory", {"shopId": shop_id, "name": name, "description": description})

    def category(self, category_id, name, description):
        return self.__client.call("eleme.product.category.updateCategory", {"categoryId": category_id, "name": name, "description": description})

    def category(self, category_id):
        return self.__client.call("eleme.product.category.removeCategory", {"categoryId": category_id})

    def upload_image(self, image):
        return self.__client.call("eleme.file.uploadImage", {"image": image})

    def upload_image_with_remote_url(self, url):
        return self.__client.call("eleme.file.uploadImageWithRemoteUrl", {"url": url})

    def get_uploaded_url(self, hash):
        return self.__client.call("eleme.file.getUploadedUrl", {"hash": hash})

