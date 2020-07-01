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
    SAVE_PATH = os.path.join(dir,"images_with_boxes_dpi_"+str(dpi))  # Directory to save the images with boxes
    PAGE_NUM = len(images)                                      # Total number of pdf pages
    os.makedirs(SAVE_PATH, exist_ok=True)

    for page_num in range(PAGE_NUM):
        image_new = images[page_num]
        cropped = image_new
        if len(boxes[page_num]) > 0:                  # Some figures detected
            for box_num in range(len(boxes[page_num])):
                box_idx = boxes[page_num][box_num]
                box = [(int(box_idx["y1"]) - Error_Margin), (int(box_idx["x1"]) - Error_Margin),
                       (int(box_idx["y2"]) + Error_Margin), (int(box_idx["x2"]) + Error_Margin)]                          # Get box boundary coordinates
                image_new = visualize_box(box = box, image = image_new) 
                cropped = image_new[box[0]:box[2], box[1]:box[3]]                      # Extract the cropped image of the figure
        # Save the images
        # Pages that do not have figures are saved just as normal 
        if np.array_equal(image_new, cropped):                                       # If the images are the same, save as normal
            io.imsave(os.path.join(SAVE_PATH, "Page" + str(page_num) + ".png"), image_new) 
        else:                                                                          # Else saved the cropped one
            io.imsave(os.path.join(SAVE_PATH,"CroppedPage" + str(page_num) + ".png"), cropped)  # Depict bounding boxes

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
    dirs = os.listdir(pdf_directory)
    'Draws bounding boxes over figures in pdfs in output directory'
    # Loop through all directories
    for dir in dirs:
        dir = os.path.join(settings.Local_Output, dir) # Adding path to dir
        pdf_name = next(x for x in os.listdir(dir) if x[-4:]==".pdf").replace(".pdf", "").strip(" ")  # Get pdf name by removing extra white space and .pdf
        with open(os.path.join(dir,pdf_name+"deepfigures-results.json")) as f:       # Load JSON file containing bounding
            output = json.load(f)
        boxes = output["raw_detected_boxes"]      # Get bounding boxes for all pages

        IMAGE_PATH = os.path.join(dir,pdf_name+".pdf-images","ghostscript","dpi"+str(DPI))
        image_names = sorted(os.listdir(IMAGE_PATH))
        image_names.remove("_SUCCESS")                 # Get image names for all pages
        images = []

        for name in image_names:
            images.append(np.array(io.imread(os.path.join(IMAGE_PATH, name))))  # Get images as numpy arrays
            depict_boxes(dir=dir, dpi=DPI, images=images, boxes=boxes, Error_Margin=error_margin)

if __name__ == '__main__':
    boundbox_overlay()
