from peewee import *
import datetime

mysql_db = MySQLDatabase('ws_orderinfo', user='noosa', password='IOTnoosa',
                         host='mysql-iot.c5ww1oozzb84.us-east-1.rds.amazonaws.com', port=3306)

class BaseModel(Model):
    class Meta:
        database = mysql_db

class Orders(BaseModel):
    customer = CharField(max_length=30)
    red = IntegerField(default=None, null=True)
    blue = IntegerField(default=None, null=True)
    green = IntegerField(default=None, null=True)
    yellow = IntegerField(default=None, null=True)
    black = IntegerField(default=None, null=True)
    white = IntegerField(default=None, null=True)
    pending = BooleanField(default=None, null=True)
    orderdate = DateTimeField(default=datetime.datetime.now)
    fill = BooleanField(default=False, null=True)
    filldate = DateTimeField(default='0000-00-00 00:00:00')


#mysql_db.create_tables([Orders])
# time = datetime.datetime.now
# print time
