#!/usr/bin/env python3

import time
import os
import socket
import psutil
import systemd.daemon
from influxdb import InfluxDBClient

serverIp = os.environ.get('INFLUX_SERVER_IP')
serverPort = os.environ.get('INFLUX_SERVER_PORT', 8086)
serverDatabase = os.environ.get('INFLUX_SERVER_DATABASE', 'external')

client = InfluxDBClient(host=serverIp, port=8086)

hostname = socket.gethostname()

systemd.daemon.notify('READY=1')


def seconds_since_boot():
    return time.time() - psutil.boot_time()


while True:
    data = []

    try:
        memStats = psutil.virtual_memory()
        data.append("{measurement},hostname={hostname} temperature={temp},cpu={cpu},mem_available={mem_available},mem_total={mem_total},mem_used={mem_used},mem_percent={mem_percent},uptime={uptime}".format(
            measurement="pisystem",
            hostname=socket.gethostname(),
            temp=psutil.sensors_temperatures()['cpu-thermal'][0].current,
            cpu=psutil.cpu_percent(),
            mem_available=memStats.available,
            mem_total=memStats.total,
            mem_used=memStats.used,
            mem_percent=memStats.percent,
            uptime=seconds_since_boot()))
    except RuntimeError as error:
        print(error.args[0])

    client.write_points(data, database=serverDatabase, protocol='line')
    print(data)

    time.sleep(10.0)
