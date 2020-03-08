#!/usr/bin/python3
import argparse
import warnings
import datetime
import imutils as image_utils
import json
import time
import cv2
import os


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

                self.output_image_dir = self.conf["output_image_dir"]
                self.last_occupied_frames_past = 0

                self.avg = None
                ##########self.motionCounter = 0
                self.motion_event_number = 0

                self.not_occupied_counter = 0
                self.occupied_counter = 0
                self.mirror = False
                self.file_name = "cam"
                self.motion_event_dir = None



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
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                gray = cv2.GaussianBlur(gray, (21, 21), 0)
                # if the average frame is None, initialize it
                if self.avg is None:
                        print("[INFO] starting background model...")
                        self.avg = gray.copy().astype("float")
                        return
                # accumulate the weighted average between the current frame and
                # previous frames, then compute the difference between the current
                # frame and running average
                cv2.accumulateWeighted(gray, self.avg, 0.05)
                frameDelta = cv2.absdiff(gray, cv2.convertScaleAbs(self.avg))

                # threshold the delta image, dilate the thresholded image to fill
                # in holes, then find contours on thresholded image
                thresh = cv2.threshold(frameDelta, self.conf["delta_thresh"], 255,cv2.THRESH_BINARY)[1]
                thresh = cv2.dilate(thresh, None, iterations=2)

                cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                cnts = cnts[0] if image_utils.is_cv2() else cnts[1]
                
                # loop over the contours
                contour_list = []
                if(self.conf["show_video"]) : frame_copy = frame.copy()
                for c in cnts:
                        # if the contour is too small, ignore it
                        if cv2.contourArea(c) < self.conf["min_area"]: continue
                        # compute the bounding box for the contour, draw it on the frame, and update the text
                        (x, y, w, h) = cv2.boundingRect(c)
                        if(self.conf["show_video"]) :
                                cv2.rectangle(frame_copy, (x, y), (x + w, y + h), (0, 255, 0), 2)
                        contour_list.append({"x":x,"y":y,"w":w,"h":h})
                        text = "Occupied"


                
                if(self.conf["show_video"]):
                        # draw the text and timestamp on the frame
                        ts = timestamp.strftime("%A %d %B %Y %I:%M:%S%p")+":"+self.file_name
                        cv2.putText(frame_copy, "Room Status: {}".format(text), (10, 20),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                        cv2.putText(frame_copy, ts, (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX,0.35, (0, 0, 255), 1)
                        display_image = cv2.hconcat([frame, frame_copy])
                        cv2.imshow('display_image',display_image)
                        cv2.waitKey(5)        
                        #cv2.destroyAllWindows()
                status = "0"
                

                if text != "Occupied" : 
                        self.occupied_counter = 0
                        self.not_occupied_counter += 1
                        self.last_occupied_frames_past += 1
                if text == "Occupied":
                        if(self.occupied_counter==0) : 
                                self.motion_event_number += 1
                                self.motion_event_dir = time.strftime("%Y%m%d_%H%M%S")+"_"+str(self.motion_event_number).rjust(8, '0')
                                print("self.not_occupied_counter="+str(self.not_occupied_counter)+" "+self.motion_event_dir)

                        self.last_occupied_frames_past = 0
                        self.not_occupied_counter = 0
                        self.occupied_counter += 1
                        #self.motionCounter += 1
                        #if self.motionCounter >= self.conf["min_motion_frames"]:
                                #self.consecFrames = 0
                                #print("Uploaded")
                                #if not kcw.recording:
                                # if(False):
                                        
                                #         timestamp = datetime.datetime.now()
                                #         # .avi for an avi (must have MJPG set in codec in args
                                #         p = "{}/{}.mp4".format(self.args["output"],timestamp.strftime("%Y%m%d-%H%M%S"))
                                #         kcw.start(p, cv2.VideoWriter_fourcc(*self.args["codec"]), self.conf["fps"])
                                #self.motionCounter = 0
                        if(self.conf["save_motion_files"]):
                                # output_image_dir
                                full_output_dir = self.output_image_dir+"/"+self.motion_event_dir
                                # Create target Directory if don't exist
                                if not os.path.exists(full_output_dir):os.mkdir(full_output_dir)
                                output_file_name = str(self.occupied_counter).rjust(5, '0')
                                cv2.imwrite(full_output_dir+"/" + output_file_name+".jpg", frame)
                                with open(full_output_dir+"/" + output_file_name+".json", 'w') as outfile:
                                        json.dump(json.dumps(contour_list), outfile)

                

#capture_motion = CaptureMotion()
#capture_motion.start_grabbing_frames()