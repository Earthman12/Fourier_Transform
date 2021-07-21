# -*- coding: utf-8 -*-
"""
Created on Fri Jun 19 13:00:03 2020

@author: Earthman
"""

##############################################################################

def file(openOrClose):
    
    filePath = askopenfilename()
    fileName = os.path.basename(filePath)
    
    #   Opening fits file. Returns Header Data Unit(HDU) List (hdul: header and data array/table)
    hdul = fits.open(filePath)
    if openOrClose == True:
        #   Primary HDU
        primHDU = hdul[0]
    
        #   Obtaining number of dimensions and determining if its 2 or 3 dimensional
        numDim = len(np.shape(primHDU))
        if(numDim == 2):
            imageArray = primHDU.data[:,:]
        elif(numDim == 3):
            imageArray = primHDU.data[0,:,:]    
    
        plt.imshow(imageArray, origin='lower', cmap='gray')
        plt.title(fileName + ' Fits Image')
        plt.xlabel("Pixel No.")
        plt.ylabel("Pixel No.")
        plt.show(block=True)
    
        print("File Name:",fileName)
        print(len(imageArray[0]), "values in the X axis")
        print(len(imageArray), "values in the Y axis")
        
        return imageArray
    
    else :
        hdul.close()
        print("End of program.")
        sys.exit(0)
    
##############################################################################
    
def zoomImage(imageArray):
    #   Creating a zoomed in array of fringes, getting center location 
    #   and putting into an array
    center = input("Choose fringe center X,Y values of zoomed image seperated by space: ")
    center = center.split()
    centerArray = np.zeros(shape = len(center), dtype = int)
    i = 0
    for i in range(len(centerArray)):
        centerArray[i] = center[i]
    
    centerXCoord = centerArray[0]
    centerYCoord = centerArray[1]
    
    #   Get horizontal and vertical limits of zoom and converting
    #   to integers
    horizLength = input("Enter horizontal length: ")
    vertLength = input("Enter vertical length: ")
    horizLength = int(horizLength)
    vertLength = int(vertLength)
    
    #   Empty array for new zoomed image
    zoomedArray = np.zeros(shape = (vertLength, horizLength))
    
    #   Setting X and Y coordinates and checking if it will be less 
    #   than zero, setting to 0 if negative
    startX = centerXCoord - int(horizLength / 2)
    endX = centerXCoord + int(horizLength / 2)
    startY = centerYCoord - int(vertLength / 2)
    endY = centerYCoord + int(vertLength / 2)
    if(startX < 0):
        startX = 0
    if(startY < 0):
        startY = 0
            
    #   If the lengths are odd, add one to end edges cause it wont reach
    #   in the loop below
    if(horizLength % 2 != 0):
        endX += 1
    if(vertLength % 2 != 0):
        endY += 1

    #   Loop to set proper values in original image to new zoomed image array
    i = startX
    j = startY
    x = 0
    y = 0
    while i < endX:
        while j < endY:
            zoomedArray[y][x] = imageArray[j][i]
            j += 1
            y += 1
        y = 0
        j = startY
        i += 1
        x += 1
        
    return zoomedArray
        
##############################################################################
    
def subAverageValue(image):
    
    avgValArray = np.zeros(shape = (len(image), len(image[0])))
    i = 0
    j = 0
    while j < len(image):
        while i < len(image[j]):
            avgValArray[j][i] = image[j][i] - np.median(image)
            i += 1
        j += 1
    
    return avgValArray
    
##############################################################################
    
def hanningWindow(image):
    
    hann1 = np.hanning(len(image))
    hann2 = np.hanning(len(image[0]))
    hann2d = np.sqrt(np.outer(hann1, hann2))
    hannWin = hann2d * image
    
    return hannWin

##############################################################################
    
def fourTransform(image):
    
    four = np.fft.fft2(image)
    fourShift = np.fft.fftshift(four)
    fourImage = np.log(np.abs(fourShift))
    
    return fourImage
    
##############################################################################
    
def displayImage(image, imageTitle):
    
    plt.imshow(image, origin = 'lower', cmap = 'gray')
    plt.title(imageTitle)
    plt.xlabel("Pixel No.")
    plt.ylabel("Pixel No.")
    plt.show(block = True)

##############################################################################
    
def plotSpectrum(image):
    
    rowLocation = input("Enter Y value to take slice from: ")
    rowValues = image[int(rowLocation)]
    plt.plot(rowValues)
    plt.title("Row Values Plotted")
    plt.show(block = True)
    
##############################################################################
    
import numpy as np
import matplotlib.pyplot as plt
import scipy.ndimage as ndi
import os
import sys
from astropy.io import fits
from tkinter.filedialog import askopenfilename
from tkinter import Tk

Tk().withdraw()

image = file(True)
zoomedImage = zoomImage(image)

#   Median filtered image
medianFilImage = ndi.median_filter(zoomedImage, size = 1)

#   Subtracted average valued image
subAvgValImage = subAverageValue(medianFilImage)

#   Apply Hanning Window
hanningImage = hanningWindow(subAvgValImage)

#   Fourier Transforming
fourierImage = fourTransform(hanningImage)

#   Display all images
displayImage(zoomedImage, "Zoomed Image")
displayImage(medianFilImage, "Median Filtered Image")
displayImage(subAvgValImage, "Average Value Subtracted From All Values")
displayImage(hanningImage, "Hanning Window")
displayImage(fourierImage, "Fourier Transform")

plotSpectrum(fourierImage)

#   Close file
file(False)