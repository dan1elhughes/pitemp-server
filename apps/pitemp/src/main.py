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

serverIp = os.environ.get('INFLUX_SERVER_IP')
serverPort = os.environ.get('INFLUX_SERVER_PORT', 8086)
serverDatabase = os.environ.get('INFLUX_SERVER_DATABASE', 'external')

client = InfluxDBClient(host=serverIp, port=8086)

hostname = socket.gethostname()

systemd.daemon.notify('READY=1')

while True:
    data = []
    try:
        data.append("{measurement},hostname={hostname} temperature={temp},humidity={humidity}".format(
            measurement="pitemp",
            hostname=hostname,
            temp=dhtDevice.temperature,
            humidity=dhtDevice.humidity))
    except RuntimeError as error:
        print(error.args[0])

    client.write_points(data, database=serverDatabase, protocol='line')
    print(data)

    time.sleep(10.0)
