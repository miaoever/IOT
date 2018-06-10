#!/usr/bin/python2.7
from models import Orders
from time import gmtime, strftime


class Order:
    def __init__(self):
        pass

    def getNextOrder(self, order_id):
        query = Orders.select().where(Orders.id == order_id)
        order_item = []
        try:
            order = query.where(Orders.id == order_id).get()
            order_ori = [order.black, order.blue, order.green, order.yellow, order.red, order.white]
            for i in order_ori:
                if i is None:
                    order_item.append(0)
                else:
                    order_item.append(i)

            if order.fill is False:
                order_status = 1  # order is not fulfilled
            else:
                order_status = 2   # order is fulfilled
        except Orders.DoesNotExist:
            order_status = 0  # no recorde
        print {"order_status": order_status, "order_item": order_item}

    def markOrderFill(self, order_id):
        query = Orders.select().where(Orders.id == order_id)
        if query.exists():
            current_time = strftime("%Y-%m-%d %H:%M:%S", gmtime())
            Orders.update(fill=True, filldate=current_time).where(Orders.id == order_id).execute()
            return  True
        else:
            return False


o = Order()
o.getNextOrder(8)
o.getNextOrder(9)
o.getNextOrder(10)