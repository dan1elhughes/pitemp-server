#!/usr/bin/env python3

import time
import socket
import board
import adafruit_dht
import psutil
import systemd.daemon
from influxdb import InfluxDBClient

client = InfluxDBClient(host='192.168.1.128', port=8086)
dhtDevice = adafruit_dht.DHT11(board.D2)

systemd.daemon.notify('READY=1')

while True:
    data = []
    try:
        data.append("{measurement},hostname={hostname} temperature={temp},humidity={humidity}".format(
            measurement="pitemp",
            hostname=socket.gethostname(),
            temp=dhtDevice.temperature,
            humidity=dhtDevice.humidity))
    except RuntimeError as error:
        print(error.args[0])

    try:
        memStats = psutil.virtual_memory()
        data.append("{measurement},hostname={hostname} temperature={temp},cpu={cpu},mem_available={mem_available},mem_total={mem_total},mem_used={mem_used},mem_percent={mem_percent}".format(
            measurement="pisystem",
            hostname=socket.gethostname(),
            temp=psutil.sensors_temperatures()['cpu-thermal'][0].current,
            cpu=psutil.cpu_percent(),
            mem_available=memStats.available,
            mem_total=memStats.total,
            mem_used=memStats.used,
            mem_percent=memStats.percent))
    except RuntimeError as error:
        print(error.args[0])

    client.write_points(data, database='external', protocol='line')
    print(data)

    time.sleep(10.0)
