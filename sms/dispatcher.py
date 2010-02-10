#!/usr/bin/env python
import atexit
import posix_ipc as ipc
from amqplib import client_0_8 as amqp
import simplejson as json
import gammu
import logging
import setup

log = setup.setup_logger("sms.dispatcher")

semaphore = setup.setup_semaphore()

conn, chan = setup.setup_queue()

sm = setup.setup_gammu_state_machine()

def send_sms(msg):
    log.debug("Waiting for lock")
    semaphore.acquire()
    log.debug("Acquired lock")
    data = json.loads(msg.body)
    data['SMSC'] = {'Location': 1}
    try:
        sm.SendSMS(data)
        chan.basic_ack(msg.delivery_tag)
        log.info("Sent %s message: %s" % (data['Number'], data['Text']))
    finally:
        semaphore.release()
        log.debug("Lock released")

chan.basic_consume(queue="smses",callback=send_sms, consumer_tag="smstag")
try:
    while True:
        chan.wait()
except KeyboardInterrupt:
    pass

@atexit.register
def cleanup():
    log.info("Cleanup Started")
    semaphore.close()
    log.debug("Semaphore closed")
    chan.basic_cancel("smstag")
    chan.close()
    conn.close()
    log.debug("Queue Connection closed")
    log.info("Cleanup completed")
