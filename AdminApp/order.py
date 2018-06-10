#!/usr/bin/python2.7
from models import Orders
import json


class Order:
    def __init__(self):
        pass

    def getNextOrder(self, order_id):
        query = Orders.select().where(Orders.id == order_id)
        if query.exists():
            order = Orders.get(Orders.id == order_id)
            order_item = {"id": order.id, "red": order.red, "blue": order.blue, "green": order.green,
                          "yellow": order.yellow, "black": order.black, "white": order.white}
            order_item = json.dumps(order_item)
            order_result = json.loads(order_item)
            # print order_result
            return order_result
        else:
            return None

    def markOrderFill(self, order_id):
        query = Orders.select().where(Orders.id == order_id)
        if query.exists():
            Orders.update(fill=True).where(Orders.id == order_id).execute()
            return True
        else:
            return False
