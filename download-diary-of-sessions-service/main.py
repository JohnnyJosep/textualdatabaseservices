from multiprocessing.connection import deliver_challenge
import time
import requests
import json
import redis
import os
import pika

legislature = 14
url = os.environ['TFG_URL'] if 'TFG_URL' in os.environ else 'https://www.congreso.es/public_oficiales/L14/CONG/DS/PL/DSCD-14-PL-'
file_type = os.environ['TFG_FILE_TYPE'] if 'TFG_FILE_TYPE' in os.environ else 'dscd'
redis_host = os.environ['TFG_REDIS'] if 'TFG_REDIS' in os.environ else '127.0.0.1'
fs_url = os.environ['TFG_FS_URL'] if 'TFG_FS_URL' in os.environ else 'http://localhost:9000/fs'
errors_threshold = 50
rabbit_host = os.environ['TFG_RABBITMQ_URL'] if 'TFG_RABBITMQ_URL' in os.environ else 'localhost'
rabbit_diary_queue = os.environ['TFG_RABBITMQ_DIARY_QUEUE'] if 'TFG_RABBITMQ_DIARY_QUEUE' in os.environ else 'diary'


r = redis.Redis(host=redis_host, port=6379, db=0)


def download(plenary, ch):
    pdf = f'{url}{plenary}.PDF'
    file_name = f'{file_type}-{legislature:02d}-{plenary:02d}.pdf'

    if r.exists(file_name):
        return True

    download_response = requests.get(pdf)
    if download_response.status_code != 200:
        return False

    file = download_response.content
    upload_response = requests.post(fs_url, files=[('file',  ('test.pdf', file))])

    fs_response = json.loads(upload_response.content.decode('utf8'))
    r.set(f'{file_type}-{legislature:02d}-{plenary:03d}.pdf', fs_response['filename'])

    ch.basic_publish(
        exchange='',
        routing_key=rabbit_diary_queue,
        body=fs_response['filename'],
        properties=pika.BasicProperties(delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE))

    return True


def download_all():       
    connection = pika.BlockingConnection(pika.ConnectionParameters(rabbit_host))
    channel = connection.channel()
    channel.queue_declare(queue=rabbit_diary_queue, durable=True)

    plenary = 0
    errors = 0
    while errors < errors_threshold:
        if not download(plenary, channel):
            errors += 1
        else:
            print(f'Plenary {plenary}')
        plenary += 1
    
    
    connection.close()


if __name__ == '__main__':
    time.sleep(60)
    while True:
        download_all()
        print('Sleep')
        time.sleep(60 * 60 * 24)  # sleep one day
