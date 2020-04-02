import argparse
import warnings
import datetime
import json
import time
import cv2
import os
import sys
from cmosys import CmoSys
from imageevent import ImageEvent
from imageeventholder import ImageEventHolder


class CaptrueMotion :

        def __init__(self):


                if(len(sys.argv)!=2) :
                        print("Invalid arguments : your_config_file.json : the \"output_image_dir\" is the dir which will be processed")
                        print("You gave %i arguments" % (len(sys.argv)))
                        quit()
                ######config_file = sys.argv[1]
                self.cmosys = CmoSys(sys.argv[1])
                #config_json = {}
                #with open(config_file, 'r') as f:
                #        config_json = json.load(f)  

                self.conf = self.cmosys.config_json["motion_event_generator"]

                self.avg = None                
                self.mirror = False
                self.file_name = "cam"
                self.motion_event_dir = None
                self.image_event_holder = ImageEventHolder(self.conf,self.cmosys)


        def grab_frames_from_files(self,relevant_path) :
                included_extensions = ['jpg','jpeg', 'bmp', 'png', 'gif']
                file_names = [fn for fn in os.listdir(relevant_path)
                        if any(fn.endswith(ext) for ext in included_extensions)]
                file_names.sort()
                for file_name in file_names: 
                        self.file_name = file_name
                        full_file_name = relevant_path+file_name
                        frame = cv2.imread(full_file_name) 
                        self.do_a_frame(frame)
                self.image_event_holder.reset()



        #### use this section for capture frames from the camera
        def grab_frames_from_camera(self) :
                cam = cv2.VideoCapture(0)

                while(True) :
                        ret_val, frame = cam.read()
                        if self.mirror: frame = cv2.flip(frame, 1) 
                        self.file_name = "image_from_cam"
                        self.do_a_frame(frame)
                self.reset()

        def do_a_frame(self,frame) :   
                full_file_name = "this is full_file_name read in, but its from a camera"
                timestamp = datetime.datetime.now()
                text = "Unoccupied"
        
                # resize the frame, convert it to grayscale, and blur it
                #frame = image_utils.resize(frame, width=500)
                frame = self.resize(frame, width=500)
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                gray = cv2.GaussianBlur(gray, (21, 21), 0)
                # if the average frame is None, initialize it
                if self.avg is None:
                        self.cmosys.log.info("starting background model")
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
                #print(f"image_utils.is_cv2()={ str(image_utils.is_cv2()) } image_utils.is_cv3()={ str(image_utils.is_cv3()) }")
                #cnts = cnts[0] if image_utils.is_cv2() else cnts[1]
                cnts = cnts[1]
                
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
                        self.image_event_holder.add_empty_frame(frame,contour_list)

                if text == "Occupied":
                        self.image_event_holder.add_occupied_frame(frame,contour_list)

                #print(f"number_of_frames={self.image_event_holder.number_of_frames()} ms_since_last_occupied={self.image_event_holder.get_ms_since_last_occupied()} ms_since_last_not_occupied={self.image_event_holder.get_ms_since_last_not_occupied()} is_occupied={self.image_event_holder.is_occupied}")

        def resize(self,image, width=None, height=None, inter=cv2.INTER_AREA):
                # initialize the dimensions of the image to be resized and
                # grab the image size
                dim = None
                (h, w) = image.shape[:2]

                # if both the width and height are None, then return the
                # original image
                if width is None and height is None:
                        return image

                # check to see if the width is None
                if width is None:
                        # calculate the ratio of the height and construct the
                        # dimensions
                        r = height / float(h)
                        dim = (int(w * r), height)

                # otherwise, the height is None
                else:
                        # calculate the ratio of the width and construct the
                        # dimensions
                        r = width / float(w)
                        dim = (width, int(h * r))

                # resize the image
                resized = cv2.resize(image, dim, interpolation=inter)

                # return the resized image
                return resized     



#cmo = cmo.CaptrueMotion()
#cmo.grab_frames_from_files('../../test_data/images_1/')
#cmo.grab_frames_from_files('/home/mdm/storage/proc_images/')
#cmo.grab_frames_from_files('../../test_data/images_2/')

cmo = CaptrueMotion()
cmo.grab_frames_from_camera()