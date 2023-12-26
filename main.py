import os
from tkinter import filedialog
import customtkinter as ctk
from PIL import Image, ImageDraw
import numpy as np
import cv2 as cv

img_path = ''
can_show = False
image_to_show = None
selected_image = None

accepted_extensions = ["jpg", "png", "bmp"] 

def selectPath():
    global img_path
    global image_to_show
    global selected_image
    global img_cpy

    selected_image = None
    currdir = os.getcwd()
    img_path = str(filedialog.askopenfile(initialdir=currdir))
    if(img_path):
        if(image_to_show):  # reset if an image has been selected already
            image_to_show.destroy()
        selected_image = img_path.split("name=")[1]
        selected_image = selected_image.split(" mode=")[0]
        selected_image = selected_image.strip("'")
        img_path = selected_image
        file_extension = selected_image.split(".")[-1]
        file_extension = file_extension.strip("'")
        
        if(file_extension in accepted_extensions):  # check for correct file type
            with Image.open(selected_image) as img:
                img_cpy = np.asarray(img)
            updateImage()
        else:
             print("Selected file is not an accepted filetype!")
             filedialog.askopenfile(initialdir=currdir)
    else:
        selectPath()


def selectOutputPath():
    global outputPath
    currdir = os.getcwd()
    outputPath = str(filedialog.askdirectory(initialdir=currdir))
    output_dir_label = ctk.CTkLabel(frame_outputButtons, text=outputPath, font=("Roboto", 12))
    output_dir_label.grid(row=1,column=0,sticky="ew")


def updateImage(arg=None):      #todo cleanup globals
    nothing_burger = arg
    global slider_starting_x
    global slider_starting_y
    global img_cpy
    global selected_image
    global image_to_show
    global back_to_pil
    global x0,y0,x1,y1

    if selected_image is None:
        return

    try:
        scaleY, scaleX, colors = np.shape(img_cpy)
    except NameError:
        return
    ratio = scaleX/scaleY

    if(ratio > 1):
        max_rect_size = scaleY
    else:
        max_rect_size = scaleX
    
    image_cvitised = np.asarray(img_cpy)
    image_cvitised = cv.cvtColor(image_cvitised, cv.COLOR_RGB2BGR)

    rect_size = max_rect_size*slider_size.get()/100
    
    slider_starting_x.configure(to=int((scaleX-rect_size)))
    slider_starting_y.configure(to=int((scaleY-rect_size)))

    x0 = slider_starting_x.get()
    y0 = slider_starting_y.get()
    x1 = x0 + rect_size
    y1 = y0 + rect_size

    

    if(x1 > scaleX):
        x1 = scaleX - 1
    if(y1 > scaleY):
        y1 = scaleY - 1

    thickness = int(max_rect_size / 1000) * 10
    
    cv.rectangle(image_cvitised, (int(x0), int(y0)), (int(x1),int(y1)), (255), thickness)

    back_to_pil = cv.cvtColor(image_cvitised, cv.COLOR_BGR2RGB)
    back_to_pil = Image.fromarray(back_to_pil)

    selected_image = ctk.CTkImage(dark_image=back_to_pil, size=(200*ratio,200))
    
    if(image_to_show is not None):
        image_to_show.configure(image=selected_image)
    else:
        image_to_show = ctk.CTkLabel(root, image=selected_image, text="")
        image_to_show.grid(column=0, row=2, padx=10, pady=5,columnspan=3, sticky='ew')

# todo, fix sliders causing program not to work after clearing img
def clearImage():
    try:
        global image_to_show
        global selected_image
        image_to_show.destroy()
        selected_image.destroy()
        selected_image = None
        image_to_show = None

    except AttributeError:
        pass


def getCroppedImg():
    global img_path
    output = ""
    try:
        with Image.open(img_path) as img:
            im_crop = img.crop((x0, y0, x1, y1))
            im_resized = im_crop.resize((240,240))
            output = outputPath + "/img.bmp" 
            im_resized.save(output, "BMP")
            # im_resized_cropped = im_resized.crop((0, 70, 240, 139))
            # output2 = outputPath + "/imgCropped.bmp" 
            # im_resized_cropped.save(output2, "BMP")
        output = "Successful Write!"
    except AttributeError:
        output = "Bad Write!"
    output_label = ctk.CTkLabel(frame_outputButtons, text=output, font=("Roboto", 12))
    output_label.grid(row=3,column=0,sticky="ew")


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

root = ctk.CTk()
root.geometry("500x600")
root.title("Image Cropper")
root.resizable(False, False)

root.columnconfigure(0, weight=1)
root.columnconfigure(1, weight=1)
root.columnconfigure(2, weight=0)
root.rowconfigure(0, weight=0)
root.rowconfigure(1, weight=0)
root.rowconfigure(2, weight=1)
root.rowconfigure(3, weight=0)

label = ctk.CTkLabel(master=root, text="Image Cropper", font=("Roboto", 24))
label.grid(column=0, row=0,ipady=10, ipadx=0, padx=0, pady=10, sticky='ew', columnspan=3)

button = ctk.CTkButton(root, text="Select Input Image", command=selectPath)
button.grid(row=1,column=0,ipady=0, ipadx=10, padx=20, pady=0)    
button_clear = ctk.CTkButton(root, text="Clear Image", command=clearImage)
button_clear.grid(row=1,column=2, ipady=0, ipadx=10, padx=20,pady=0)    

frame_sliders = ctk.CTkFrame(root)

slider_size_label = ctk.CTkLabel(frame_sliders, text="Select size of rectangle:", font=("Roboto", 12))
slider_size_label.grid(row=0,column=0,sticky="ew")
slider_size = ctk.CTkSlider(frame_sliders, from_=0, to=100, command=updateImage)
slider_size.grid(row=1,column=0,sticky="ew")

slider_starting_x_label = ctk.CTkLabel(frame_sliders, text="Select x position of rectangle:", font=("Roboto", 12))
slider_starting_x_label.grid(row=2,column=0,sticky="ew")
slider_starting_x = ctk.CTkSlider(frame_sliders, from_=0, to=100, command=updateImage)
slider_starting_x.grid(row=3,column=0,sticky="ew")

slider_starting_y_label = ctk.CTkLabel(frame_sliders, text="Select y position of rectangle:", font=("Roboto", 12))
slider_starting_y_label.grid(row=4,column=0,sticky="ew")
slider_starting_y = ctk.CTkSlider(frame_sliders, from_=0, to=100, command=updateImage)
slider_starting_y.grid(row=5, column=0,sticky="ew")

frame_sliders.grid(row=3,column=0,padx=10, pady=5, columnspan = 1, sticky="ewns")

frame_outputButtons = ctk.CTkFrame(root)
button_askoutput = ctk.CTkButton(frame_outputButtons, text="Set Output Directory", command=selectOutputPath)
button_askoutput.grid(row=0,column=0,ipady=0, ipadx=10, padx=20, pady=0)    
button_getoutput = ctk.CTkButton(frame_outputButtons, text="Generate Output", command=getCroppedImg)
button_getoutput.grid(row=2,column=0, ipady=0, ipadx=10, padx=20,pady=0)

frame_outputButtons.grid(row=3,column=2,padx=10, pady=5, columnspan = 1, sticky="ewns")

root.mainloop()