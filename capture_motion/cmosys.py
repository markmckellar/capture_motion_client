import logging
import sys
import json

class CmoSys:
    def __init__(self,config_file_name):
        self.config_file_name = config_file_name
        logging.basicConfig(format='%(asctime)s : %(message)s',
            stream=sys.stdout,
            level=logging.DEBUG)
        self.log = logging
        self.log.debug(f"constructor config:{self.config_file_name}")

        self.config_json = None
        self.refreshConfig()


    @staticmethod
    def getnew(config_file_name):
        return(CmoCaputureSystem(config_file_name))

    
    def getAsJsonString(self) :
        return("xyz")

    def notReadyTag(self) :
        return(self.config_json['not_ready_tag'])


    def refreshConfig(self) :
        self.log.info(f"refresh config:{self.config_file_name}")
        self.config_json = self.readInJsonFile(self.config_file_name)
        #with open(self.config_file_name, 'r') as f:
        #    self.config_json = json.load(f)   

    def readInJsonFile(self,json_file) :
        self.log.debug(f"loading json :{json_file}")
        json_object = None
        with open(json_file, 'r') as f:
            json_object = json.load(f)  
        return(json_object)