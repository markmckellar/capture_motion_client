import argparse
import warnings
import datetime
import json
import time
import cv2
import os
import sys
class ImageEvent :
        def __init__(self,frame,is_occupied,json_data,image_event_holder):
                self.frame = frame
                self.event_time = datetime.datetime.now()
                self.is_occupied = is_occupied
                self.event_time_iso = self.event_time.isoformat()
                self.json_data = {
                        "contours":json_data,
                        "occupied":is_occupied,
                        "event_time_ms":self.event_time.microsecond/100,
                        "event_time_iso":self.event_time.isoformat(),
                        "last_occupied_ago_in_ms":image_event_holder.get_ms_since_last_occupied(),
                        "ms_since_last_occupied":image_event_holder.get_ms_since_last_occupied(),
                        "event_start_time":image_event_holder.start_time.microsecond/100,
                        #"time_last_occupied":image_event_holder.time_last_occupied.microsecond/100,
                        #"time_last_occupied":image_event_holder.time_last_empty.microsecond/100,
                        "number_of_frames":image_event_holder.number_of_frames()
                        }
                image_event_holder.start_time
                image_event_holder.time_last_occupied
                image_event_holder.number_of_frames()
        def how_old_in_ms(self) :
                diff = datetime.datetime.now() - self.event_time
                return( diff.total_seconds()*1000 )

        def distance_in_ms(self,image_event) :
                diff = image_event.event_time - self.event_time
                return( diff.total_seconds()*1000 )

