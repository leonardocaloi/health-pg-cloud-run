FROM python:3.9

ENV PORT 3000

RUN apt-get update -y && \
    apt-get install -y python3-pip

COPY app/ /app

WORKDIR /app

RUN pip install -r requirements.txt

RUN pip install gunicorn

CMD exec gunicorn --bind :$PORT main:app