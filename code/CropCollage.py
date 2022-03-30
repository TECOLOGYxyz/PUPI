# -*- coding: utf-8 -*-
"""
@author: 
Hjalte M. R. Mann
Aarhus University
TECOLOGY.xyz

Production of collages of crops of flower and insect detections to be used on Zooniverse.

This script takes raw images and detection info (bounding box coordinates) for flowers and insects as input. 
It crops detections and produces collages with four crops in each. It also produces a manifest to be used on the Zooniverse platform.

"""

import cv2
import pandas as pd
import csv
import os
from PIL import Image, ImageDraw
from math import ceil

### SET THE RELEVANT PATHS ###
camyear = "2018_NARS-02"
flower_detections = r"2018_NARS-02_submit_boxes_NewFormat_NoZeroes_Day.csv"
known_visitors = r"Dryas-12_All.csv"
save_root = r"/mnt/archive/Workspace_Hjalte/MaskRCNN/2020_01_22_VisitorDetectionOnFlowers_DetectionPhenologyTestSeries/collages_Monster_Final/"

flowers_and_visitors = camyear + "_" + "flowers_and_visitors_Temp.csv"


### USER SETTINGS ###
upscale_factor = 1 # Use this if the coordinates for the detections need to be upscaled
crops_per_collage = 4 # Number of flower crops in each collage
known_visitor_percentage = 0.5 # So far, we have used 2% known visitors. However, as we are presenting four crops at a time, we can divide this by 4.
collages_per_folder = 50000 # Number of collages per folder

### Mixing in known insects ###
"""
To mix in known insects, we will 
-open the flower detections
-count the number of detections
-calculate number of known insect needed

-open insect annotations file
-sample the number needed
-add them to the flower detections
-mix the flower detections, so the insects appear randomly
-save the new flower detections file containing the known insects.
-Now the rest of the script can be run


"""

fl_detections = pd.read_csv(flower_detections, header = None) # Read the file containing the flower detections
fl_detections.columns=['filename', 'x_min', 'y_min', 'x_max', 'y_max'] # Name the columns
fl_detections['known_insect'] = str(0)


fl_detections['x_min'] = fl_detections['x_min']*upscale_factor # We might as well upscale the detection coordinates now we have the file open
fl_detections['y_min'] = fl_detections['y_min']*upscale_factor
fl_detections['x_max'] = fl_detections['x_max']*upscale_factor
fl_detections['y_max'] = fl_detections['y_max']*upscale_factor

fl_detections['x_min'] = fl_detections['x_min'].astype(int)
fl_detections['y_min'] = fl_detections['y_min'].astype(int)
fl_detections['x_max'] = fl_detections['x_max'].astype(int)
fl_detections['y_max'] = fl_detections['y_max'].astype(int)

det_count = fl_detections.shape[0] # Count the number of detections


visitors_needed = ceil(det_count/100 * known_visitor_percentage) # We calculate the number of known insects we need to add to the detection dataset. ceil rounds up to the next integer

if visitors_needed + det_count % crops_per_collage != 0: # If the combined number of images is not divisible by 4 (crops_per_collage), we will sample extra insects until it is. This ensures that we do not leave out any crops.
	visitors_needed = visitors_needed + (crops_per_collage -((visitors_needed + det_count) % crops_per_collage))

known_visitors = pd.read_csv(known_visitors, header = None)
known_visitors.columns=['filename', 'x_min', 'y_min', 'x_max', 'y_max']

#known_visitors = known_visitors[['filename', 'x_min', 'y_min', 'x_max', 'y_max']]
known_visitors['known_insect'] = str(1)

sampled_visitors = known_visitors.sample(n = visitors_needed, replace = True) # Sample the insect visitor crops
fl_detections_visitors =  pd.concat([fl_detections, sampled_visitors], axis=0) # Add them to the detection dataframe
fl_detections_visitors = fl_detections_visitors.sample(frac=1) # Mix the dataframe so the insects occur at random locations
fl_detections_visitors.to_csv(flowers_and_visitors, header = None, index = False) # Write the dataframe to csv


