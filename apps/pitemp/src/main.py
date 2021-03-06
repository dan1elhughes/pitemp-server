#!/usr/bin/env python3

# OS stuff
import time
import os
import socket

# GPIO stuff
import board
import adafruit_dht
import systemd.daemon

# Webthings server stuff
import logging
import tornado.ioloop
from webthing import (SingleThing, Property, Thing, Value,
                      WebThingServer)

device = adafruit_dht.DHT22(board.D2)


class ClimateSensor(Thing):
    def __init__(self):
        Thing.__init__(
            self,
            f'urn:dev:ops:climate-sensor-{socket.gethostname()}',
            f'{socket.gethostname()} climate sensor',
            ['MultiLevelSensor'],
            'Climate'
        )

        self.location = Value(os.environ.get('LOCATION'))
        self.add_property(
            Property(self,
                     'location',
                     self.location,
                     metadata={
                         'title': 'Location',
                         'type': 'string',
                         'description': 'Location of the sensor',
                         'readOnly': True,
                     }))

        self.temperature = Value(0.0)
        self.add_property(
            Property(self,
                     'temperature',
                     self.temperature,
                     metadata={
                         '@type': 'LevelProperty',
                         'title': 'Temperature',
                         'type': 'integer',
                         'description': 'The current temperature in degrees celsius',
                         'unit': 'degree celsius',
                         'readOnly': True,
                     }))

        self.humidity = Value(0.0)
        self.add_property(
            Property(self,
                     'humidity',
                     self.humidity,
                     metadata={
                         '@type': 'LevelProperty',
                         'title': 'Humidity',
                         'type': 'integer',
                         'description': 'The current humidity in %',
                         'minimum': 0,
                         'maximum': 100,
                         'unit': 'percent',
                         'readOnly': True,
                     }))

        logging.debug('starting the sensor update looping task')
        self.timer = tornado.ioloop.PeriodicCallback(
            self.update_sensors,
            5000
        )
        self.timer.start()

    def update_sensors(self):
        try:
            new_temperature = self.read_temp_from_gpio()
            logging.debug('setting new temperature: %s', new_temperature)
            self.temperature.notify_of_external_update(new_temperature)
        except (RuntimeError, ValueError) as error:
            logging.warning('failed to get new temperature: %s', error.args[0])

        try:
            new_humidity = self.read_humidity_from_gpio()
            logging.debug('setting new humidity: %s', new_humidity)
            self.humidity.notify_of_external_update(new_humidity)
        except (RuntimeError, ValueError) as error:
            logging.warning('failed to get new humidity: %s', error.args[0])

    def cancel_update_level_task(self):
        self.timer.stop()

    @staticmethod
    def read_temp_from_gpio():
        value = device.temperature
        if value is not None:
            return value
        raise ValueError('read a zero value')

    @staticmethod
    def read_humidity_from_gpio():
        value = device.humidity
        if value is not None:
            return value
        raise ValueError('read a zero value')


def run_server():
    sensor = ClimateSensor()

    server = WebThingServer(SingleThing(sensor),
                            port=8888)
    try:
        logging.info('starting the server')
        systemd.daemon.notify('READY=1')
        server.start()

    except KeyboardInterrupt:
        logging.debug('canceling the sensor update looping task')
        sensor.cancel_update_level_task()
        logging.info('stopping the server')
        server.stop()
        logging.info('done')


if __name__ == '__main__':
    logging.basicConfig(
        level=10,
        format="%(filename)s:%(lineno)s %(levelname)s %(message)s"
    )
    run_server()
