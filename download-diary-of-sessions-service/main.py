import time
import requests
import json
import redis
import os

legislature = int(os.environ['TFG_LEGISLATURE']) if 'TFG_LEGISLATURE' in os.environ else 14
url = os.environ['TFG_URL'] if 'TFG_URL' in os.environ else f'https://www.congreso.es/public_oficiales/L14/CONG/DS/PL/DSCD-14-PL-'
file_type = os.environ['TFG_FILE_TYPE'] if 'TFG_FILE_TYPE' in os.environ else 'dscd'
redis_host = os.environ['TFG_REDIS'] if 'TFG_REDIS' in os.environ else '127.0.0.1'
fs_url = os.environ['TFG_FS_URL'] if 'TFG_FS_URL' in os.environ else 'http://localhost:9000/fs'
errors_threshold = 50

r = redis.Redis(host=redis_host, port=6379, db=0)


def download(plenary):
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
    r.set(f'{file_type}-{legislature:02d}-{plenary:02d}.pdf', fs_response['filename'])
    # TODO: Add to rabbitmq
    return True


def download_all():
    plenary = 0
    errors = 0
    while errors < errors_threshold:
        if not download(plenary):
            errors += 1
        else:
            print(f'Plenary {plenary}')
        plenary += 1


if __name__ == '__main__':
    while True:
        download_all()
        print('Sleep')
        time.sleep(60 * 60 * 24)  # sleep one day
