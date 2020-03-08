#!/bin/bash

docker build -t cv_docker_captrue_motion -f cv_docker_captrue_motion  .
docker run -it --rm  -v `pwd`/images:/images --device /dev/video0 --name cv_docker_captrue_motion cv_docker_captrue_motion