#!/usr/bin/python2.7
from models import Orders
from time import gmtime, strftime
import requests
import json


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

    def getLastFillIndex(self):
        query = Orders.select().where(Orders.pending == False and Orders.fill == True).order_by(Orders.orderdate.desc())
        if query.exists():
            last_fill_order = query.get()
            print last_fill_order.id
        else:
            return 4

    def getNextOrderFromServer(self):
        # api-endpoint
        URL = "http://128.237.129.43:3000/api/getNextOrder"

        # sending get request and saving the response as response object
        r = requests.get(url=URL)

        # extracting data in json format
        data = r.json()

        result = data['Orders']

        if len(result) != 1:
            return {"order_status": -1, "order_item": None, "orderID": 0}
        else:
            order = result[0]
            orderID = result[0]['id']
            return {"order_status": 1, "order_item": order, "orderID": orderID}

    def updateTokenStatus(self, orderID, tokenDate):
        # api-endpoint
        URL = 'http://128.237.129.43:3000/api/updateTokenStatus'

        body = {'orderID': orderID, 'tokenDate': tokenDate}

        r = requests.post(url=URL, data=body)

        data = r.json()
        affected_row = data['Orders']['affectedRows']
        if affected_row != 1:
            return False
        else:
            return True

    def updateShipStatus(self, orderID, shipDate):
        # api-endpoint
        URL = 'http://128.237.129.43:3000/api/updateShipStatus'

        # request body
        body = {'orderID': orderID, 'shipDate': shipDate}

        # sending get request and saving the response as response object
        r = requests.post(url=URL, data=body)

        data = r.json()
        affected_row = data['Orders']['affectedRows']
        if affected_row != 1:
            return False
        else:
            return True


o = Order()
current_time = strftime("%Y-%m-%d %H:%M:%S", gmtime())
o.updateShipStatus(2, current_time)
