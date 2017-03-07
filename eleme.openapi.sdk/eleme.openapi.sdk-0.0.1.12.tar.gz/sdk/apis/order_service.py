# -*- coding: utf-8 -*-


class OrderService:

    __client = None

    def __init__(self, client):
        self.__client = client

    def get_order(self, order_id):
        return self.__client.call("eleme.order.getOrder", {"orderId": order_id})

    def mget_orders(self, order_ids):
        return self.__client.call("eleme.order.mgetOrders", {"orderIds": order_ids})

    def confirm_order(self, order_id):
        return self.__client.call("eleme.order.confirmOrder", {"orderId": order_id})

    def cancel_order(self, order_id, type, remark):
        return self.__client.call("eleme.order.cancelOrder", {"orderId": order_id, "type": type, "remark": remark})

    def agree_refund(self, order_id):
        return self.__client.call("eleme.order.agreeRefund", {"orderId": order_id})

    def disagree_refund(self, order_id, reason):
        return self.__client.call("eleme.order.disagreeRefund", {"orderId": order_id, "reason": reason})

