import posix_ipc as ipc
from amqplib import client_0_8 as amqp
import gammu
import logging
from logging.handlers import SysLogHandler

log = None
semaphore = None
logging.basicConfig()

def setup_logger(name):
    global log
    log = logging.getLogger(name)
    log.setLevel(logging.DEBUG)
    handler = SysLogHandler(address="/dev/log")
    formatter = logging.Formatter("%(name)s: %(levelname)s %(message)s")
    handler.setFormatter(formatter)
    log.addHandler(handler)
    return log

def setup_semaphore():
    global semaphore
    log.info("Opening semaphore")    
    semaphore = ipc.Semaphore("/send_sms", flags=ipc.O_CREAT, initial_value=1)
    log.info("Semaphore opened")
    return semaphore

def _loop_init_sm(sm, device_no=0):
    config = sm.GetConfig()
    try:
        device = '/dev/ttyACM' + str(device_no)
        config['Device'] = device
        sm.SetConfig(0, config)
        sm.Init()
        log.info("Connected to %s" % device)
    except (gammu.ERR_DEVICENOTEXIST, gammu.ERR_DEVICEOPENERROR):
        if device_no < 32:
            _loop_init_sm(sm, device_no + 1)
        else:
            raise

def setup_gammu_state_machine():
    log.info("Connecting to phone")
    sm = gammu.StateMachine()
    log.debug("Acquiring lock (value %s)" % semaphore.value)
    semaphore.acquire()
    log.debug("Lock acquired")
    sm.ReadConfig()
    try:
        _loop_init_sm(sm)
    finally:
        semaphore.release()
        log.debug("Lock released")
    return sm

def setup_queue():
    log.info("Connecting to Queue")
    qconn = amqp.Connection(hostname="localhost:5672", virtual_host="/", insist=False)
    chan = qconn.channel()
    log.info("Queue Server connected")
    return (qconn, chan)
