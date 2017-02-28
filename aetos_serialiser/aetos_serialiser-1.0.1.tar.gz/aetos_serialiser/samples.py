from helpers import dict_reducer, get_module
from serialisers import Serializer

getting = {
    "product_id": "2206219",
    "product_name": "Laundry Basket 2 Pcs Combo",
    "product_sku": "MKUBE13730961290",
    "product_qty": 1,
    "product_price": "599.0000",
    "cod_available": None,
    "product_image": "/C/V/CV-MKUBE13730961290-Home_Decor-Kuber_Industries-Craftsvilla_1.jpeg",
    "discount": "59.9000",
    "seller_note": "",
    "quote_item_id": "16069896"
}


class ProductSerializer(Serializer):
    BODY_MAP = {
        "qty": ("product_qty", float),
        "productName": ("product_name", str, ""),
        "regularPrice": ("__self___get_regular_price", float),
        "discountPercentage": ("__self___get_disc_percentage", float),
        "discountedPrice": ("__self___get_disc_price", float),
        "vendorDetails": ("__default__dict", dict),
        "variants": {
            "size": ("variant__Size", list, [], False),
            "color": ("variant__Color", list, [], False),
        },
        "imgUrl": ("product_image", str, "", False),
        "productId": ("product_id", str),
        "vendorPincode": ("vendor_pincode", str, "000000", False)
    }
    REDUCER = dict_reducer
    MODULE = get_module(__name__)

    @property
    def _get_disc_percentage(self):
        if float(self._get_regular_price):
            return (float(self._get_regular_price) - float(self._get_disc_price)) / float(self._get_regular_price)
        else:
            return 0.0

    @property
    def _get_disc_price(self):
        return self.instance['product_price']

    @property
    def _get_regular_price(self):
        return float(self.instance['product_price']) + float(self.instance['discount'])
