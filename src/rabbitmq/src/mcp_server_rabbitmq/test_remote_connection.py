import pika
import ssl


username = "admin"
password = "admintestrabbit"
rabbitmq_host = "b-9560b8e1-3d33-4d91-9488-a3dc4a61dfe7.mq.us-east-1.amazonaws.com"
port = 5671

# SSL Context for TLS configuration of Amazon MQ for RabbitMQ
ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
ssl_context.set_ciphers('ECDHE+AESGCM:!ECDSA')
url = f"amqps://{username}:{password}@{rabbitmq_host}:{port}"
parameters = pika.URLParameters(url)
parameters.ssl_options = pika.SSLOptions(context=ssl_context)
connection = pika.BlockingConnection(parameters)
channel = connection.channel()
channel.queue_declare("hello")
channel.basic_publish(exchange="", routing_key="hello", body="this is a test message")