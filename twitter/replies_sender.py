#!/usr/bin/env python
import atexit
from amqplib import client_0_8 as amqp
from pymongo.connection import Connection
import simplejson as json
import twitter

conn = amqp.Connection(hostname="localhost:5672",
                       virtual_host="/", insist=False)

chan = conn.channel()

dbconn = Connection("localhost")
db = dbconn.twitter
users = db.users

for u in users.find():
    api = twitter.Api(username=u['Username'], password=u['Password'])
    print "Replies for %s" % u['Username']
    if not 'since_id' in u:
        replies = api.GetReplies()
    else:
        replies = api.GetReplies(since_id=u['since_id'])
        if len(replies) > 0:    
            for r in replies:
                data = {'Number': u['Number'], 'Text': '@%s: %s' % (r.GetUser().GetScreenName(), r.GetText())}
                msg = amqp.Message(json.dumps(data))
                msg.properties["delivery_mode"] =  2
                chan.basic_publish(msg, exchange="smses", routing_key="sms")
                print "Sent %s" % data['Text']

    if len(replies) > 0:
        u['since_id'] = replies[0].GetId()
        users.save(u)

@atexit.register
def cleanup():
    chan.close()
    conn.close()
            
