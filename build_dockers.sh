#!/bin/bash



docker build -t python3_opencv_docker --build-arg PYTHON3_IMAGE=balenalib/i386-ubuntu-python:3.6.9 -f python3_opencv_docker .
cd capture_motion
docker build -t cmo_docker -f cmo_docker .
docker build -t make_video_docker -f make_video_docker .

