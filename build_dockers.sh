#!/bin/bash


# docker login
# docker tag python3_opencv_docker  markmckellar/python3_opencv_docker-i386-ubuntu
# markmckellar/python3_opencv_docker-i386-ubuntu 

# docker login
# docker tag python3_opencv_docker  markmckellar/python3_raspberrypi3-debian
# markmckellar/python3_opencv_raspberrypi3-debian


docker build -t python3_opencv_docker --build-arg PYTHON3_IMAGE=balenalib/i386-ubuntu-python:3.6.9 -f python3_opencv_docker .
#docker build -t python3_opencv_docker --build-arg PYTHON3_IMAGE=balenalib/raspberrypi3-debian-python:3.6.9 -f python3_opencv_docker .

cd capture_motion
docker build -t cmo_docker -f cmo_docker .
docker build -t make_video_docker -f make_video_docker .

