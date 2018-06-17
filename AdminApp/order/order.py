#!/usr/bin/python2.7
from models import Orders_APP
from time import localtime, strftime
import requests
import json


class Order:

    def __init__(self):
        pass

    def getLastFilledOrderID(self):
        # api-endpoint
        URL = "http://128.237.129.43:3000/api/getLastFilledOrderID"

        # sending get request and saving the response as response object
        r = requests.get(url=URL)

        try:
            r.raise_for_status()
        except requests.exceptions.HTTPError as err:
            return None

        # extracting data in json format
        data = r.json()

        result = data['Orders']

        if len(result) != 1:
            return 0
        else:
            orderID = result[0]['id']
            return orderID

    def getOrder(self, orderID):
        # api-endpoint
        URL = "http://128.237.129.43:3000/api/getOrderByID"

        body = {'orderID': orderID}
        current_time = strftime("%Y-%m-%d %H:%M:%S", localtime())
        r = requests.post(url=URL, data=body)

        try:
            r.raise_for_status()
        except requests.exceptions.HTTPError as err:
            return None

        data = r.json()
        if len(data['Orders']) != 1:
            return None
        else:
            order = data['Orders'][0]
            result = []
            order_item = [order.get('black'), order.get('blue'), order.get('green'), order.get('yellow'),
                          order.get('red'), order.get('white')]
            for i in order_item:
                if i is None:
                    result.append(0)
                else:
                    result.append(i)
            self.updateTokenStatus(order.get('id'), current_time)
            return result


    def updateTokenStatus(self, orderID, tokenDate):
        # api-endpoint
        URL = 'http://128.237.129.43:3000/api/updateTokenStatus'

        body = {'orderID': orderID, 'tokenDate': tokenDate}

        r = requests.post(url=URL, data=body)

        try:
            r.raise_for_status()
        except requests.exceptions.HTTPError as err:
            return None

        data = r.json()
        affected_row = data['Orders']['affectedRows']
        if affected_row != 1:
            return False
        else:
            return True

    def updateShipStatus(self, orderID):
        # api-endpoint
        URL = 'http://128.237.129.43:3000/api/updateShipStatus'

        current_time = strftime("%Y-%m-%d %H:%M:%S", localtime())

        # request body
        body = {'orderID': orderID, 'shipDate': current_time}

        # sending get request and saving the response as response object
        r = requests.post(url=URL, data=body)

        data = r.json()
        affected_row = data['Orders']['affectedRows']
        if affected_row != 1:
            return False
        else:
            return True

    def carArriveAtReceiving(self, carID):
        current_time = strftime("%Y-%m-%d %H:%M:%S", localtime())
        record_id = Orders_APP.insert(carid=carID, arriveAtReceiving=current_time).execute()
        return record_id


    def loadedInventoryWithRecordID(self, recordID, orderID, inventory):
        current_time = strftime("%Y-%m-%d %H:%M:%S", localtime())
        query = Orders_APP.select().where(Orders_APP.id == recordID)
        if query.exists():
            Orders_APP.update(orderid=orderID, black=inventory[0], blue=inventory[1], green=inventory[2], yellow=inventory[3],
                                red=inventory[4], white=inventory[5], loadedDate=current_time).where(Orders_APP.id == recordID).execute()
            print True
        else:
            print False


    def carArriveAtShipping(self, records):
        current_time = strftime("%Y-%m-%d %H:%M:%S", localtime())
        length = len(recordID)
        count = 0
        for r in records:
            query = Orders_APP.select().where(Orders_APP.id == r)
            if query.exists():
                Orders_APP.update(arriveAtShipping=current_time).where(Orders_APP.id == r).execute()
                count += 1
        if count == length:
            return True
        else:
            return False


    def unloadedInventoryWithRecordID(self, records):
        current_time = strftime("%Y-%m-%d %H:%M:%S", localtime())
        length = len(recordID)
        count = 0
        for r in records:
            query = Orders_APP.select().where(Orders_APP.id == r)
            if query.exists():
                Orders_APP.update(unloadedDate=current_time).where(Orders_APP.id == r).execute()
                count += 1
        if count == length:
            return True
        else:
            return False
