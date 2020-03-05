import cv2

class AverageImage:
    def __init__(self, max_image_buffer):
        self.average_window = []
        self.max_image_buffer = max_image_buffer
        self.average_image = None

    def get_num_files(self):
        return len(self.average_window)

    def add_image(self,image):
        self.average_window.append(image)
        if(self.average_image is None) : 
            self.average_image = image.copy()
        else :
            percent_per_file =  1 / self.get_num_files()
            self.average_image = cv2.addWeighted(
                self.average_image,
                ####add_factor * (self.get_num_files()-1),
                (self.max_image_buffer-1)/self.max_image_buffer,
                image,
                ####add_factor,
                1/self.max_image_buffer,
                0) 


    def remove_image(self):
        to_be_removed = self.average_window[0]
        if(self.get_num_files()==0) : 
            self.average_image = None
        else :            
            add_factor =  1 / self.max_image_buffer

            print("remove add_factor="+str(add_factor)+" "+str( self.get_num_files() ))
            self.average_image = cv2.addWeighted(
                self.average_image,
                2*(1-add_factor),# * ( (self.max_image_buffer-1)/self.max_image_buffer ),
                to_be_removed,
                -add_factor,
                0) 
        del self.average_window[0]

    def get_average_image(self):
        return self.average_image


# max_iamge_buffer  = 50
# average_files_window = []
# average_image
