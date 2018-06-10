#!/usr/bin/python2.7
from models import CarInfo

class CarMrg:

    def __init__(self):
        pass

    def setCarPosition(self, id, position):
        CarInfo.insert(id=id, position=position).execute()

    def getCarPosition(self, id):
        return CarInfo.select("position").where("carId" == id).order_by(CarInfo.get_id.desc())
        #return CarInfo.raw('SELECT position FROM CarInfo WHERE carId = ' + str(id) + ' AND id = (select max(id) from CarInfo group by id)')[0]

    def move(self, id):
        pass
    
    def stop(self, id):
        pass
        

    


