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

hostname = socket.gethostname()
client = InfluxDBClient(host=serverIp, port=serverPort,
                        database=serverDatabase)


def seconds_since_boot():
    return time.time() - psutil.boot_time()


# Notify systemd that we're done loading.
systemd.daemon.notify('READY=1')

while True:
    try:
        metrics = {}
        metrics['measurement'] = "system"

        tags = {}
        tags['hostname'] = hostname

        fields = {}
        fields['temp'] = psutil.sensors_temperatures()[
            'cpu_thermal'][0].current
        fields['cpu'] = psutil.cpu_percent()
        fields['uptime'] = seconds_since_boot()

        memStats = psutil.virtual_memory()
        fields['mem_available'] = memStats.available
        fields['mem_total'] = memStats.total
        fields['mem_used'] = memStats.used
        fields['mem_percent'] = memStats.percent

        diskStats = psutil.disk_usage('/')
        fields['disk_total'] = diskStats.total
        fields['disk_used'] = diskStats.used
        fields['disk_free'] = diskStats.free
        fields['disk_percent'] = diskStats.percent

        metrics['tags'] = tags
        metrics['fields'] = fields

        client.write_points([metrics])
        print(metrics)
    except RuntimeError as error:
        print(error.args[0])

    time.sleep(10.0)
