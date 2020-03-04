#!/usr/bin/python3

import sys 
import picamera
import time
import requests
import os
import socket       
import logging


#server = "http://192.168.1.169:8081"
#server = "http://96.126.98.96:8081"
server = "http://192.168.1.177:8080"
endPoint = "/uploadfile"
port=9080
logging.basicConfig(format='%(asctime)s : %(message)s',stream=sys.stdout,level=logging.DEBUG)

piImageServer = server+endPoint

image_path ='./images/'
included_extensions = ['jpg','jpeg', 'bmp', 'png', 'gif']
file_names = [fn for fn in os.listdir(image_path)
              if any(fn.endswith(ext) for ext in included_extensions)]

file_names.sort()

for file_name in file_names:

	full_file_name = image_path + file_name
	#print(full_file_name)
	try :
		with open(full_file_name, 'rb') as f:
			r = requests.post(piImageServer, files={'file': f})
			logging.info("transimited : " + file_name)
	except :
		logging.info("Unexpected error sending file:", sys.exc_info()[0])
	
