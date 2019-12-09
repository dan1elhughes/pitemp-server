#!/usr/bin/env python3

import time
import os
import socket
import board
import adafruit_dht
import psutil
import systemd.daemon
from influxdb import InfluxDBClient

dhtDevice = adafruit_dht.DHT11(board.D2)

location = os.environ.get('LOCATION')
print("Env: location ", location)

serverIp = os.environ.get('INFLUX_SERVER_IP')
print("Env: serverIp ", serverIp)
serverPort = os.environ.get('INFLUX_SERVER_PORT', 8086)
print("Env: serverPort ", serverPort)
serverDatabase = os.environ.get('INFLUX_SERVER_DATABASE', 'external')
print("Env: serverDatabase ", serverDatabase)

client = InfluxDBClient(host=serverIp, port=serverPort,
                        database=serverDatabase)

hostname = socket.gethostname()

systemd.daemon.notify('READY=1')

while True:
    metrics = {}
    try:
        metrics['measurement'] = "pitemp"

        tags = {}
        tags['hostname'] = hostname
        tags['location'] = location
        metrics['tags'] = tags

        fields = {}
        fields['temperature'] = dhtDevice.temperature
        fields['humidity'] = dhtDevice.humidity
        metrics['fields'] = fields

        client.write_points([metrics])
        print(metrics)
    except RuntimeError as error:
        print(error.args[0])

    time.sleep(10.0)
