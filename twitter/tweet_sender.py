#!/usr/bin/env python
import atexit
from amqplib import client_0_8 as amqp
import simplejson as json
import twitter
from pymongo.connection import Connection

qconn = amqp.Connection(hostname="localhost:5672",        
                        virtual_host="/", insist=False)

chan = qconn.channel()

chan.queue_declare(queue="tweets", durable=True, exclusive=False, auto_delete=False)
chan.exchange_declare(exchange="tweeter", type="direct", durable=True, auto_delete=False)
chan.queue_bind(queue="tweets", exchange="tweeter", routing_key="tweet")

dbconn = Connection("localhost")
db = dbconn.twitter
users = db.users

def tweet(msg):    
    data = json.loads(msg.body)
    user = users.find_one({'Number':data['Number']})
    if user:
        api = twitter.Api(username=user['Username'], password=user['Password'])
        if len(data['Text']) > 140:
            text = data['Text'][:139]
        else:
            text = data['Text']        
        api.PostUpdate(text)
        print text
    else:
        if data['Text'].startswith('r'):
            username, password = data['Text'].split()[1:3]
            user = {'Number': data['Number'],
                    'Username': username,
                    'Password': password}
            users.insert(user)
            print "Inserted %s" % username
        else:
            print "Message %s from %s ignored" % (data['Text'], data['Number'])
    chan.basic_ack(msg.delivery_tag)

chan.basic_consume(queue="tweets", callback=tweet, consumer_tag="tweetertag")

while True:
    chan.wait()

@atexit.register
def cleanup():    
    chan.basic_cancel("tweetertag")    
    chan.close()
    qconn.close()
