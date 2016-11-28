#!/bin/bash

kill $(ps | grep "python server" | awk '{print $1}')
