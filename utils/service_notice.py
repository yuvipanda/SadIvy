#!/usr/bin/env python
import sys
import atexit
from amqplib import client_0_8 as amqp
from pymongo.connection import Connection
import simplejson as json

conn = amqp.Connection(hostname="localhost:5672",
                       virtual_host="/", insist=False)

chan = conn.channel()

dbconn = Connection("localhost")
db = dbconn.twitter
users = db.users

message = ' '.join(sys.argv[1:])

for u in users.find():    
    data = {'Number': u['Number'], 'Text': message}
    msg = amqp.Message(json.dumps(data))
    msg.properties["delivery_mode"] =  2
    chan.basic_publish(msg, exchange="smses", routing_key="sms")
    print "Sent %s" % data['Number']

    
@atexit.register
def cleanup():
    chan.close()
    conn.close()
            
