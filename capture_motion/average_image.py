import cv2

class AverageImage:
    def __init__(self, max_image_buffer):
        self.average_window = []
        self.max_image_buffer = max_image_buffer

    def get_num_files(self):
        return len(self.average_window)

    def add_image(self,image):
        self.average_window.append(image)

    def remove_image(self):
        del self.average_window[0]


    def gray_and_blur(self,image_to_gray):
        gray = cv2.cvtColor(image_to_gray, cv2.COLOR_BGR2GRAY)
        gray_and_blur = cv2.GaussianBlur(gray, (21, 21), 0)
        return(gray_and_blur)

    def get_average_image(self):
        avearage_past = None

        for one_past_image in reversed(self.average_window):
                if avearage_past is None: 
                        avearage_past = one_past_image
                else :
                        avearage_past = cv2.addWeighted(avearage_past,0.9, one_past_image,0.1,0) 
        return avearage_past


# max_iamge_buffer  = 50
# average_files_window = []
# average_image
