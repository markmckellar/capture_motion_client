import argparse
import warnings
import datetime
import imutils as image_utils
import json
import time
import cv2
import os

class ImageEvent :
        def __init__(self,frame,is_occupied,json_data):
                self.frame = frame
                self.event_time = datetime.datetime.now()
                self.is_occupied = is_occupied
                self.json_data = json_data
        def how_old_in_ms(self) :
                diff = datetime.datetime.now() - self.event_time
                return(diff.microseconds/100)

class ImageEventHolder :
        def __init__(self,output_image_dir,ms_seconds_overlap,should_frames_be_written):
                self.frames = []
                self.time_last_occupied = None
                self.time_last_empty = None
                self.ms_seconds_overlap = ms_seconds_overlap
                self.is_occupied = False
                self.motion_event_counter = 0
                self.output_image_dir = output_image_dir
                self.should_frames_be_written = should_frames_be_written
                self.start_time = datetime.datetime.now()

        def reset(self) :
                print("reset called")
                if(self.should_frames_be_written and self.time_last_occupied is not None) : self.write_frames()
                self.frames = []
                self.time_last_occupied = None
                self.time_last_empty = None  
                self.motion_event_counter += 1
                self.start_time = datetime.datetime.now()


        def write_frames(self) :
                   # output_image_dir
                   frame_counter = 0
                   motion_event_dir = time.strftime("%Y%m%d_%H%M%S")+"_"+str(self.motion_event_counter).rjust(4, '0')
                   print(f"WRITING FRAMES motion_event_dir={motion_event_dir}")

                   for frame_event in self.frames :

                        full_output_dir = self.output_image_dir+"/"+motion_event_dir
                        # Create target Directory if don't exist
                        if not os.path.exists(full_output_dir):os.mkdir(full_output_dir)
                        output_file_name = str(frame_counter).rjust(5, '0')
                        ###########print(f"     WRITING FRAMES full_output_dir={full_output_dir} output_file_name={output_file_name}")
                        cv2.imwrite(full_output_dir+"/" + output_file_name+".jpg", frame_event.frame)
                        with open(full_output_dir+"/" + output_file_name+".json", 'w') as outfile:
                                outfile.write( json.dumps(frame_event.json_data) )

                        frame_counter += 1
        def check_for_max(self) :
                if(self.number_of_frames()>2000): self.reset()
                        
        def add_occupied_frame(self,frame,json_data) :
                self.frames.append( ImageEvent(frame,True,json_data) )
                self.time_last_occupied = datetime.datetime.now()
                self.is_occupied = True

        def add_empty_frame(self,frame,json_data) :
                self.frames.append( ImageEvent(frame,False,json_data))
                self.time_last_empty = datetime.datetime.now()
                self.is_occupied = False

                del_counter = 0
                ms_last_occupied = 0
                if(self.time_last_occupied is None) :
                        while( self.number_of_frames()>0  and self.frames[0].how_old_in_ms()>self.ms_seconds_overlap) :
                                print(f"     deleting first frame  ************* self.frames[0].how_old_in_ms()={self.frames[0].how_old_in_ms()}")                                
                                del self.frames[0]
                                del_counter += 1
                else : 
                        ms_last_occupied = self.get_ms_since_last_occupied()
                        if(ms_last_occupied>self.ms_seconds_overlap) : 
                                print(f"calling reset ms_last_occupied={ms_last_occupied} ms_seconds_overlap={self.ms_seconds_overlap}")
                                self.reset()
                        else :
                                print(f"skipping rest reset ms_last_occupied={ms_last_occupied} ms_seconds_overlap={self.ms_seconds_overlap}")

                frame_zero_age = -99999999999
                if( len(self.frames)>0  ) :
                        frame_zero_age = self.frames[0].how_old_in_ms()
                #print(f"     frames={len(self.frames)} del_counter={del_counter} frame_zero_age={frame_zero_age} ms_seconds_overlap={self.ms_seconds_overlap} ms_last_occupied={ms_last_occupied}")
                
        def get_ms_since_last_occupied(self) :
                use_date = self.time_last_occupied
                if(use_date is None) : use_date = self.start_time                        
                diff = datetime.datetime.now() - use_date
                return(diff.microseconds/100)

        def get_ms_since_last_not_occupied(self) :
                use_date = self.time_last_empty
                if(use_date is None) : use_date = self.start_time                        
                diff = datetime.datetime.now() - use_date
                return(diff.microseconds/100)
        
        def number_of_frames(self) :
                return( len(self.frames) )
        







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

                # filter warnings, load the configuration and initialize the Dropbox
                # client
                warnings.filterwarnings("ignore")
                self.conf = json.load(open(self.args["conf"]))
                self.client = None
                self.avg = None                
                self.mirror = False
                self.file_name = "cam"
                self.motion_event_dir = None
                self.image_event_holder = ImageEventHolder(
                        self.conf["output_image_dir"],
                        self.conf["motion_event_overlap"],
                        self.conf["save_motion_files"])


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

                print(f"number_of_frames={self.image_event_holder.number_of_frames()} ms_since_last_occupied={self.image_event_holder.get_ms_since_last_occupied()} ms_since_last_not_occupied={self.image_event_holder.get_ms_since_last_not_occupied()} is_occupied={self.image_event_holder.is_occupied}")

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
