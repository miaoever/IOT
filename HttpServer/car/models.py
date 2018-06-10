#!/usr/bin/python2.7
from peewee import *

mysql_db = MySQLDatabase('ws_orderinfo', user='noosa', password='IOTnoosa',
                         host='mysql-iot.c5ww1oozzb84.us-east-1.rds.amazonaws.com', port=3306)

#0 - rre
#1 -rec - > shipping
#2- shiping
#3 shiping->rec

class BaseModel(Model):
    class Meta:
        database = mysql_db # this model uses the "people.db" database

class CarInfo(BaseModel):
    carId = IntegerField()
    position = IntegerField() # 0 - recieving, 1 - recieving->shipping, 2 - shipping, 3 - shipping->rec


mysql_db.create_tables([CarInfo])