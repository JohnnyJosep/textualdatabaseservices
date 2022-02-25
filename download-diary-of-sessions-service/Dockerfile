FROM python:3.10.2-alpine

WORKDIR /usr/src/app

ENV TFG_URL=https://www.congreso.es/public_oficiales/L14/CONG/DS/PL/DSCD-14-PL-
ENV TFG_FILE_TYPE=dscd
ENV TFG_REDIS=redis
ENV TFG_FS_URL=http://fs/fs

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py ./

CMD [ "python", "./main.py" ]