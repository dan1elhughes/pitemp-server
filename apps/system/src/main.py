#!/usr/bin/env python3

import time
import os
import socket
import psutil
import systemd.daemon
from influxdb import InfluxDBClient

serverIp = os.environ.get('INFLUX_SERVER_IP', '192.168.1.128')
print("Env: serverIp ", serverIp)
serverPort = os.environ.get('INFLUX_SERVER_PORT', 8086)
print("Env: serverPort ", serverPort)
serverDatabase = os.environ.get('INFLUX_SERVER_DATABASE', 'external')
print("Env: serverDatabase ", serverDatabase)

client = InfluxDBClient(host=serverIp, port=serverPort,
                        database=serverDatabase)

hostname = socket.gethostname()

systemd.daemon.notify('READY=1')


def seconds_since_boot():
    return time.time() - psutil.boot_time()


while True:
    metrics = {}
    try:
        metrics['measurement'] = "system"

        tags = {}
        tags['hostname'] = hostname
        metrics['tags'] = tags

        memStats = psutil.virtual_memory()
        fields = {}
        fields['temp'] = psutil.sensors_temperatures()[
            'cpu-thermal'][0].current
        fields['cpu'] = psutil.cpu_percent()
        fields['mem_available'] = memStats.available
        fields['mem_total'] = memStats.total
        fields['mem_used'] = memStats.used
        fields['mem_percent'] = memStats.percent
        fields['uptime'] = seconds_since_boot()
        metrics['fields'] = fields

        client.write_points([metrics])
        print(metrics)
    except RuntimeError as error:
        print(error.args[0])

    time.sleep(10.0)
