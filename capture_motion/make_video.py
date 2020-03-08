#!/usr/bin/python3
import cv2
import numpy as np
import glob
import os 
import sys
import json



class MakeVideo :

    def __init__(self):
        self.xxxx = 0

    def make_video_from_image_dir(self,image_folder,video_name,image_ends_with) :
        images = [img for img in os.listdir(image_folder) if img.endswith(image_ends_with)]
        images.sort()
        frame = cv2.imread(os.path.join(image_folder, images[0]))
        height, width, layers = frame.shape

        video = cv2.VideoWriter(video_name, 0, 1, (width,height))

        for image in images:
            video.write(cv2.imread(os.path.join(image_folder, image)))

        cv2.destroyAllWindows()
        video.release()



# get the config file 

if(len(sys.argv)!=2) :
    print("Invalid arguments : your_config_file.json : the \"output_image_dir\" is the dir which will be processed")
    print("You gave %i arguments" % (len(sys.argv)))
    quit()
config_file = sys.argv[1]

config_json = {}
with open(config_file, 'r') as f:
        config_json = json.load(f)   


folder = config_json["output_image_dir"]
print(f"starting processing:folder={folder}")

subfolders = [ f.path for f in os.scandir(folder) if f.is_dir() ]
subfolders.sort()        

make_video = MakeVideo()
for image_dir in subfolders: 
    size = None
    img_array_for_a_dir = []

    # then the files...
    movie_file = image_dir+".avi"
    image_ends_with = "jpg"
    print(f"processing:image_dir={image_dir} image_type={image_ends_with} write to={movie_file}")
    make_video.make_video_from_image_dir(image_dir,movie_file,image_ends_with)
