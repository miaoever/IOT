#!/usr/bin/python2.7
from models import Orders_APP, Orders_Server, orderInRound, carinfo
from time import localtime, strftime
import requests
import json
from datetime import timedelta

host_ip = 'http://128.237.205.154:3000'

class Order:
    def __init__(self):
        pass

    def getLastFilledOrderID(self):
        # api-endpoint
        URL = host_ip+"/api/getLastFilledOrderID"

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
        URL = host_ip+"/api/getOrderByID"

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
        URL = host_ip+'/api/updateTokenStatus'

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
        URL = host_ip+'/api/updateShipStatus'

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

    def loadedInventoryWithRecordID(self, recordID, inventory, backup):
        current_time = strftime("%Y-%m-%d %H:%M:%S", localtime())
        query = Orders_APP.select().where(Orders_APP.id == recordID)
        if query.exists():
            Orders_APP.update(black=inventory[0], blue=inventory[1], green=inventory[2], yellow=inventory[3],
                              red=inventory[4], white=inventory[5],
                              loadedDate=current_time,
                              blackBackUp=backup[0], blueBackUp=backup[1], greenBackUp=backup[2], yellowBackUp=backup[3],
                              redBackUp=backup[4], whiteBackUp=backup[5]).where(Orders_APP.id == recordID).execute()
            return True
        else:
            return False

    def useBackUpWithRecordID(self, roundID, used):
        query = Orders_APP.select().where(Orders_APP.id == roundID)
        if query.exists():
            original = Orders_APP.get(Orders_APP.id == roundID)
            Orders_APP.update(blackUsed=used[0]+original.blackUsed, blueUsed=used[1]+original.blueUsed, greenUsed=used[2]+original.greenUsed, yellowUsed=used[3]+original.yellowUsed,
                              redUsed=used[4]+original.redUsed, whiteUsed=used[5]+original.whiteUsed).where(Orders_APP.id == roundID).execute()
            return True
        else:
            return False

    def carArriveAtShipping(self, recordID):
        current_time = strftime("%Y-%m-%d %H:%M:%S", localtime())
        query = Orders_APP.select().where(Orders_APP.id == recordID)
        if query.exists():
            Orders_APP.update(arriveAtShipping=current_time).where(Orders_APP.id == recordID).execute()
            return True
        else:
            return False

    def unloadedInventoryWithRecordID(self, recordID, orders):
        current_time = strftime("%Y-%m-%d %H:%M:%S", localtime())
        query = Orders_APP.select().where(Orders_APP.id == recordID)
        if query.exists():
            Orders_APP.update(unloadedDate=current_time).where(Orders_APP.id == recordID).execute()
            for order in orders:
              orderInRound.insert(roundid=recordID, orderid=order).execute()
            return True
        else:
            return False

    def carEnterMain(self, roundID):
        print roundID
        record_id = []
        current_time = strftime("%Y-%m-%d %H:%M:%S", localtime())
        for rid in roundID:
          recorid = carinfo.insert(roundid=rid, entermain=current_time).execute()
          record_id.append(recorid)
        return record_id


    def carExitMain(self, recordID):
        current_time = strftime("%Y-%m-%d %H:%M:%S", localtime())
        for rid in recordID:
          query = carinfo.select().where(carinfo.id == rid)
          if query.exists():
              carinfo.update(exitmain=current_time).where(carinfo.id == rid).execute()
              return True
          else:
              return False



    def dataCollection(self):
        query = Orders_APP.select(Orders_APP.carid, Orders_APP.arriveAtReceiving, Orders_APP.loadedDate, Orders_APP.unloadedDate, Orders_APP.arriveAtShipping)
        car4Info = []
        car12Info = []
        queryList = []
        if query.exists:
            queryResults = query.dicts()
            for r in queryResults:
                if not r.get('arriveAtReceiving') is None and not r.get('arriveAtShipping') is None and not r.get('loadedDate') is None and not r.get('unloadedDate') is None:
                    queryList.append(r)
            for r in queryList:
                if r.get('carid') == 4:
                    loadInventoryTime = r.get('loadedDate') - r.get('arriveAtReceiving')
                    unloadInventoryTime = r.get('unloadedDate') - r.get('arriveAtShipping')
                    fromReceivingToShippingTime = r.get('arriveAtShipping') - r.get('loadedDate')
                    currentIndex = queryList.index(r)
                    previousIndex = currentIndex - 2
                    if previousIndex >= 0:
                        fromShippingToReceivingTime = r.get('arriveAtReceiving') - queryList[
                            previousIndex].get('unloadedDate')
                    else:
                        fromShippingToReceivingTime = timedelta(seconds=0)
                    carRecord = {'loadInventoryTime': loadInventoryTime, 'unloadInventoryTime': unloadInventoryTime,
                                 'fromReceivingToShippingTime': fromReceivingToShippingTime,
                                 'fromShippingToReceivingTime': fromShippingToReceivingTime}
                    car4Info.append(carRecord)
                else:
                    loadInventoryTime = r.get('loadedDate') - r.get('arriveAtReceiving')
                    unloadInventoryTime = r.get('unloadedDate') - r.get('arriveAtShipping')
                    fromReceivingToShippingTime = r.get('arriveAtShipping') - r.get('loadedDate')
                    currentIndex = queryList.index(r)
                    previousIndex = currentIndex - 2
                    if previousIndex >= 0:
                        fromShippingToReceivingTime = r.get('arriveAtReceiving') - queryList[
                            previousIndex].get('unloadedDate')
                    else:
                        fromShippingToReceivingTime = timedelta(seconds=0)
                    carRecord = {'loadInventoryTime': loadInventoryTime, 'unloadInventoryTime': unloadInventoryTime,
                                 'fromReceivingToShippingTime': fromReceivingToShippingTime,
                                 'fromShippingToReceivingTime': fromShippingToReceivingTime}
                    car12Info.append(carRecord)
        sumLoadTime = self.mySum([f["loadInventoryTime"] for f in car4Info]) + self.mySum([f["loadInventoryTime"] for f in car12Info])
        sumUnloadTime = self.mySum(f["unloadInventoryTime"] for f in car4Info) + self.mySum([f["unloadInventoryTime"] for f in car12Info])
        averageLoadTime = sumLoadTime / (len(car4Info) + len(car12Info))
        averageUnloadTime = sumUnloadTime / (len(car4Info) + len(car12Info))
        car4AverageTime = self.mySum([f["fromReceivingToShippingTime"] for f in car4Info]) / len(car4Info)
        car4ShipReceive = self.mySum([f['fromShippingToReceivingTime'] for f in car4Info]) / len(car4Info)
        car12AverageTime = self.mySum([f["fromReceivingToShippingTime"] for f in car12Info]) / len(car12Info)
        car12ShipReceive = self.mySum([f['fromShippingToReceivingTime'] for f in car12Info]) / len(car12Info)


        orderQuery = Orders_Server.select(Orders_Server.id, Orders_Server.tokenDate, Orders_Server.shipDate).where(Orders_Server.pending == False)
        orderRecords = []
        if orderQuery.exists:
            orderResults = orderQuery.dicts()
            for o in orderResults:
                orderShipTime = o.get('shipDate') - o.get('tokenDate')
                orderItem = {"id": o.get('id'), "orderShipTime": orderShipTime}
                orderRecords.append(orderItem)

        orderFulFilledNumber = len(orderRecords)
        orderFulFilledTimeSum = self.mySum([f["orderShipTime"] for f in orderRecords])
        orderFulFilledTimeAverage = orderFulFilledTimeSum / orderFulFilledNumber


        print
        print
        print "=============================================================="
        print "                            Workers                           "
        print "=============================================================="
        print "The average time for loading the inventories is " + str(averageLoadTime.seconds) + " seconds. " #+ str(averageLoadTime.microseconds) + " microseconds."
        print "The average time for unloading the inventoried is " + str(averageUnloadTime.seconds) + " seconds. " #+ str(averageUnloadTime.microseconds) + " microseconds."
        print "=============================================================="
        print "                             Cars                             "
        print "=============================================================="
        print "Car 4 :: The average time from receiving to shipping is " + str(car4AverageTime.seconds) + " seconds. " #+ str(car4AverageTime.microseconds) + " microseconds."
        print "Car 4 :: The average time from shipping to receiving is " + str(car4ShipReceive.seconds) + " seconds. "
        print "Car 12 :: The average time from receiving to shipping is " + str(car12AverageTime.seconds) + " seconds. " #+ str(car12AverageTime.microseconds) + " microseconds."
        print "Car 12 :: The average time from shipping to receiving is " + str(car12ShipReceive.seconds) + " seconds. "
        print "=============================================================="
        print "                             Orders                           "
        print "=============================================================="
        print "The total number of the fulfilled order is " + str(orderFulFilledNumber)
        print "The total time to fulfilled " + str(orderFulFilledNumber) + " orders is " + str(orderFulFilledTimeSum.seconds/60) + " minutes " + str(orderFulFilledTimeSum.seconds - orderFulFilledTimeSum.seconds/60*60) + " seconds."
        print "The average time to fulfilled " + str(orderFulFilledNumber) + " orders is " + str(orderFulFilledTimeAverage.seconds) + " seconds."
        print "============================================================"
        print "============================================================"

    def mySum(self, listofTime):
        sum = timedelta(seconds=0)
        for i in listofTime:
            sum = sum + i
        return sum

o = Order()
#o.dataCollection()

