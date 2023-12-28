import os
from tkinter import filedialog
import customtkinter as ctk
from PIL import Image
import numpy as np
import cv2 as cv


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.accepted_extensions = ["bmp", "jpg", "png"]
        
        self.img_ctk_object = None
        self.img_label_object = None  # initialise
        self.img_cpy = None
        self.img_object = None

        self.geometry("500x600")
        self.title("Image Cropper")
        self.resizable(False, False)
    
        self.columnconfigure((0,1), weight=1)
        self.columnconfigure(2, weight=0)
        self.rowconfigure((0,1), weight=0)
        self.rowconfigure(2, weight=1)
        self.rowconfigure(3, weight=0)
    
        self.label = ctk.CTkLabel(master=self, text="Image Cropper", font=("Roboto", 24))
        self.label.grid(column=0, row=0,ipady=10, ipadx=0, padx=0, pady=10, sticky='ew', columnspan=3)
    
        self.button = ctk.CTkButton(self, text="Select Input Image", command=self.selectPath)
        self.button.grid(row=1,column=0,ipady=0, ipadx=10, padx=20, pady=0)    
        

        self.image_button_frame = ImageButtonFrames(self, self.clearImage, self.rotateCCW, self.rotateCW)
        self.image_button_frame.grid(row=1,column=2, ipady=0, ipadx=10, padx=20,pady=0)    
    
        self.slider_frame = SliderFrame(self, self.updateImage)
        self.slider_frame.grid(row=3,column=0,padx=10, pady=5, columnspan = 1, sticky="ewns")
    
        self.frame_outputButtons = OutputButtonsFrame(self, self.writeImage)
        self.frame_outputButtons.grid(row=3,column=2,padx=10, pady=5, columnspan = 1, sticky="ewns")
    

    def selectPath(self):
        self.curr_dir = os.getcwd()
        self.img_object = filedialog.askopenfile(initialdir=self.curr_dir)
        if(self.img_object is None):
            return
        else:
            self.file_extension = self.img_object.name.split(".")[-1]   # get file extension
        
            if(self.file_extension in self.accepted_extensions):  # check for correct file type
                self.img_path = self.img_object.name
                self.frame_outputButtons.setImgPath(self.img_path)
                with Image.open(self.img_path) as self.img:
                    self.img = np.asarray(self.img)   # convert to CV2 format and colours (BGR)
                    self.img = cv.cvtColor(self.img, cv.COLOR_RGB2BGR)
                self.updateImage()


    def clearImage(self):
        if(self.img_label_object is None):
            return
        self.img_label_object.destroy()
        self.img_label_object = None
        self.img_ctk_object = None
        self.img_object = None


    def updateImage(self):
        if(self.img_object is None):    # checking if no image has been selected
            return
        else:
            self.img_cpy = self.img.copy()

            self.img_size_y, self.img_size_x, self.img_size_colours = np.shape(self.img_cpy)
            
            self.ratio = self.img_size_x / self.img_size_y            
    

            self.max_rect_size = min(self.img_size_x, self.img_size_y)  # we want the maximum size of the cropping square to be the minimum of the two image dimensions

            self.rectsize = self.max_rect_size * self.slider_frame.getSizeVal() / 100
            
            self.slider_frame.updateSliderEndstops(self.slider_frame.slider_starting_x, int(self.img_size_x-self.rectsize))
            self.slider_frame.updateSliderEndstops(self.slider_frame.slider_starting_y, int(self.img_size_y-self.rectsize))

            self.x0 = int(self.slider_frame.getXVal())       # coordinates to draw cropping square
            self.y0 = int(self.slider_frame.getYVal())
            self.x1 = int(self.x0 + self.rectsize)
            self.y1 = int(self.y0 + self.rectsize)

            if(self.x1 > self.img_size_x):
                self.x1 = self.img_size_x - 1
            if(self.y1 > self.img_size_y):
                self.y1 = self.img_size_y - 1

            self.thickness = int(self.max_rect_size / 1000) * 10    # scale the thickness of the cropping square with the size of image
            
            cv.rectangle(self.img_cpy, (self.x0, self.y0), (self.x1-self.thickness, self.y1-self.thickness), (255, 0, 0), self.thickness)

            self.img_pil_format = cv.cvtColor(self.img_cpy, cv.COLOR_BGR2RGB)
            self.img_pil_format = Image.fromarray(self.img_pil_format)
            
            if(self.img_ctk_object is not None):                    # don't create new image or label if one already exists
                self.img_ctk_object.configure(dark_image=self.img_pil_format)
                self.img_ctk_object.configure(size=(200*self.ratio,200))    # a bit wasteful but whatever
            else:
                self.img_ctk_object = ctk.CTkImage(dark_image=self.img_pil_format, size=(200*self.ratio,200))       # ratio is used to fix the size of the displayed image

            if(self.img_label_object is not None):
                self.img_label_object.configure(image=self.img_ctk_object)
            else:
                self.img_label_object = ctk.CTkLabel(self, image=self.img_ctk_object, text="")
                self.img_label_object.grid(column=0, row=2, padx=10, pady=5,columnspan=3, sticky='ew')
    

    def getCropCoords(self):
        return(self.x0, self.y0, self.x1, self.y1)


    def rotateCCW(self):
        try:
            self.img = cv.rotate(self.img, cv.ROTATE_90_COUNTERCLOCKWISE)
            self.updateImage()
        except AttributeError:
            pass

    def rotateCW(self):
        try:
            self.img = cv.rotate(self.img, cv.ROTATE_90_CLOCKWISE)
            self.updateImage()
        except AttributeError:
            pass


    def writeImage(self):
        self.output = ""
        try:
            self.im_crop = cv.cvtColor(self.img, cv.COLOR_BGR2RGB)
            self.im_crop = Image.fromarray(self.im_crop)
            self.im_crop = self.im_crop.crop(self.getCropCoords())
            self.im_resized = self.im_crop.resize((240,240))
            self.output = self.frame_outputButtons.getOutputPath() + "/img.bmp" 
            self.im_resized.save(self.output, "BMP")
            self.output = "Successful Write!"
        except AttributeError:
            self.output = "Bad Write!"      
        return self.output


