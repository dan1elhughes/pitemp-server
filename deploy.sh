#!/usr/bin/env bash

rsync --delete -avP . pizero1:pitemp/
ssh pizero1 'ln -sf ~/pitemp/pitemp.service ~/.config/systemd/user'
ssh pizero1 'systemctl --user restart pitemp'
ssh pizero1 'systemctl --user enable pitemp'
ssh pizero1 'sudo loginctl enable-linger $USER'
