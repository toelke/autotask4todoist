FROM python:3.10.6

RUN pip install --no-cache-dir paho-mqtt todoist-python

WORKDIR /app
COPY *.py /app

#ENV MQTT_BROKER
#ENV MQTT_TOPIC
#ENV TODOIST_API_KEY

CMD python3 autotask.py
