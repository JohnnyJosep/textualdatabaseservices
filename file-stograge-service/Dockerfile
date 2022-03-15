FROM python:3.10.2-alpine

WORKDIR /usr/src/app

ENV TFG_ROOT_FOLDER=/home/fs

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py ./

CMD [ "python", "-u", "main.py" ]

EXPOSE 80