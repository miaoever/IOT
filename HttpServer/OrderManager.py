from copy import copy
#from Console import Console
from order.order import Order
from car.carMrg import CarMrg
import datetime
import time
import threading

class OrderManager(object):
    
    def __init__(self):
        # OrderNumber : (Black, Blue, Green, Yellow, Red, White)
        self.order_api = Order()
        self.orders = {}
        self.dispatching = self.order_api.getLastFilledOrderID()
        if self.dispatching is None:
            throw("Error getting last filled order.")
        print "Retrieved last fulfilled order #"+str(self.dispatching)
        self.total = self.dispatching
        self.remaining = [0,0,0,0,0,0]
        self.completed = self.dispatching
        self.maintenance = True
        self.cars = {4:Car(4,-1,self),12:Car(12,-1,self)}
        self.serial = None
    
    def force_car_location(self, car, loc):
        self.cars[car].location = loc
        if loc==0:
            self.order_api.carArriveAtReceiving(car)
        elif loc==2 and self.cars[car].record_id!=None:
            self.order_api.carArriveAtShipping(self.cars[car].record_id)

    def setSerial(self, serial):
        self.serial = serial

    def set_car_location(self, car, loc):
        self.cars[car].set_location(loc)

    def enter_maintenance(self):
        self.maintenance = True
        self.serial.enterMaintenance()
        for car in self.cars:
            self.cars[car].enter_maintenance()

    def exit_maintenance(self):
        self.maintenance = False
        self.serial.exitMaintenance()
        for car in self.cars:
            self.cars[car].exit_maintenance()

    def get_loading_instruction(self):
        loading_car = None
        if self.cars[4].location==0:
            loading_car = 4
        elif self.cars[12].location==0:
            loading_car = 12
        if not loading_car:
            return "Please wait until the next car arrives at the receiving station."
        if self.cars[loading_car].is_loaded:
            return "You have loaded the current car. Please wait for the next car."
        if self.cars[loading_car].inventory!={}:
            return self.cars[loading_car].get_loading_instruction()
        count = 24
        while count>0:
            if self.remaining==[0,0,0,0,0,0]:
                if self.dispatching<self.total:
                    self.dispatching+=1
                    self.remaining=self.orders[self.dispatching]
                else:
                    print "Getting next order"
                    next_order = self.order_api.getOrder(self.total+1)
                    if next_order:
                        #print next_order
                        self.total+=1
                        self.orders[self.total]=next_order
                        continue
                    else:
                        break
            load_items, fulfilled, count = self.get_load_helper(count, self.remaining)
            self.cars[loading_car].load(self.dispatching,load_items,fulfilled)
        return self.cars[loading_car].get_loading_instruction()
    def finish_loading_instruction(self):
        loading_car = None
        if self.cars[4].location==0:
            loading_car = 4
        elif self.cars[12].location==0:
            loading_car = 12
        if len(self.cars[loading_car].inventory)>0:
            self.cars[loading_car].is_loaded = True
        if self.cars[loading_car].simulate():
            print "Let car #"+str(loading_car)+" go."
            self.serial.carMove(loading_car)
    def get_load_helper(self, count, items):
        load_items = [0,0,0,0,0,0]
        for i in range(6):
            if items[i]<=count:
                load_items[i]=items[i]
                items[i]=0
                count-=load_items[i]
            else:
                load_items[i]=count
                items[i]-=count
                count = 0
                return (load_items, False, 0)
        return (load_items, True, count)
    def fulfill_order(self, order):
        if order!=self.completed+1:
            print "Order not fulfilled in order!"
        else:
            self.completed+=1
            print "Order #" + str(self.completed) + " is fulfilled."
            self.order_api.updateShipStatus(self.completed)
    def get_unload_instruction(self):
        if self.cars[4].location==2:
            return self.cars[4].get_unload_instruction()
        elif self.cars[12].location==2:
            return self.cars[12].get_unload_instruction()
        return "Please wait until the next car arrives at the shipping station."
    def finish_unload_instruction(self):
        unloading_car = None
        if self.cars[4].location==2:
            unloading_car = 4
        elif self.cars[12].location==2:
            unloading_car = 12
        if not unloading_car:
            print "You can't finish shipping instruction if there's no car at shipping."
            return
        order, fulfilled = None, False
        order, fulfilled = self.cars[unloading_car].complete_unload_instruction()
        if fulfilled:
            self.fulfill_order(order)
        if self.cars[unloading_car].simulate():
            print "Let car #"+str(unloading_car)+" go."
            self.serial.carMove(unloading_car)
