import pika, os

rabbit_host = os.environ['TFG_RABBITMQ_URL'] if 'TFG_RABBITMQ_URL' in os.environ else 'localhost'
rabbit_diary_queue = os.environ['TFG_RABBITMQ_DIARY_QUEUE'] if 'TFG_RABBITMQ_DIARY_QUEUE' in os.environ else 'diary'

def main():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbit_host))
    channel = connection.channel()

    def callback(ch, method, properties, body):
        print(" [x] Received %r" % body.decode())
        ch.basic_ack(delivery_tag = method.delivery_tag)

    channel.basic_consume(queue=rabbit_diary_queue, on_message_callback=callback, auto_ack=False)
    channel.start_consuming()

if __name__ == '__main__':
    main()