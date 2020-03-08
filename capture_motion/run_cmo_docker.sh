#!/bin/bash

docker run -it --rm  -v `pwd`/images:/images --device /dev/video0 --name cmo_docker cmo_docker 
docker run -it --rm  -v `pwd`/images:/images --device /dev/video0 --name make_video_docker make_video_docker