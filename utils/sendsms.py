#!/usr/bin/env python
from amqplib import client_0_8 as amqp
import simplejson as json

import sys

conn = amqp.Connection(hostname="localhost:5672",
                       virtual_host="/", insist=False)

chan = conn.channel()

data = {'Number': sys.argv[1], 'Text': ' '.join(sys.argv[2:])}

msg = amqp.Message(json.dumps(data))
msg.properties["delivery_mode"] =  2
chan.basic_publish(msg, exchange="smses", routing_key="sms")

chan.close()
conn.close()
            
