#!/usr/bin/env python
import atexit
import posix_ipc as ipc
import sys
from amqplib import client_0_8 as amqp
import simplejson as json
import time
import setup

count = 0

log = setup.setup_logger("sms.reciever")

exchange = sys.argv[1]
routing_key = sys.argv[2]

semaphore = setup.setup_semaphore()

sm = setup.setup_gammu_state_machine()

qconn, chan = setup.setup_queue()

while True:

    log.debug("Aquiring lock")
    semaphore.acquire()
    log.debug("Lock aquired")
    status = sm.GetSMSStatus()
    semaphore.release()
    log.debug("Lock released")
    total = status['PhoneUsed']
    log.info("Found %s total messages in phone" % total)
    start = True

    remain = total

    while remain > 0:
        log.debug("Aquiring lock")
        semaphore.acquire()
        log.debug("Lock aquired")
        try:
            if start:
                sms = sm.GetNextSMS(Start = True, Folder = 3)
                start = False
            else:
                sms = sm.GetNextSMS(Location = sms[0]['Location'], Folder = 3)
    
            remain = remain - len(sms)
            m = sms[0]
            if m['State'] == 'UnRead':
                log.info("Read message from %s" % m['Number'])
                data = {'Number': m['Number'], 'Text': m['Text']}
                msg = amqp.Message(json.dumps(data))
                msg.properties["delivery_mode"] =  2
                chan.basic_publish(msg, exchange=exchange, routing_key=routing_key)
                log.info("Message from %s queued" % data['Number'])
            else:
                log.info("Read %s unread messages" % (total - remain - 1))
                break
        finally:
            semaphore.release()
            log.debug("Lock released")

    count += 1
    log.info("%s read cycle completed" % count)
    time.sleep(30 )

@atexit.register
def cleanup():
    log.info("Cleanup Started")
    semaphore.close()
    log.debug("Semaphore closed")
    chan.close()
    qconn.close()
    log.debug("Queue Connection closed")
    log.info("Cleanup completed")
