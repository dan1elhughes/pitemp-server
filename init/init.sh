#/!usr/bin/env bash

ssh-copy-id pi@raspberrypi.local

ansible-playbook -i init/init-hosts.ini init/init.yml
