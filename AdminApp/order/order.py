#!/usr/bin/python2.7
from models import Orders_APP, Orders_Server, orderInRound,demographic,carinfo
from time import localtime, strftime
import requests
import json
from datetime import timedelta
import datetime
import os
import math


class Order:
    remaining = 0
    start_bucket = "iot-robotdata-noosa"
    finish_bucket = "iot-robotdata-finish"
    # header_start = "\"orderid,black,blue,green,yellow,red,white,amount,split\n"
    # header_finish = "\"orderid,age,sex,state,education,transitDuration,fulfillDuration,black,blue,green,yellow,red,white,amount\n"

    url= "http://128.237.186.90:3000/api/"

    def __init__(self):
        pass

    def getLastFilledOrderID(self):
        # api-endpoint
        URL = self.url + "getLastFilledOrderID"

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
        URL = self.url + "getOrderByID"
        content = ""
        body = {'orderID': orderID}
        current_time = strftime("%Y-%m-%d %H:%M:%S", localtime())
        r = requests.post(url=URL, data=body)

        try:
            r.raise_for_status()
        except requests.exceptions.HTTPError as err:
            return None

        data = r.json()
        if len(data['Orders']) != 1:
            print "The order number is " + str(len(data['Orders'])) + "\n"
            print "There is nothing to send."
            return None
        else:
            order = data['Orders'][0]
            result = []
            orderSum = 0
            content = content + "\"" + str(orderID) + ","
            order_item = [order.get('black'), order.get('blue'), order.get('green'), order.get('yellow'),
                          order.get('red'), order.get('white')]
            for i in order_item:
                if i is None:
                    result.append(0)
                    content = content + "0,"
                else:
                    result.append(i)
                    orderSum = orderSum + i
                    content = content + str(i) + ","

            content = content + str(orderSum) + ","

            # update token status in database
            # self.updateTokenStatus(order.get('id'), current_time)

            # count splits
            split = 0
            if self.remaining != 0:
              split = split + 1
              if orderSum >= self.remaining:
                orderSum = orderSum - self.remaining
                self.remaining = 0
              else:
                self.remaining = self.remaining - orderSum
                orderSum = 0
        
            if self.remaining == 0 and orderSum != 0:
              split = split + math.ceil(orderSum/24.0)
              self.remaining = 24 - orderSum%24
            
            content = content + str(int(split))+"\n\""
            if content != "":
              print "Contents: " + content
              os.system("aws kinesis put-record --stream-name \"iot-robotdata-noosa\" --partition-key 1 --data " + content)
              start_file_path = "\"data/ingest/" + str((datetime.datetime.now() + datetime.timedelta(hours=4)).strftime("%Y/%m/%d/%H/")) + "\""
              print "spark-submit entry.py 1 "+ self.start_bucket + " " + start_file_path
              # os.system("spark-submit entry.py 1 "+ self.start_bucket + " " + start_file_path)
            else:
                print "There is nothing to send."
            return result



    def updateTokenStatus(self, orderID, tokenDate):
        # api-endpoint
        URL = self.url + "updateTokenStatus"

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
        URL = self.url + "updateShipStatus"

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
        content = ""
        if query.exists():
            print "Exist round"
            # Orders_APP.update(unloadedDate=current_time).where(Orders_APP.id == recordID).execute()
            content = "\""
            for order in orders:
              query_order = Orders_Server.select().where(Orders_Server.id==order)
              if query_order.exists():
                print "Exist order " + str(order)
                # update order in round table
                orderInRound.insert(roundid=recordID, orderid=order).execute()

                # pass required data to kinesis
                order_info = Orders_Server.get(Orders_Server.id==order)
                query_customer = demographic.select().where(demographic.name == order_info.customer)
                if query_customer.exists():
                    print "customer round"
                    customer_info = demographic.get(demographic.name == order_info.customer)
                    content = content + str(order_info.id) + ","
                    content = content+str(customer_info.age)+","+str(customer_info.sex)+","+str(customer_info.state)+","+str(customer_info.education)+","

                    transitDuration = (order_info.shipDate-order_info.tokenDate).total_seconds()
                    fulfillDuration = (order_info.shipDate-(order_info.orderDate - datetime.timedelta(hours=4))).total_seconds()

                    content = content+str(transitDuration)+","+str(fulfillDuration)+","
                    content = content+str(order_info.black)+","+str(order_info.blue)+","+str(order_info.green)+","+str(order_info.yellow)+","+str(order_info.red)+","+str(order_info.white)+","
                    amount = order_info.black + order_info.blue + order_info.green + order_info.yellow +order_info.red + order_info.white
                    content = content + str(amount)+"\n"
            content = content + "\""
            print content
            if content != "" and content != "\"\"":
                os.system("aws kinesis put-record --stream-name \"iot-robotdata-finish\" --partition-key 1 --data " + content)
                finish_file_path = "\"data/ingest/" + str((datetime.datetime.now() + datetime.timedelta(hours=4)).strftime("%Y/%m/%d/%H/")) + "\""
                print "spark-submit entry.py 2 "+ self.finish_bucket + " " + finish_file_path
                # os.system("spark-submit entry.py 2 "+ self.finish_bucket + " " + finish_file_path)
            else:
                print "There is nothing to upload"
            return True
        else:
            return False


    def useBackUp(self, roundID, used):
        query = Orders_APP.select().where(Orders_APP.id == roundID)
        if query.exists():
            original = Orders_APP.get(Orders_APP.id == roundID)
            Orders_APP.update(blackUsed=used[0]+original.blackUsed, blueUsed=used[1]+original.blueUsed, greenUsed=used[2]+original.greenUsed, yellowUsed=used[3]+original.yellowUsed,
                              redUsed=used[4]+original.redUsed, whiteUsed=used[5]+original.whiteUsed).where(Orders_APP.id == roundID).execute()
            return True
        else:
            return False


    def carEnterMain(self, roundID):
        record_id = []
        current_time = strftime("%Y-%m-%d %H:%M:%S", localtime())
        for rid in roundID:
          recorid = carinfo.insert(roundid=rid, entermain=current_time).execute()
          record_id.append(recorid)
        return record_id


    def carExistMain(self, recordID):
        current_time = strftime("%Y-%m-%d %H:%M:%S", localtime())
        for rid in recordID:
          query = carinfo.select().where(carinfo.id == rid)
          if query.exists():
              carinfo.update(existmain=current_time).where(carinfo.id == rid).execute()
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
                    print r.get('unloadedDate')
                    print r.get('arriveAtShipping')
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

        #print logo
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
o.getOrder(1)
o.unloadedInventoryWithRecordID(1, [2])
# o.useBackUp(1, [2,2,2,1,4,1])

