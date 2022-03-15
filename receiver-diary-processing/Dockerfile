FROM python:3.10.2-alpine

ENV TFG_RABBITMQ_URL=rabbitmq
ENV TFG_RABBITMQ_DIARY_QUEUE=diary

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py ./

CMD [ "python", "-u", "main.py" ]
