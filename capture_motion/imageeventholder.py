from imageevent import ImageEvent
import argparse
import warnings
import datetime
import json
import time
import cv2
import os
import sys
class ImageEventHolder :
        def __init__(self,conf,cmosys):
                self.conf = conf
                self.cmosys = cmosys
                self.output_image_dir = self.conf["output_image_dir"]
                self.ms_seconds_overlap = self.conf["ms_seconds_overlap"]
                self.save_motion_files = self.conf["save_motion_files"]


                self.frames = []
                self.time_last_occupied = None
                self.time_last_empty = None
                self.is_occupied = False
                self.motion_event_counter = 0
                self.start_time = datetime.datetime.now()

        def reset(self) :
                self.cmosys.log.info("reset called")
                if(self.save_motion_files and self.time_last_occupied is not None) : self.write_frames()
                self.frames = []
                self.time_last_occupied = None
                self.time_last_empty = None  
                self.motion_event_counter += 1
                self.start_time = datetime.datetime.now()


        def write_frames(self) :
                # output_image_dir
                frame_counter = 0
                motion_event_dir_final = time.strftime("%Y%m%d_%H%M%S")+"_"+str(self.motion_event_counter).rjust(4, '0')
                motion_event_dir = f"{self.cmosys.notReadyTag()}_{motion_event_dir_final}"
                self.cmosys.log.info(f"WRITING FRAMES motion_event_dir={motion_event_dir}")

                self.cmosys.log.info(f"     f[0].msage={ self.frames[0].how_old_in_ms()} f[0].iso={self.frames[0].event_time_iso}")

                for frame_event in self.frames :

                        full_output_dir = self.output_image_dir+"/"+motion_event_dir
                        # Create target Directory if don't exist
                        if not os.path.exists(full_output_dir):os.mkdir(full_output_dir)
                        output_file_name = str(frame_counter).rjust(5, '0')
                        cv2.imwrite(full_output_dir+"/" + output_file_name+".jpg", frame_event.frame)
                        with open(full_output_dir+"/" + output_file_name+".json", 'w') as outfile:
                                outfile.write( json.dumps(frame_event.json_data,indent=4) )

                        frame_counter += 1
                
                os.rename(self.output_image_dir+"/"+motion_event_dir,self.output_image_dir+"/"+motion_event_dir_final)

        def add_occupied_frame(self,frame,json_data) :
                new_event =  ImageEvent(frame,True,json_data,self)
                self.frames.append(new_event)
                if(self.time_last_occupied is None) :
                        self.cmosys.log.info(f"add 1st occupied frame frame#={self.number_of_frames()} f[0].msage={ self.frames[0].how_old_in_ms()} f[0].iso={self.frames[0].event_time_iso} new_event={new_event.event_time_iso}")
                self.time_last_occupied = datetime.datetime.now()
                self.is_occupied = True

        def add_empty_frame(self,frame,json_data) :
                self.frames.append( ImageEvent(frame,False,json_data,self))
                self.time_last_empty = datetime.datetime.now()
                self.is_occupied = False

                del_counter = 0
                ms_last_occupied = 0
                if(self.time_last_occupied is None) :
                        while( self.number_of_frames()>0  and self.frames[0].how_old_in_ms()>self.ms_seconds_overlap) :
                                #self.cmosys.log.info(f"     deleting first frame  ************* self.frames[0].how_old_in_ms()={self.frames[0].how_old_in_ms()}")                                
                                del self.frames[0]
                                del_counter += 1
                else : 
                        ms_last_occupied = self.get_ms_since_last_occupied()
                        if(ms_last_occupied>self.ms_seconds_overlap) : 
                                self.cmosys.log.info(f"calling reset ms_last_occupied={ms_last_occupied} ms_seconds_overlap={self.ms_seconds_overlap}")
                                self.reset()
                        else :
                                dummmy = 0
                                #self.cmosys.log.info(f"skipping rest reset ms_last_occupied={ms_last_occupied} ms_seconds_overlap={self.ms_seconds_overlap}")

                frame_zero_age = -99999999999
                if( len(self.frames)>0  ) :
                        frame_zero_age = self.frames[0].how_old_in_ms()
                #self.cmosys.log.info(f"     frames={len(self.frames)} del_counter={del_counter} frame_zero_age={frame_zero_age} ms_seconds_overlap={self.ms_seconds_overlap} ms_last_occupied={ms_last_occupied}")
                
        def get_ms_since_last_occupied(self) :
                use_date = self.time_last_occupied
                if(use_date is None) : use_date = self.start_time                        
                diff = datetime.datetime.now() - use_date
                return( diff.total_seconds()*1000 )

        def get_ms_since_last_not_occupied(self) :
                use_date = self.time_last_empty
                if(use_date is None) : use_date = self.start_time                        
                diff = datetime.datetime.now() - use_date
                return( diff.total_seconds()*1000 )
        
        def number_of_frames(self) :
                return( len(self.frames) )

        # def check_for_max(self) :
                #         if(self.number_of_frames()>2000): self.reset()
