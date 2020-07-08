import numpy as np
import json
import os
import logging
import click
from skimage import io

from deepfigures import settings

# Get all the directories in the folder
DPI = 100

logger = logging.getLogger(__name__)

def visualize_box(box, image, thick = 3):
    """
    Drawing the rectangular bounding boxes on the images of pdf pages
        @PARAM:
            box: list of 4 int, the four coordinates of the bounding boxes
            image: numpy array, the 3D numpy array representing images
            thick: int, the thickness of the bounding boxes depicted, DEFAULT = 3 pixels
        @RETURN:
            I_new: the images with bounding boxes on them
    """
    height = image.shape[0]
    width = image.shape[1]
    I_new = np.copy(image)
    t = max(box[0]-thick,0)
    b = min(box[2]+thick,height)
    l = max(box[1]-thick,0)
    r = min(box[3]+thick,width)
    for h in range(t,box[0]):
        I_new[h, l:r, 0] = 0
        I_new[h, l:r, 1] = 255
        I_new[h, l:r, 2] = 0
    for h in range(box[0],box[2]):
        I_new[h, l:box[1], 0] = 0
        I_new[h, l:box[1], 1] = 255
        I_new[h, l:box[1], 2] = 0
        I_new[h, box[3]:r, 0] = 0
        I_new[h, box[3]:r, 1] = 255
        I_new[h, box[3]:r, 2] = 0
    for h in range(box[2],b):
        I_new[h, l:r, 0] = 0
        I_new[h, l:r, 1] = 255
        I_new[h, l:r, 2] = 0
    return I_new

def depict_boxes(dir, dpi, images, boxes, Error_Margin, thick = 3):
    """
    Drawing the rectangular bounding boxes on the images of pdf pages
        @PARAM:
            dir: the directory where pdf is saved
            dpi: the dpi in the setting
            images: list of numpy arrays, the filenames of the images of the pdf pages, in PNG
            boxes: list of dictionaries, the coordinates of bounding boxes
            thick: int, the thickness of the bounding boxes depicted, DEFAULT = 3 pixels
        @RETURN:
            Void
    """
    SAVE_PATH = os.path.join(dir,"images_with_boxes_dpi_" + str(dpi))  # Directory to save the images with boxes
    IMAGE_NUM = len(images)
    PDF_NAME = next(x for x in os.listdir(dir) if x[-4:] == ".pdf").replace(".pdf", "").strip(" ")                                      # Total number of pdf pages

    try:
        os.makedirs(SAVE_PATH)
    except OSError: # stops if figures have already been extracted
        if len(os.listdir(SAVE_PATH)) > IMAGE_NUM:
            return 

    for page_num in range(IMAGE_NUM):
        image_new = images[page_num]
        num_images = len(boxes[page_num])
        if  num_images > 0:  
            for box_num in range(num_images):
                # Reset cropped each time so we start fresh with the full page
                cropped = image_new
                box_idx = boxes[page_num][box_num]
                box = [int(box_idx["y1"]) - Error_Margin, int(box_idx["x1"]) - Error_Margin,
                       int(box_idx["y2"]) + Error_Margin, int(box_idx["x2"]) + Error_Margin]                          # Get box boundary coordinates
                image_new = visualize_box(box = box, image = image_new) 
                cropped = image_new[box[0]:box[2], box[1]:box[3]] 
                # We are going to save each image on every page
                io.imsave(os.path.join(SAVE_PATH, PDF_NAME + "Page" + str(page_num + 1) + '-' + str(box_num + 1) + ".png"), cropped)  # Depict bounding boxes

@click.command(
    context_settings={
        'help_option_names': ['-h', '--help']
    })

@click.option(
    '--Error_Margin', default = 10,
    help='Making bounding box with Error_Margin # pixels larger on each side. Default is 10.')

@click.argument(
    'pdf_directory',
    type=click.Path(
        exists=True,
        file_okay=False,
        dir_okay=True,
        resolve_path=True))

def boundbox_overlay(pdf_directory, error_margin):
    'Draws bounding boxes over figures in pdfs in output directory'
    
    dirs = os.listdir(pdf_directory)
    Failed_Files = 0
    Processed_Files = 0
    Processed_Images = 0
    try:
        # Remove done file if from a previous run
        os.remove(os.path.join(os.getcwd(), pdf_directory, "Done_Extracting_Figures.txt"))
    except FileNotFoundError:
        pass
    # Loop through all directories
    for dir in dirs:
        dir = os.path.join(os.getcwd(), pdf_directory, dir) # Adding path to dir
        if (not os.path.isdir(dir)):
            continue # Then skip
        try:
            pdf_name = next(x for x in os.listdir(dir) if x[-4:] == ".pdf").replace(".pdf", "").strip(" ")  # Get pdf name by removing extra white space and .pdf
            if (os.path.exists(dir + "/Image_Extracted.txt")):
                print("Skipping processed file")
                continue # Skip if already processed
            with open(os.path.join(dir, pdf_name + "deepfigures-results.json")) as f:       # Load JSON file containing bounding
                output = json.load(f)
            boxes = output["raw_detected_boxes"]      # Get bounding boxes for all pages

            IMAGE_PATH = os.path.join(dir, pdf_name + ".pdf-images", "ghostscript", "dpi" + str(DPI))
            image_names = sorted(os.listdir(IMAGE_PATH))
            image_names.remove("_SUCCESS")                 # Get image names for all pages
            images = []

            for name in image_names:
                images.append(np.array(io.imread(os.path.join(IMAGE_PATH, name))))  # Get images as numpy arrays
                depict_boxes(dir=dir, dpi=DPI, images=images, boxes=boxes, Error_Margin=error_margin)    
                Processed_Images += 1
            Processed_Files += 1
            # File that contains the number of processed files
            with open(os.path.join(os.getcwd(), pdf_directory, "Processed_Files.txt"), 'a+') as f:
                f.write("File Success #:" + str(Processed_Files) + ', File name:' + pdf_name + ', Number of images:' + str(Processed_Images) + "\n")
            open(os.path.join(dir, "Image_Extracted.txt"), "w+")
        except FileNotFoundError:
            Failed_Files += 1 # Add 1 to Failed file count
            print("Skipped file because it had issues will processing in deepfigures.")
            with open(os.path.join(os.getcwd(), pdf_directory, "Failed_Files.txt"), 'a+') as f:
                f.write("File Failed #:" + str(Failed_Files) + ", File name:" + pdf_name + "\n")
            open(os.path.join(dir, "Image_Extracted.txt"), "w+")
            continue
        except NotADirectoryError:
            continue
    # Create done file to indicate the boundbox finished
    f = open(os.path.join(os.getcwd(), pdf_directory, "Done_Extracting_Figures.txt"), 'a+')
    f.close()
    print("Done extracting figures!")

if __name__ == '__main__':
    boundbox_overlay()