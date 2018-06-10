#!/usr/bin/python2.7
from models import CarInfo

class CarMrg:

    def __init__(self):
        pass

    def setCarPosition(self, id, position):
        CarInfo.insert(carId=id, position=position).execute()

    def getCarPosition(self, id):
        car_item = CarInfo.select().where(CarInfo.carId == id).order_by(CarInfo.id.desc()).get()
        return car_item.position

    def move(self, id):
        pass
    
    def stop(self, id):
        pass
        
