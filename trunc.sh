#!/bin/bash

ffmpeg -i $1 -t 1200 -c copy $2
