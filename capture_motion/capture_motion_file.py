#!/usr/bin/python3
import argparse
import warnings
import datetime
import imutils as image_utils
import json
import time
import cv2
import os
import average_image


# construct the argument parser and parse the arguments
# export DISPLAY=localhost:0.0
# ./capture_motion_file.py -c config.json -o ./
class CaptrueMotion :

        def __init__(self):

                self.arg_parser = argparse.ArgumentParser()
                self.arg_parser.add_argument("-c", "--conf", required=True,
                        help="path to the JSON configuration file")
                self.arg_parser.add_argument("-o", "--output", required=True,
                        help="path to output directory")
                #self.arg_parser.add_argument("-f", "--fps", type=int, default=10,
                #	help="FPS of output video")
                self.arg_parser.add_argument("-d", "--codec", type=str, default="mp4v",
                        help="codec of output video") #MJPG for an .avi, mp4v for an mp4
                self.arg_parser.add_argument("-b", "--buffer-size", type=int, default=32,
                        help="buffer size of video clip writer")
                self.args = vars(self.arg_parser.parse_args())

                #####kcw = KeyClipWriter(bufSize=args["buffer_size"])

                # filter warnings, load the configuration and initialize the Dropbox
                # client
                warnings.filterwarnings("ignore")
                self.conf = json.load(open(self.args["conf"]))
                self.client = None

                self.avg = None
                self.consecFrames = 0
                self.motionCounter = 0

                self.counter = 0
                self.not_occupied_counter = 0
                self.occupied_counter = 0
                self.mirror = False
                self.file_name = "cam"

                self.average_image = average_image.AverageImage(5)

        def start_grabbing_frames(self) :
                
                #grab_frames_from_files('/mnt/c/dev/python/images/')
                #self.grab_frames_from_files('/home/mdm/storage/proc_images/')
                self.grab_frames_from_camera()


        def grab_frames_from_files(self,relevant_path) :
                included_extensions = ['jpg','jpeg', 'bmp', 'png', 'gif']
                file_names = [fn for fn in os.listdir(relevant_path)
                        if any(fn.endswith(ext) for ext in included_extensions)]
                file_names.sort()
                for file_name in file_names: 
                        self.file_name = file_name
                        full_file_name = relevant_path+file_name
                        frame = cv2.imread(full_file_name) 
                        print("yep!:"+full_file_name)
                        self.do_a_frame(frame)


        #### use this section for capture frames from the camera
        def grab_frames_from_camera(self) :
                cam = cv2.VideoCapture(0)

                while(True) :
                        ret_val, frame = cam.read()
                        if self.mirror: frame = cv2.flip(frame, 1) 
                        self.file_name = "image_from_cam"
                        self.do_a_frame(frame)

        def do_a_frame(self,frame) :   
                full_file_name = "this is full_file_name read in, but its from a camera"
                timestamp = datetime.datetime.now()
                text = "Unoccupied"
        
                # resize the frame, convert it to grayscale, and blur it
                frame = image_utils.resize(frame, width=500)
                frame_copy = frame.copy()

                if(self.average_image.get_num_files()==0) : self.average_image.add_image(frame_copy)
                average_past = self.average_image.get_average_image()

                # current frame changed to gray and blurred
                current_gray = self.average_image.gray_and_blur(frame_copy)

                # past frame changed to gray and blurred
                avg_gray = self.average_image.gray_and_blur(average_past)        
                self.avg = avg_gray.copy().astype("float")

                cv2.accumulateWeighted(current_gray, self.avg, 0.5)
                frameDelta = cv2.absdiff(current_gray, cv2.convertScaleAbs(self.avg))
                #frameDelta = cv2.absdiff(current_gray, cv2.convertScaleAbs(avg_gray))
                # threshold the delta image, dilate the thresholded image to fill
                # in holes, then find contours on thresholded image
                thresh = cv2.threshold(frameDelta, self.conf["delta_thresh"], 255,cv2.THRESH_BINARY)[1]
                thresh = cv2.dilate(thresh, None, iterations=2)
                ###import imutils
                cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                cnts = cnts[0] if image_utils.is_cv2() else cnts[1]
                
                # loop over the contours
                contour_list = []
                for c in cnts:
                        # if the contour is too small, ignore it
                        if cv2.contourArea(c) < self.conf["min_area"]: continue
                        # compute the bounding box for the contour, draw it on the frame, and update the text
                        (x, y, w, h) = cv2.boundingRect(c)
                        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                        contour_list.append({"x":x,"y":y,"w":w,"h":h})
                        text = "Occupied"
        
                # draw the text and timestamp on the frame
                ts = timestamp.strftime("%A %d %B %Y %I:%M:%S%p")+":"+self.file_name
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
                        self.average_image.add_image(frame_copy)
                        if(self.average_image.get_num_files() > self.average_image.max_image_buffer) : self.average_image.remove_image()
                if(False): print(text+":working on elemnt "+str(counter)+" status="+status+" avg files="+str( self.average_image.get_num_files() ) +
                        " self.not_occupied_counter="+str(self.not_occupied_counter)+
                        " max_image_buffer="+str(self.average_image.max_image_buffer))#+" of "+len(file_names.size))
                if text != "Occupied" : 
                        self.occupied_counter = 0
                        self.not_occupied_counter += 1
                if text == "Occupied" :
                        self.occupied_counter = 0
                        self.occupied_counter += 1
                        self.motionCounter += 1
                        if self.motionCounter >= self.conf["min_motion_frames"]:
                                self.consecFrames = 0
                                #print("Uploaded")
                                #if not kcw.recording:
                                if(False):
                                        
                                        timestamp = datetime.datetime.now()
                                        # .avi for an avi (must have MJPG set in codec in args
                                        p = "{}/{}.mp4".format(self.args["output"],timestamp.strftime("%Y%m%d-%H%M%S"))
                                        kcw.start(p, cv2.VideoWriter_fourcc(*self.args["codec"]), self.conf["fps"])
                                self.motionCounter = 0
                        origFileName =  "Detection_" + time.strftime("%Y%m%d-%H%M%S") +"_"+str(self.counter)+ ".jpg"
                        #cv2.imwrite('/images/' + origFileName, im_v)
                        if(True): 
                                countor_json = ""
                                if( len(contour_list) > 0) : countor_json = json.dumps(contour_list)
                                print(text+":"+origFileName+":working on elemnt "+str(self.counter)+" status="+status+" avg files="+str( self.average_image.get_num_files() ) +
                                " self.not_occupied_counter="+str(self.not_occupied_counter)+
                                " max_image_buffer="+str(self.average_image.max_image_buffer)+
                                ":"+countor_json)#+" of "+len(file_names.size))

                
                if updateConsecFrames: self.consecFrames += 1#increment motion counter of frames wihtout motion
                self.counter = self.counter + 1            

#capture_motion = CaptureMotion()
#capture_motion.start_grabbing_frames()