# -*- coding: utf-8 -*-
"""
Created on Tue Apr  7 14:33:07 2020

@author: Daniel Teran
"""
#   Displays fits image, cuts out section, and fourier transforms

import numpy as np
import matplotlib.pyplot as plt
import scipy.ndimage as ndi
import os
from matplotlib.colors import LogNorm
from astropy.io import fits
from tkinter.filedialog import askopenfilename
from tkinter import Tk

Tk().withdraw()

#   Opens up file explorer to select the file
filePath = askopenfilename()
fileName = os.path.basename(filePath)
print("File Name:",fileName)

#   Opening fits file. Returns Header Data Unit(HDU) List (hdul: header and data array/table)
hdul = fits.open(filePath)

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

print(len(imageArray[0]), "values in the X axis")
print(len(imageArray), "values in the Y axis")

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

#   Loop to set proper values in original image to new zoomed image
#   array
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

#   Array for median filtered image
medianImage = ndi.median_filter(zoomedArray, size = 2)

#   Empty array for the barber pole and median values
barber = np.zeros(len(zoomedArray))
medValArray = np.zeros(shape = (len(zoomedArray), len(zoomedArray[0])))

#   Find median value in image array
medval = np.median(medianImage)

#   Subtracting median value from all values in array
i = 0
j = 0
for i in range(len(medianImage)):
    for j in range(len(medianImage[i])):
        medValArray[i][j] = medianImage[i][j] - medval

#   Finding average pixel count for each column and determining highest 
#   average and getting location
averageArray = np.mean(medValArray, axis = 0)
i = 0
highestAverage = 0
xCoord = 0
for i in range(len(averageArray)):
    if (averageArray[i] > highestAverage):
        highestAverage = averageArray[i]
        xCoord = i

#   Filling barber array with vertical values of x coordinate location of 
#   highest values
i = 0
for i in range(len(medianImage)):
    barber[i] = medValArray[i][int(xCoord)]
    
#   Creating the 2d Hanning window
hann1 = np.hanning(len(medValArray))
hann2 = np.hanning(len(medValArray[0]))
hann2d = np.sqrt(np.outer(hann1, hann2))
hannWin = hann2d * medValArray

#   Fourier Transforming
f = np.fft.fft2(hannWin)

#   Shifting zero frequency component to center spectrum
fshift = np.fft.fftshift(f)

#   Visual representation of Fourier Transform
fourierImage = np.log(np.abs(fshift))

#   Displaying all the images
#   Fits
plt.imshow(zoomedArray, origin = 'lower', cmap = 'gray')
plt.title("Zoomed Image")
plt.xlabel("Pixel No.")
plt.ylabel("Pixel No.")
plt.show(block = True)

#   Median
plt.imshow(medianImage, origin = 'lower', cmap = 'gray', norm = LogNorm())
plt.title("Median Filtered Image")
plt.xlabel("Pixel No.")
plt.ylabel("Pixel No.")
plt.show(block=True)

#   Average Subtracted
plt.imshow(medValArray, origin = 'lower', cmap = 'gray')
plt.title("Median Value Subtracted")
plt.xlabel("Pixel No.")
plt.ylabel("Pixel No.")
plt.show(block=True)

#   Hanning Window
plt.imshow(hannWin, origin = 'lower', cmap = 'gray')
plt.title("Hanning Window Output")
plt.xlabel("Pixel No.")
plt.ylabel("Pixel No.")
plt.show(block=True)

#   2D Fourier Transform
plt.imshow(fourierImage, origin ='lower', cmap='gray')
plt.title("Fourier Image")
plt.xlabel("Pixel No.")
plt.ylabel("Pixel No.")
plt.show(block=True)

#   Take row cut of bright pixel in transform image and plot intensity as
#   function of x
rowLocation = input("Enter Y value to take slice from: ")
rowValues = fourierImage[int(rowLocation)]
plt.plot(rowValues)
plt.title("Row Values Plotted")
plt.show(block = True)

"""
#   FUNCTION TO SEARCH FOR THAT BRIGHT PIXEL ROW ON ITS OWN
highXCoordLoc = 0
highYCoordLoc = 0
highValue = 0
i = 0
j = 0
while j < vertLength / 2:
    while i < horizLength:
        if (fourierImage[j][i] > highValue):
            highValue = fourierImage[j][i]
            highXCoordLoc = i
            highYCoordLoc = j
        i += 1
    j += 1
    
print(highValue, " ", highXCoordLoc, " ", highYCoordLoc)
print(fourierImage[highXCoordLoc,highYCoordLoc])
"""

#   Closing file
hdul.close()

print ("End of program")