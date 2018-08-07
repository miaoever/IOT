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
    redBackUp = IntegerField(default=0, null=True)
    blueBackUp = IntegerField(default=0, null=True)
    greenBackUp = IntegerField(default=0, null=True)
    yellowBackUp = IntegerField(default=0, null=True)
    blackBackUp = IntegerField(default=0, null=True)
    whiteBackUp = IntegerField(default=0, null=True)
    redUsed = IntegerField(default=0, null=True)
    blueUsed = IntegerField(default=0, null=True)
    greenUsed = IntegerField(default=0, null=True)
    yellowUsed = IntegerField(default=0, null=True)
    blackUsed = IntegerField(default=0, null=True)
    whiteUsed = IntegerField(default=0, null=True)

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
    roundid = IntegerField(default=None)
    orderid = IntegerField(default=None)

class carinfo(BaseModel):
    roundid = IntegerField(default=None)
    entermain = DateTimeField(default=None)
    exitmain = DateTimeField(default=None)

class demographic(BaseModel):
    entryid = IntegerField(primary_key=True)
    name = CharField(default=None)
    age = CharField(default=None)
    sex = CharField(default=None)
    city = CharField(default=None)
    state = CharField(default=None)
    country = CharField(default=None)
    income = IntegerField(default=None)
    credit = IntegerField(default=None)
    education = CharField(default=None)
    occupation = CharField(default=None)