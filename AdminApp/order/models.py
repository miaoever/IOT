from peewee import *
import datetime

mysql_db = MySQLDatabase('ws_orderinfo', user='noosa', password='IOTnoosa',
                         host='mysql-iot.c5ww1oozzb84.us-east-1.rds.amazonaws.com', port=3306)

class BaseModel(Model):
    class Meta:
        database = mysql_db

class Orders_APP(BaseModel):
    carid = IntegerField(null=True)
    red = IntegerField(default=None, null=True)
    blue = IntegerField(default=None, null=True)
    green = IntegerField(default=None, null=True)
    yellow = IntegerField(default=None, null=True)
    black = IntegerField(default=None, null=True)
    white = IntegerField(default=None, null=True)
    arriveAtReceiving = DateTimeField(default=None)
    loadedDate = DateTimeField(default=None)
    arriveAtShipping = DateTimeField(default=None)
    unloadedDate = DateTimeField(default=None)

class Orders_Server(BaseModel):
    customer = CharField()
    red = IntegerField(default=None, null=True)
    blue = IntegerField(default=None, null=True)
    green = IntegerField(default=None, null=True)
    yellow = IntegerField(default=None, null=True)
    black = IntegerField(default=None, null=True)
    white = IntegerField(default=None, null=True)
    pending = BooleanField()
    orderDate = DateTimeField(default=None)
    tokenDate = DateTimeField(default=None)
    shipDate = DateTimeField(default=None)
    shipped = BooleanField()

class orderInRound(BaseModel):
    roundid = IntegerField(default=None, null=True)
    orderid = IntegerField(default=None, null=True)


