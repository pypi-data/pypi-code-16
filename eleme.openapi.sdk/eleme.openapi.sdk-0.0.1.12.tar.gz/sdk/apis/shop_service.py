# -*- coding: utf-8 -*-


class ShopService:

    __client = None

    def __init__(self, client):
        self.__client = client

    def get_shop(self, shop_id):
        return self.__client.call("eleme.shop.getShop", {"shopId": shop_id})

    def update_shop(self, shop_id, properties):
        return self.__client.call("eleme.shop.updateShop", {"shopId": shop_id, "properties": properties})

    def mget_shop_status(self, shop_ids):
        return self.__client.call("eleme.shop.mgetShopStatus", {"shopIds": shop_ids})

