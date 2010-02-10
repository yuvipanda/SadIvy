from amqplib import client_0_8 as amqp
qconn = amqp.Connection(hostname="localhost:5672",        
                        virtual_host="/", insist=False)

chan = qconn.channel()

chan.queue_declare(queue="smses", durable=True, exclusive=False, auto_delete=False)
chan.exchange_declare(exchange="smses", type="direct", durable=True, auto_delete=False)
chan.queue_bind(queue="smses", exchange="smses", routing_key="sms")
