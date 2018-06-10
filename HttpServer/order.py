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
            order_item = [order.black, order.blue, order.green, order.yellow, order.red, order.white]
            return [x if x else 0 for x in order_item]
        else:
            return None

    def markOrderFill(self, order_id):
        query = Orders.select().where(Orders.id == order_id)
        if query.exists():
            Orders.update(fill=True).where(Orders.id == order_id).execute()
            return True
        else:
            return False