from copy import copy

class OrderManager(object):
    def __init__(self):
        # OrderNumber : (Black, Blue, Green, Yellow, Red, White)
        self.orders = {1:[2,0,0,0,0,0],
                       2:[0,3,0,1,0,0],
                       3:[1,4,2,0,0,0]}
        self.total = 3
        self.remaining = [0,0,0,0,0,0]
        self.completed = 0
        self.dispatching = 0
        self.cars = {4:Car(4,0),12:Car(12,3)}
    def simulate(self):
        self.cars[4].simulate()
        self.cars[12].simulate()
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
        count = 6
        while count>0:
            if self.remaining==[0,0,0,0,0,0]:
                if self.dispatching<self.total:
                    self.dispatching+=1
                    self.remaining=self.orders[self.dispatching]
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
        self.cars[loading_car].is_loaded = True
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
    def get_unload_instruction(self):
        if self.cars[4].location==2:
            return cars[4].get_unload_instruction()
        elif self.cars[12].location==2:
            return self.cars[12].get_unload_instruction()
        return "Please wait until the next car arrives at the shipping station."
    def finish_unload_instruction(self):
        unloading_car = None
        if cars[4].location==2:
            unloading_car = 4
        elif cars[12].location==2:
            unloading_car = 12
        if not unloading_car:
            print "You can't finish shipping instruction if there's no car at shipping."
            return
        order, fulfilled = None, False
        order, fulfiflled = cars[unloading_car].complete_unload_instruction()
        if fulfilled:
            self.fulfill_order(order)

class Car(object):
    def __init__(self, id, loc=-1):
        self.id = id
        self.inventory = {}
        self.orders = {} # order numer : last portion here?
        self.in_service = True
        self.location = loc # -1: Unknown, 0: receiving, 1: receiving -> shipping, 2: shipping, 3: shipping -> receiving
        self.current_order = None
        self.loading_msg = None
        self.unload_msg = None
        self.is_loaded = False
    def unload_all(self):
        self.inventory={}
        self.orders={}
        self.current_order=None
    def load(self, order, items, is_last_portion):
        self.inventory[order] = copy(items)
        self.orders[order]=is_last_portion
    def simulate(self):
        if self.location == 0 and self.is_loaded:
            self.location == 2
        elif self.location == 2 and self.orders=={}:
            self.location == 0
            self.unload_all
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
            self.loading_msg = "Nothing to load for now. Please wait."
        else:
            self.loading_msg = "Please load "+get_string(load_items)
        return self.loading_msg
    def complete_loading_instruction(self):
        self.loading_msg = None
    def get_unload_instruction(self):
        if self.unload_msg:
            return self.unload_msg
        if len(self.orders)==0:
            self.unload_msg = "No items to unload from this car. Please wait."
            return self.unload_msg
        if not self.current_order:
            self.current_order = min(self.orders.keys())
        items = self.inventory[self.current_order]
        last_portion = self.orders[self.current_order]
        instruction = "Please unload "+get_string(items)+"for order #"+str(self.current_order)+"<br/>"
        instruction2 = ""
        if last_portion:
            instruction2 = "All items for this order are here. You may ship now."
        else:
            instruction2 = "More items for this order are on the way."
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

colors = ["Black","Blue","Green","Yellow","Red","White"]
def get_string(items):
    s = []    
    for i in range(6):
        s.append(str(items[i])+" "+colors[i])
    return " ".join(s)