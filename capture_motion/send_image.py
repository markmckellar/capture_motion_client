#!/usr/bin/python3

import sys 
import time
import requests
import os
import socket       
import logging
import json
# get the config file 

if(len(sys.argv)!=2) :
	print("Invalid arguments : your_config_file.json : the \"output_image_dir\" is the dir which will be processed")
	print("You gave %i arguments" % (len(sys.argv)))
	quit()

config_file = sys.argv[1]
#server = "http://192.168.1.169:8081"
#server = "http://96.126.98.96:8081"
#server = "http://192.168.1.177:8080"
#endPoint = "/uploadfile"
logging.basicConfig(format='%(asctime)s : %(message)s',stream=sys.stdout,level=logging.DEBUG)

while(True) :
	config_json = {}
	with open(config_file, 'r') as f: config_json = json.load(f)   

	config = config_json["upload_server"]
	# "upload_server":{
	# 		"active":true,
	# 		"watch_dir":"./uploads",
	#		"server_type":"open",
	# 		"server":"http://192.168.1.177:8080",
	# 		"endpoint":"/uploadfile",
	# 		"delete_when_done":true
	# 	},
	
	if(config["active"])  :
		watch_dir = config["watch_dir"] 
		included_extensions = ['jpg','jpeg', 'bmp', 'png', 'gif',"mp4"]
		file_names = [fn for fn in os.listdir(watch_dir)
					if any(fn.endswith(ext) for ext in included_extensions)]

		file_names.sort()
		server_url = config["server"] + config["endpoint"]
		for file_name in file_names:

			full_file_name = watch_dir + "/"+ file_name
			#print(full_file_name)
			print(f"sending {full_file_name} to {server_url}")
			try :
				with open(full_file_name, 'rb') as f:
					r = requests.post(server_url, files={'file': f})
					logging.info("transimited : " + file_name)
					if( config["delete_when_done"]) :
						os.remove(full_file_name) 
			except :
				logging.info("Unexpected error sending file:", sys.exc_info()[0])
		sleep_time = config["sleep_time"]
		print(f"sleeping for {sleep_time}...")
		time.sleep(sleep_time)
	