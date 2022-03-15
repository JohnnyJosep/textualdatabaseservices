from urllib import response
import pika
import os
import time
import requests

rabbit_host = os.environ['TFG_RABBITMQ_URL'] if 'TFG_RABBITMQ_URL' in os.environ else 'localhost'
rabbit_diary_queue = os.environ['TFG_RABBITMQ_DIARY_QUEUE'] if 'TFG_RABBITMQ_DIARY_QUEUE' in os.environ else 'diary'
fs_url = os.environ['TFG_FS_URL'] if 'TFG_FS_URL' in os.environ else 'http://localhost:9000/fs'
ocr_url = os.environ['TFG_OCR_URL'] if 'TFG_OCR_URL' in os.environ else 'http://localhost:9001/ocr/pdf'

def download_pdf(filename):
    url = f'{fs_url}/{filename}'
    response = requests.get(url)
    if response.status_code != 200:
        return None

    file = response.content
    return file


def process_ocr(pdf):
    response = requests.post(ocr_url, files=[('file', pdf)])
    if response.status_code != 200:
        return None
    
    data = response.content
    return data


def main():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbit_host))
    channel = connection.channel()

    def callback(ch, method, properties, body):
        print("Received %r" % body.decode())
        pdf = download_pdf(body.decode())
        if pdf == None:
            return
        
        ocr = process_ocr(pdf)
        if ocr == None:
            return

        ch.basic_ack(delivery_tag = method.delivery_tag)

    channel.basic_consume(queue=rabbit_diary_queue, on_message_callback=callback, auto_ack=False)
    channel.start_consuming()

if __name__ == '__main__':

    print("1")
    pdf = download_pdf('0a9af0db-bc3b-4957-a9b6-58082e986951.pdf')
    print(pdf == None)
    ocr = process_ocr(pdf)
    print(ocr)

    #time.sleep(60)
    #main()