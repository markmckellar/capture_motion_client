## VStream video from cv2 docker


### Usage
1. install docker
2. build the docker : docker build -t cv_docker_stream_vid -f cv_docker_stream_vid  .
3. run the docker : docker run -it --rm  -d -p 5000:5000 --device /dev/video0 --name cv_docker_stream_vid cv_docker_stream_vid
4. Navigate the browser to the local webpage : http://<host ip>:5000/
5. list the dockers running : docker -ps
6. kill the docker : docker stop cv_docker_stream_vid