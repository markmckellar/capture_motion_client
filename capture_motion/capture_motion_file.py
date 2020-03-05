#!/usr/bin/python3
import argparse
import warnings
import datetime
import imutils
import json
import time
import cv2
import os
import average_image


# construct the argument parser and parse the arguments
# export DISPLAY=localhost:0.0
# ./capture_motion_file.py -c config.json -o ./

ap = argparse.ArgumentParser()
ap.add_argument("-c", "--conf", required=True,
        help="path to the JSON configuration file")
ap.add_argument("-o", "--output", required=True,
	help="path to output directory")
#ap.add_argument("-f", "--fps", type=int, default=10,
#	help="FPS of output video")
ap.add_argument("-d", "--codec", type=str, default="mp4v",
	help="codec of output video") #MJPG for an .avi, mp4v for an mp4
ap.add_argument("-b", "--buffer-size", type=int, default=32,
	help="buffer size of video clip writer")
args = vars(ap.parse_args())

#####kcw = KeyClipWriter(bufSize=args["buffer_size"])

# filter warnings, load the configuration and initialize the Dropbox
# client
warnings.filterwarnings("ignore")
conf = json.load(open(args["conf"]))
client = None

avg = None
lastUploaded = datetime.datetime.now()
consecFrames = 0
motionCounter = 0

counter = 0
not_occupied_counter = 0
occupied_counter = 0
mirror = False
file_name = "cam"

average_image = average_image.AverageImage(5)

relevant_path ='/mnt/c/dev/python/images/'
included_extensions = ['jpg','jpeg', 'bmp', 'png', 'gif']
file_names = [fn for fn in os.listdir(relevant_path)
              if any(fn.endswith(ext) for ext in included_extensions)]
file_names.sort()


#for f in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):

##### use this section for capture frames from the camera
# cam = cv2.VideoCapture(0)
# while(True):
#     ret_val, frame = cam.read()
#     if mirror: frame = cv2.flip(frame, 1) 
##### use this section for getting images from dir
for file_name in file_names: 
        full_file_name = relevant_path+file_name
        frame = cv2.imread(full_file_name) 
        timestamp = datetime.datetime.now()
        text = "Unoccupied"
 
        # resize the frame, convert it to grayscale, and blur it
        frame = imutils.resize(frame, width=500)
        frame_copy = frame.copy()

        if(average_image.get_num_files()==0) : average_image.add_image(frame_copy)
        average_past = average_image.get_average_image()

        # current frame changed to gray and blurred
        current_gray = average_image.gray_and_blur(frame_copy)

        # past frame changed to gray and blurred
        avg_gray = average_image.gray_and_blur(average_past)        
        avg = avg_gray.copy().astype("float")

        cv2.accumulateWeighted(current_gray, avg, 0.5)
        frameDelta = cv2.absdiff(current_gray, cv2.convertScaleAbs(avg))
        #frameDelta = cv2.absdiff(current_gray, cv2.convertScaleAbs(avg_gray))
        # threshold the delta image, dilate the thresholded image to fill
        # in holes, then find contours on thresholded image
        thresh = cv2.threshold(frameDelta, conf["delta_thresh"], 255,cv2.THRESH_BINARY)[1]
        thresh = cv2.dilate(thresh, None, iterations=2)
        import imutils
        cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = cnts[0] if imutils.is_cv2() else cnts[1]
         
        # loop over the contours
        for c in cnts:
                # if the contour is too small, ignore it
                if cv2.contourArea(c) < conf["min_area"]: continue
                # compute the bounding box for the contour, draw it on the frame, and update the text
                (x, y, w, h) = cv2.boundingRect(c)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                text = "Occupied"
 
        # draw the text and timestamp on the frame
        ts = timestamp.strftime("%A %d %B %Y %I:%M:%S%p")+":"+file_name
        cv2.putText(frame, "Room Status: {}".format(text), (10, 20),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        cv2.putText(frame, ts, (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX,0.35, (0, 0, 255), 1)
        updateConsecFrames = True
        
        # check to see if the room is occupied
        im_v = cv2.hconcat([frame, average_past])
        #im_v = cv2.hconcat([gray,avg_gray])
        if(True):#counter>48 and counter<100):
                #cv2.imshow('image',average_past)
                cv2.imshow('im_v',im_v)
                cv2.waitKey(100)        
                cv2.destroyAllWindows()
        status = "0"
        
        if True :
                average_image.add_image(frame_copy)
                if(average_image.get_num_files() > average_image.max_image_buffer) : average_image.remove_image()
        if(False): print(text+":working on elemnt "+str(counter)+" status="+status+" avg files="+str( average_image.get_num_files() ) +
                " not_occupied_counter="+str(not_occupied_counter)+
                " max_image_buffer="+str(average_image.max_image_buffer))#+" of "+len(file_names.size))
        if text != "Occupied" : 
                occupied_counter = 0
                not_occupied_counter += 1
        if text == "Occupied" :
                not_occupied_counter = 0
                occupied_counter += 1
                motionCounter += 1
                if motionCounter >= conf["min_motion_frames"]:
                        import time
                        consecFrames = 0
                        #print("Uploaded")
                        #if not kcw.recording:
                        if(False):
                                
                                timestamp = datetime.datetime.now()
                                # .avi for an avi (must have MJPG set in codec in args
                                p = "{}/{}.mp4".format(args["output"],timestamp.strftime("%Y%m%d-%H%M%S"))
                                kcw.start(p, cv2.VideoWriter_fourcc(*args["codec"]), conf["fps"])
                        motionCounter = 0
                origFileName =  "Detection_" + time.strftime("%Y%m%d-%H%M%S") +"_"+str(counter)+ ".jpg"
                #cv2.imwrite('/images/' + origFileName, im_v)
                if(True): print(text+":"+origFileName+":working on elemnt "+str(counter)+" status="+status+" avg files="+str( average_image.get_num_files() ) +
                        " not_occupied_counter="+str(not_occupied_counter)+
                        " max_image_buffer="+str(average_image.max_image_buffer))#+" of "+len(file_names.size))

        
        if updateConsecFrames: consecFrames += 1#increment motion counter of frames wihtout motion
        counter = counter + 1            