class SliderFrame(ctk.CTkFrame):
    def __init__(self, master, slider_callback):
        super().__init__(master)
        self.slider_callback = slider_callback      # we pass in the updateImage function to update the image whenever values are updated

        self.size_val = 50
        self.x_val = 0
        self.y_val = 0

        self.slider_size_label = ctk.CTkLabel(self, text="Select size of rectangle:", font=("Roboto", 12))
        self.slider_size_label.grid(row=0,column=0,sticky="ew")
        self.slider_size = ctk.CTkSlider(self, from_=0, to=100, command=self.updateSizeVal)
        self.slider_size.grid(row=1,column=0,sticky="ew")
    
        self.slider_starting_x_label = ctk.CTkLabel(self, text="Select x position of rectangle:", font=("Roboto", 12))
        self.slider_starting_x_label.grid(row=2,column=0,sticky="ew")
        self.slider_starting_x = ctk.CTkSlider(self, from_=0, to=100, command=self.updateXVal)
        self.slider_starting_x.grid(row=3,column=0,sticky="ew")
    
        self.slider_starting_y_label = ctk.CTkLabel(self, text="Select y position of rectangle:", font=("Roboto", 12))
        self.slider_starting_y_label.grid(row=4,column=0,sticky="ew")
        self.slider_starting_y = ctk.CTkSlider(self, from_=0, to=100, command=self.updateYVal)
        self.slider_starting_y.grid(row=5, column=0,sticky="ew")
    

    def updateSizeVal(self, value):         # could probably combine into one function
        self.size_val = value
        self.slider_callback()


    def getSizeVal(self):
        return self.size_val
    

    def updateXVal(self, value):
        self.x_val = value
        self.slider_callback()

    def getXVal(self):
        return self.x_val
    

    def updateYVal(self, value):
        self.y_val = value
        self.slider_callback()

    def getYVal(self):
        return self.y_val
    

    def updateSliderEndstops(self, slider, newEndstop):
        slider.configure(to=newEndstop)


class OutputButtonsFrame(ctk.CTkFrame):
    def __init__(self, master, writeImgCallback):
        super().__init__(master)

        self.writeImageCallback = writeImgCallback

        self.button_askoutput = ctk.CTkButton(self, text="Set Output Directory", command=self.selectOutputPath)
        self.button_askoutput.grid(row=0,column=0,ipady=0, ipadx=10, padx=20, pady=0)    
        self.button_getoutput = ctk.CTkButton(self, text="Generate Output", command=self.getCroppedImg)
        self.button_getoutput.grid(row=2,column=0, ipady=0, ipadx=10, padx=20,pady=0)
    
    def selectOutputPath(self):
        self.currdir = os.getcwd()
        self.outputPath = str(filedialog.askdirectory(initialdir=self.currdir))
        self.output_dir_label = ctk.CTkLabel(self, text=self.outputPath, font=("Roboto", 12))
        self.output_dir_label.grid(row=1,column=0,sticky="ew")


    def setImgPath(self, path):
        self.img_path = path


    def getOutputPath(self):
        return self.outputPath


    def getCroppedImg(self):
        output = self.writeImageCallback()
        output_label = ctk.CTkLabel(self, text=output, font=("Roboto", 12))
        output_label.grid(row=3,column=0,sticky="ew")
        

class ImageButtonFrames(ctk.CTkFrame):
    def __init__(self, master, clearCallback, rotateCCWCallback, rotateCWCallback):
        super().__init__(master)

        self.clearCallback = clearCallback
        self.rotateCWCallback = rotateCWCallback
        self.rotateCCWCallback = rotateCCWCallback

        self.button_clear = ctk.CTkButton(self, text="×", command=self.clearCallback, width=5)
        self.button_clear.grid(row=0, column=2, ipadx=7, padx=2, sticky="w")
        self.button_rotateCCW = ctk.CTkButton(self, text="↶", command=self.rotateCCWCallback, width=5)
        self.button_rotateCCW.grid(row=0, column=0, ipadx=5, padx=(19,2),sticky="w")
        self.button_rotateCW = ctk.CTkButton(self, text="↷", command=self.rotateCWCallback, width=5)
        self.button_rotateCW.grid(row=0, column=1, ipadx=5, padx=2,sticky="w")


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")
app = App()
app.mainloop()