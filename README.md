# `pitemp`

A systemd+python service for emitting metrics for a DHT11 chip and system metrics to an InfluxDB server.

It's _very_ specific to me, so I haven't exposed any configuration. 😅

## Adding a new device

Assuming the new device is named `raspberrypi.local`:

Edit the hostname in init/init-hosts.ini. Todo, make this read from the shell arguments.

```sh
$ ./init/init.sh
```
