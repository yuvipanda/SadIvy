#!/usr/bin/env python
from amqplib import client_0_8 as amqp
import simplejson as json
import gammu


conn = amqp.Connection(hostname="localhost:5672",        
                       virtual_host="/", insist=False)

chan = conn.channel()
chan.queue_declare(queue="smses", durable=True, exclusive=False, auto_delete=False)
chan.exchange_declare(exchange="smses", type="direct", durable=True, auto_delete=False)
chan.queue_bind(queue="smses", exchange="smses", routing_key="sms")

def send_sms(msg):
    data = json.loads(msg.body)
    data['SMSC'] = {'Location': 1}
    chan.basic_ack(msg.delivery_tag)
    print data

chan.basic_consume(queue="smses",callback=send_sms, consumer_tag="smstag")

while True:
    chan.wait()

chan.basic_cancel("smstag")

chan.close()
conn.close()
