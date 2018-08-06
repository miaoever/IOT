import os
content = ""
content = content + "\"1\n"
content = content + "2,"
content = content + "3\""

print "aws kinesis put-record --stream-name iot-robotdata-noosa --partition-key 1 --data " + content
#os.system("aws kinesis put-record --stream-name iot-robotdata-noosa --partition-key 1 --data " + content)