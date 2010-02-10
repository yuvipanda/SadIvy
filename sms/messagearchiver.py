import sys
from amqplib import client_0_8 as amqp
from pymongo.connection import Connection
import simplejson as json

queue = sys.argv[1]

qconn = amqp.Connection(hostname="localhost:5672", virtual_host="/", insist=False)
chan = qconn.channel()

dbconn = Connection("localhost")
db = dbconn.archive
smsarchive = db.sms

def archive_message(msg):
    data = json.loads(msg.data)
    smsarchive.insert(data)
    print "Message from %s: %s" % (data['Number'], data['Text'])

chan.basic_consume(queue=queue, callback=archive_message, consumer_tag="archivemessages")

while True:
    chan.wait()