class Car(object):
    def __init__(self, id, loc, order_manager):
        self.id = id
        self.inventory = {}
        self.orders = {} # order numer : last portion here?
        self.in_service = 0 # 0: Maintenance, 1: In service, -1: Out of service
        self.location = loc # -1: Unknown, 0: receiving, 1: receiving -> shipping, 2: shipping, 3: shipping -> receiving
        self.current_order = None
        self.loading_msg = None
        self.unload_msg = None
        self.is_loaded = False
        self.record_id = None
        self.total_inventory = [0,0,0,0,0,0]
        self.order_manager = order_manager
    def unload_all(self):
        self.inventory={}
        self.orders={}
        self.current_order=None
        self.is_loaded=False
        self.loading_msg=None
        self.unload_msg=None
        self.record_id=None
        self.total_inventory=[0,0,0,0,0,0]
    def load(self, order, items, is_last_portion):
        self.inventory[order] = copy(items)
        for i in range(6):
            self.total_inventory[i]+=items[i]
        self.orders[order]=is_last_portion
    def simulate(self):
        if self.location == 0 and self.is_loaded:
            self.location = 1
            self.order_manager.order_api.loadedInventoryWithRecordID(self.record_id, self.total_inventory)
            return True
        elif self.location == 2 and self.orders=={}:
            if self.record_id!=None:
                self.order_manager.order_api.unloadedInventoryWithRecordID(self.record_id)
            self.unload_all()
            self.location = 3
            return True
        else:
            return False
    def set_location(self, loc):
        if self.location==1 and loc==0:
            print "Unexpected location - Check car #"+str(self.id)
            self.location=-1
        elif self.location==3 and loc==2:
            print "Unexpected location - Check car #"+str(self.id)
            self.location=-1
        else:
            self.location=loc
            if loc==0:
                self.record_id = self.order_manager.order_api.carArriveAtReceiving(self.id)
            elif loc==2 and self.record_id!=None:
                self.order_manager.order_api.carArriveAtShipping(self.record_id)
    def enter_maintenance(self):
        if self.in_service==1:
            self.in_service = 0
    def exit_maintenance(self):
        if self.in_service==0:
            self.in_service=1
    def get_service(self):
        if self.in_service==-1:
            return "Out of service"
        if self.in_service==0:
            return "Maintenance Mode"
        if self.in_service==1:
            return "In service"
        return "Error"
    def get_location(self):
        if self.location == -1:
            return "Unknown"
        if self.location == 0:
            return "At Receiving"
        if self.location == 1:
            return "Receiving --> Shipping"
        if self.location == 2:
            return "At Shipping"
        if self.location == 3:
            return "Shipping --> Receiving"
        return "Error"
    def get_backup(self):
        if (0 in self.inventory):
            return self.inventory[0]
        else:
            return None
    def use_backup(self, order, items):
        self.inventory[order]=items
        for i in range(6):
            self.inventory[0][i]-=items[i]
    def get_loading_instruction(self):
        if self.loading_msg:
            return self.loading_msg
        load_items = [0,0,0,0,0,0]
        for items in self.inventory.values():
            for i in range(6):
                load_items[i]+=items[i]
        if load_items == [0,0,0,0,0,0]:
            return "Nothing to load for now. Please wait."
        else:
            self.loading_msg = "Please load "+get_string(load_items)+" on car #"+str(self.id)
        return self.loading_msg
    def complete_loading_instruction(self):
        self.loading_msg = None
    def get_unload_instruction(self):
        #print self.inventory
        #print self.orders
        #print self.current_order
        if self.unload_msg:
            return self.unload_msg
        if len(self.orders)==0:
            return "No items to unload from this car. Please wait."
        if not self.current_order:
            self.current_order = min(self.orders.keys())
        items = self.inventory[self.current_order]
        last_portion = self.orders[self.current_order]
        instruction = "Please unload "+get_string(items)+" for order #"+str(self.current_order)+" from car #"+str(self.id)+"<br/>"
        instruction2 = ""
        if last_portion:
            instruction2 = "All items for this order are here. You may ship this order now."
        else:
            instruction2 = "More items for this order are on the way. Please hold this package."
        self.unload_msg = instruction+instruction2
        return self.unload_msg
    def complete_unload_instruction(self):
        if self.current_order==None:
            return None, False
        self.unload_msg = None
        del(self.inventory[self.current_order])
        fulfilled = self.orders[self.current_order]
        del(self.orders[self.current_order])
        last_order = self.current_order
        self.current_order = None
        return last_order, fulfilled
    def get_inventory(self):
        if not self.is_loaded and self.location==0:
            return "Loading in progress..."
        inv = []
        for order in self.orders:
            inv.append("Order #"+str(order)+": "+get_string(self.inventory[order]))
        if -1 in self.inventory:
            inv.append("Backup: "+get_string(self.inventory[-1]))
        return "<br>".join(inv)

colors = ["Black","Blue","Green","Yellow","Red","White"]
def get_string(items):
    s = []    
    for i in range(6):
        if items[i]>0:
            s.append(str(items[i])+" "+colors[i])
    return " ".join(s)


def get_timestamp():
        ts = time.time()
        st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        return st+" "