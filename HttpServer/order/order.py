#!/usr/bin/python2.7
from models import Orders
from time import localtime, strftime
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
            current_time = strftime("%Y-%m-%d %H:%M:%S", localtime())
            Orders.update(fill=True, filldate=current_time, pending=False).where(Orders.id == order_id).execute()
            return  True
        else:
            return False

    def getLastFulfilledOrderId(self):
        query = Orders.select().where(Orders.pending == False and Orders.fill == True).order_by(Orders.id.desc())
        if query.exists():
            last_fill_order = query.get()
            return last_fill_order.id
        else:
            return 4