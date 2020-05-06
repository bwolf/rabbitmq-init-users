FROM python:3-slim

COPY requirements.txt /usr/local/src/
RUN pip install --no-cache-dir -r /usr/local/src/requirements.txt
COPY src/main.py /usr/local/bin/rabbitmq-init

ENTRYPOINT ["/usr/local/bin/rabbitmq-init"]