### PRINT SOME STUFF ###
number_flowers = len(fl_detections)
number_visitors_sampled = len(sampled_visitors)
number_collages = (number_flowers + number_visitors_sampled)//crops_per_collage
number_folders = (number_collages//collages_per_folder) + 1


print(f"Running on: {camyear}")
print(f"Number of flowers detected: {number_flowers}")
print(f"Number of visitors sampled: {number_visitors_sampled}")
print(f"Number of collages that will be produced: {number_collages}")
print(f"Number of folders that will hold the collages: {number_folders}")

###

manifest = []

def write_manifest(collage_name, list_of_crops, folder_name): # Write a manifest for the Zooniverse platform

	TL_Path = list_of_crops[0][0] # Get the paths for the image for each crop in a collage
	TR_Path = list_of_crops[1][0]
	BL_Path = list_of_crops[2][0]
	BR_Path = list_of_crops[3][0]
	
	TL_Coordinates = str(list_of_crops[0][1]) + "_" + str(list_of_crops[0][2]) + "_" + str(list_of_crops[0][3]) + "_" + str(list_of_crops[0][4]) # Get the coordinates for the detection in each image
	TR_Coordinates = str(list_of_crops[1][1]) + "_" + str(list_of_crops[1][2]) + "_" + str(list_of_crops[1][3]) + "_" + str(list_of_crops[1][4])
	BL_Coordinates = str(list_of_crops[2][1]) + "_" + str(list_of_crops[2][2]) + "_" + str(list_of_crops[2][3]) + "_" + str(list_of_crops[2][4])
	BR_Coordinates = str(list_of_crops[3][1]) + "_" + str(list_of_crops[3][2]) + "_" + str(list_of_crops[3][3]) + "_" + str(list_of_crops[3][4])

	TL_KnownInsect = list_of_crops[0][5] # Binary score of whether the crop is a known insect. 0: no, 1: yes.
	TR_KnownInsect = list_of_crops[1][5]
	BL_KnownInsect = list_of_crops[2][5]
	BR_KnownInsect = list_of_crops[3][5]

	row = [collage_name, TL_Path, TL_Coordinates, TL_KnownInsect, TR_Path, TR_Coordinates, TR_KnownInsect, BL_Path, BL_Coordinates, BL_KnownInsect, BR_Path, BR_Coordinates, BR_KnownInsect, folder_name] # Header row
	manifest.append(row)



def cut_crops(list_of_crops): # Function for cutting out the detection crops from the full images based on the bounding box coordinates
	crops = []
	for c in list_of_crops:
		
		image = cv2.imread(c[0])
		
		c_xmin = c[1]
		c_ymin = c[2]
		c_xmax = c[3]
		c_ymax = c[4]
		c_width = c_xmax - c_xmin
		c_height = c_ymax - c_ymin

		crop = image[c_ymin:c_ymin + c_height, c_xmin:c_xmin + c_width]
		crops.append(crop)
		
	return crops


def create_background(crops): # Create a background image in which the crops will be pasted to create a collage of four crops
	background_width = (max([crops[0].shape[0], crops[1].shape[0], crops[2].shape[0], crops[3].shape[0]]) * 2) + 50 # The width of the background image is 2*widest crop + 50 pixels
	background_height = (max([crops[0].shape[1], crops[1].shape[1], crops[2].shape[1], crops[3].shape[1]]) * 2) + 50 # The height of the background image is 2*tallest crop + 50 pixels

	background_image = Image.new("RGB", (background_height, background_width), (255,255,255)) # Create the background image

	# We'll draw a frame around the image and a cross in the middle'
	draw = ImageDraw.Draw(background_image) 
	draw.line((0,int(background_width/2), background_height, int(background_width/2)), fill=(0,0,0, 255), width=2) # draw.line([(left, top), (left, bottom), (right, bottom), (right, top), (left, top)]
	draw.line(((int(background_height/2), 0, int(background_height/2), background_width)), fill=(0,0,0, 255), width=2)
	draw.line(((0, 0, int(background_height), 0)), fill=(0,0,0, 255), width=2)
	draw.line(((1, int(background_width), 1, 0)), fill=(0,0,0, 255), width=2)
	draw.line(((int(background_height), int(background_width)-1, 0, int(background_width)-1)), fill=(0,0,0, 255), width=2)
	draw.line(((int(background_height)-2, 0,  int(background_height)-2, int(background_width))), fill=(0,0,0, 255), width=2)
	
	return background_image # And we are ready to return our background image


def paste_crops(background_image, crops): # Function for pasting crops in the background image
	index = 0
	background_height, background_width = background_image.size

	for c in crops:
		c = cv2.cvtColor(c, cv2.COLOR_BGR2RGB)
		c = Image.fromarray(c) 
		h, w = c.size
		
		if index == 0:
			x = int(background_width/4 - (w/2))
			y = int(background_height/4 -(h/2))
		elif index == 1:
			x = int(background_width/4 - (w/2))
			y = int((background_height/(4/3)) - (h/2))
		elif index == 2:
			x = int((background_width/(4/3)) - (w/2))
			y = int(background_height/4 -(h/2))
		else:
			x = int((background_width/(4/3)) - (w/2))
			y = int((background_height/(4/3)) - (h/2))

		background_image.paste(c, (y, x, y + h, x + w))
		collage = background_image
		
		index += 1

	return collage



######## PRODUCE CROP COLLAGES ######

collage_counter = 0 # Keep track of the number of collages produced
folder_counter = 0 # Keep track of the folder number
split_save_to = save_root + "/" + camyear + "_" + str(folder_counter)
os.makedirs(split_save_to)


with open(flowers_and_visitors, 'r') as csvfile:
	detections = csv.reader(csvfile, delimiter=',')
	lines = []
	
	collage_index = 0
	
	for line in detections:
		line = [int(int(i)*upscale_factor) if i.isdigit() else i.replace('O:/Tech_TTH-AID','/mnt/bitcue_mountpoint') for i in line] # Convert the coordinates to digits in the line
		lines.append(line)
		if len(lines) >= crops_per_collage:
			crops = cut_crops(lines)
			background_image = create_background(crops)
			collage = paste_crops(background_image, crops)
			
			collage_name = camyear + "_" + str(collage_index).zfill(6) + ".jpg"
			collage_path = split_save_to + "/" + collage_name
			folder_name = camyear + "_" + str(folder_counter)
			collage.save(collage_path)
			write_manifest(collage_name, lines, folder_name)
			
			collage_counter += 1
			collage_index += 1
			
			if collage_counter % 2500 == 0: # Print message to let the user know that the script is still running
				print("2500 mark. Still going strong...")    

			if collage_counter == collages_per_folder:
				print(str(collages_per_folder), " mark. Still going. Starting a new folder.")

				manifest = pd.DataFrame(manifest, columns = ["ID", "!TL_Path", "!TL_Coordinates", "!TL_KnownInsect","!TR_Path","!TR_Coordinates", "!TR_KnownInsect","!BL_Path","!BL_Coordinates", "!BL_KnownInsect", "!BR_Path", "!BR_Coordinates", "!BR_KnownInsect", "Folder_Name"])
				manifest.to_csv(save_root + "/" + "manifest" + "_" + camyear + "_" + str(folder_counter) + ".csv", index = False)

				manifest = []

				folder_counter += 1
				split_save_to = save_root + "/" + camyear + "_" + str(folder_counter)
				os.makedirs(split_save_to)
				collage_counter = 0
        
			lines = []
	if len(lines) > 0:
		print("Not included: \n", lines)

manifest = pd.DataFrame(manifest, columns = ["ID", "!TL_Path", "!TL_Coordinates", "!TL_KnownInsect","!TR_Path","!TR_Coordinates", "!TR_KnownInsect","!BL_Path","!BL_Coordinates", "!BL_KnownInsect", "!BR_Path", "!BR_Coordinates", "!BR_KnownInsect", "Folder_Name"])
manifest.to_csv(save_root + "/" + "manifest" + "_" + camyear + "_" + str(folder_counter) + ".csv", index = False)

print("Collages done. Sending e-mail.")

### SEND NOTIFICATION WHEN SCRIPT HAS FINISHED RUNNING ###
#import win32com.client as win32

# Setup E-mail stuff
#outlook = win32.Dispatch('outlook.application')
#mail = outlook.CreateItem(0)
#mail.To = 'mann@bios.au.dk'
#mail.Subject = 'Collages done! '
#mail.HTMLBody = f"Collages are saved at: {save_root}. Have a nice day."
#mail.Send()

print("All done")
### THE END ###







