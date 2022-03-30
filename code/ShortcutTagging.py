# -*- coding: utf-8 -*-
"""
Created September 2021

@author: Hjalte Mann, TECOLOGY.xyz
"""

import pygame
import os
import sys
import shutil 
import ast

####
## USER SETTINGS
####

#directory = r'../images/ShortcutSorting' # Path to folder with images for sorting
directory = r'O:\Tech_TTH-Lab\Hjalte\PollinatorWatch\InsectCollection\Insect'
resultsFilepath = r'O:\Tech_TTH-Lab\Hjalte\PollinatorWatch\InsectCollection\Insect/LocationTags.csv'

with open(resultsFilepath, 'a') as resultFile: # Write the header of the output file
    header = 'collageName, insectCropLocation\n'
    resultFile.write(header)

tagMap = {'1': "BL", '3': "BR", '7': "TL", '9': "TR", '5': "Several", '4': "Maybe"}


img_w, img_h = 1200, 1200

####
## HARD SETTINGS
####4

pygame.init()

info = pygame.display.Info()
width, height = info.current_w, info.current_h

imageDisplay_width, imageDisplay_height = 1040, 1040 #int(width/2), int(height/2)

imageDisplay = pygame.display.set_mode((0,0), pygame.FULLSCREEN)# (imageDisplay_width,imageDisplay_height), pygame.RESIZABLE)
pygame.display.set_caption('Fast manual sorting')

#x, y =  (imageDisplay_width * 0.15), (imageDisplay_height * 0.2)
x, y =  600, 120 # Coordinates for image position in program window

#####
## DEFINE SOME FUNCTIONS
#####

imgList = sorted([file for file in os.listdir(directory) if file.endswith((".jpg", ".JPG", ".png", ".PNG"))])
pp = (os.path.join(directory, file) for file in imgList) # Generator for feeding images

def displayImage(img, x,y):
    imageDisplay.blit(img, (x,y))

def kill():
    pygame.quit()
    sys.exit()

# def createFolders(folderMap):
#     for f in list(folderMap.values()):
#         if not os.path.exists(os.path.join(directory,f)):
#             os.mkdir(os.path.join(directory,f))

# def copyImage(keyPressed, image):
#     src = image
#     dst = os.path.join(directory, tagMap[keyPressed])
#     shutil.move(src, dst)
#     print("Moved to: ", tagMap[keyPressed])
 
def waitKeypress():
    wait = True
    while wait:
        for event in pygame.event.get():
            if (event.type == pygame.QUIT):
                kill()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    kill()
            if event.type == pygame.KEYDOWN:
                wait = False
                return pygame.key.name(event.key)
                break

def showInfo(infoText):
    info = fontSmall.render(infoText, True, (255, 255, 255), (0, 0, 0)) # create a text surface object, on which text is drawn on it.
    infoRect = info.get_rect()# create a rectangular object for the text surface object
    infoRect.center = (x // 2, y // 2) # set the center of the rectangular object.
    return info


# Stuff for displaying folder info text
font = pygame.font.Font('freesansbold.ttf', 32)
fontSmall = pygame.font.Font('freesansbold.ttf', 16)
text = font.render(str(tagMap).replace('{', '').replace(',', '').replace('}', '').replace("'", ''), True, (255, 255, 255), (0, 0, 0)) # create a text surface object, on which text is drawn on it.
textRect = text.get_rect()# create a rectangular object for the text surface object
textRect.center = (x // 2, y // 2) # set the center of the rectangular object.


if not imgList: # If no images in directory, kill program.
    print("No images in directory. Killed program.")
    kill()

def run():
    """ The main program"""
    #createFolders(tagMap) # Create the folders
    left = len(imgList) + 1
    image = next(pp) # Grab the first image from the generator 
    
    while True:     
        displayImage(text, 0,0)
        displayImage(showInfo(image.split('\\')[-1]), 0,40)
        left -= 1
        displayImage(showInfo(f'Images left: {left}'), 0,80)
        
        
        collageFilename = image.split('\\')[-1]
        
        print(image)  
        picture = pygame.image.load(image)
        picture = pygame.transform.scale(picture, (img_w, img_h))
        
        displayImage(picture, x, y)
        pygame.display.update()  
        keyPressed = waitKeypress()
        keyPressed = str(ast.literal_eval(keyPressed)[0]) # Key 1 returns '1' but numpad 1 returns '[1]' so we'll check if the string is a list, if so we'll grab first (and only) instance and convert to string.
        tag = tagMap[keyPressed]
        
        with open(resultsFilepath, 'a') as resultFile:
            resultFile.write(f'{collageFilename}, {tag}\n')
        
        
        
        try:
            image = next(pp) # Grab the next image from the generator
        except StopIteration: # We'll catch the StopIteration from the generator when it has no more images to feed and kill the program.
            print("ALL DONE!")
            kill()
    kill()

####
## RUN
####

pygame.event.clear() # Clear event cache
run()

####
###
##
#
