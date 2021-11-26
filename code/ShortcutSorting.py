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


directory = r'../images/ShortcutSorting' # Path to folder with images for sorting


folderMap = {'1': "Empty", '2': "Maybe", '3': "Insect"}

####
## HARD SETTINGS
####

pygame.init()

info = pygame.display.Info()
width, height = info.current_w, info.current_h

imageDisplay_width, imageDisplay_height = 1040, 1040 #int(width/2), int(height/2)

imageDisplay = pygame.display.set_mode((0,0), pygame.FULLSCREEN)# (imageDisplay_width,imageDisplay_height), pygame.RESIZABLE)
#pygame.display.set_caption('Fast manual sorting')

#x, y =  (imageDisplay_width * 0.15), (imageDisplay_height * 0.2)
x, y =  600, 40 # Coordinates for image position in program window


#####
## DEFINE SOME FUNCTIONS
#####

pp = (os.path.join(directory, file) for file in os.listdir(directory) if file.endswith((".jpg", ".JPG", ".png", ".PNG"))) # Generator for feeding images

def displayImage(img, x,y):
    imageDisplay.blit(img, (x,y))

def kill():
    pygame.quit()
    sys.exit()

def createFolders(folderMap):
    for f in list(folderMap.values()):
        if not os.path.exists(os.path.join(directory,f)):
            os.mkdir(os.path.join(directory,f))

def copyImage(keyPressed, image):
    src = image
    dst = os.path.join(directory, folderMap[keyPressed])
    shutil.copy(src, dst)
 
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

# Stuff for displaying folder info text
font = pygame.font.Font('freesansbold.ttf', 32)
text = font.render(str(folderMap).replace('{', '').replace(',', '').replace('}', '').replace("'", ''), True, (255, 255, 255), (0, 0, 0)) # create a text surface object, on which text is drawn on it.
textRect = text.get_rect()# create a rectangular object for the text surface object
textRect.center = (x // 2, y // 2) # set the center of the rectangular object.

def run():
    """ The main program"""
    createFolders(folderMap) # Create the folders
    image = next(pp) # Grab the first image from the generator      
    while True:     
        displayImage(text, 0,0)
        
        picture = pygame.image.load(image)
        picture = pygame.transform.scale(picture, (1400, 1400))
        
        displayImage(picture, x, y)
        pygame.display.update()  
        keyPressed = waitKeypress()
        keyPressed = str(ast.literal_eval(keyPressed)[0]) # Key 1 returns '1' but numpad 1 returns '[1]' so we'll check if the string is a list, if so we'll grab first (and only) instance and convert to string.
        copyImage(keyPressed, image)

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