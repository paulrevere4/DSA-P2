#!/bin/bash

python server.py 0 ex_confs/example.conf  &! python server.py 1 ex_confs/example.conf  &! python server.py 2 ex_confs/example.conf
