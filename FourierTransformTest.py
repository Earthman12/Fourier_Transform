# -*- coding: utf-8 -*-
"""
Created on Wed Jun 24 11:08:59 2020

@author: Earthman
"""


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

#   Finding average pixel count for each column and determining highest 
#   average and getting location
averageArray = np.mean(imageArray, axis = 0)
i = 0
highestAverage = 0
xCoordCenter = 0
for i in range(len(averageArray)):
    if (averageArray[i] > highestAverage):
        highestAverage = averageArray[i]
        xCoordCenter = i

#   Filling barber array with column(barber pole) values of x coordinate
#   location of highest average values
print("X center is determined by column in array with highest pixel average also sets barber pole location, pixel no.:", xCoordCenter)
barber = np.zeros(len(imageArray))
i = 0
for i in range(len(imageArray)):
    barber[i] = imageArray[i][int(xCoordCenter)]

#   Find Y coordinate for brightest pixel in barber pole
yCoordCenter = 0
yHighVal = 0
i = 0
for i in range(len(barber)):
    if (barber[i] > yHighVal):
        yHighVal = barber[i]
        yCoordCenter = i
print("Y center is determined by highest value in barber pole, pixel no.:", yCoordCenter)

#   Search for edge boundries of interferogram to be able to transform whole
#   thing and not have to ask for horizontal input from user
#   POSSIBLE WAY TO DO THIS:
#   LOOP THROUGH EACH COLUMN(X) TAKING AVERAGE OF EACH COLUMN AND THEN TAKE
#   AVERAGE OF ALL THE AVERAGES 
i = 0
xLowLim = 0 
xHighLim = len(averageArray) #Limits set to edges initially
averageOfAverageArray = np.mean(averageArray)
checkLimit = False
while(checkLimit == False):#Check left limit
    if(averageArray[i] > averageOfAverageArray):
        xLowLim = i
        checkLimit = True
    i += 1

i = len(averageArray) - 1
checkLimit = False
while(checkLimit == False):#Check right limit
    if(averageArray[i] > averageOfAverageArray):
        xHighLim = i
        checkLimit = True
    i -= 1
    
print("Interferogram X limits calculated to be between pixels:", xLowLim,"-", xHighLim)

#   Get horizontal limits of zoom and converting to integers
horizLength = input("Enter horizontal length: ")
horizLength = int(horizLength)
#   Empty array for new zoomed image
zoomedArray = np.zeros(shape = (len(imageArray), horizLength))

#   Setting X and Y corner coordinates
startX = xCoordCenter - int(horizLength / 2)
endX = xCoordCenter + int(horizLength / 2)
startY = 0
endY = len(imageArray)
#   Checking to make sure they are within image boundaries
if(startX < 0):
    startX = 0
if(endX > len(imageArray[0])):
    endX = len(imageArray[0])

#   If the lengths are odd, add one to end edges cause it wont reach
#   in the loop below
if(horizLength % 2 != 0):
    endX += 1

#   Loop to set proper values in original image to new zoomed image
#   array
i = startX
j = startY
x = 0
y = 0
while (i < endX):
    while (j < endY):
        zoomedArray[y][x] = imageArray[j][i]
        j += 1
        y += 1
    y = 0
    j = startY
    i += 1
    x += 1

#   Array for median filtered image
medianImage = ndi.median_filter(zoomedArray, size = 2)

#   Empty array for the median values
medValArray = np.zeros(shape = (len(zoomedArray), len(zoomedArray[0])))

#   Find median value in image array
medval = np.median(medianImage)

#   Subtracting average value from all values in array
i = 0
j = 0
for i in range(len(medianImage)):
    for j in range(len(medianImage[i])):
        medValArray[i][j] = medianImage[i][j] - medval

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

#   Barber Pole Values
#   Plotting barber pole values
plt.plot(barber)
plt.title("Barber Pole Values")
plt.show(block = True)

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

#   Searching for brightest pixel in 4th quadrant of transform
startX = len(fourierImage[0]) / 2 #center
endX = len(fourierImage[0]) #right end
startY = 0                  #bottom
endY = len(fourierImage) / 2 #center
startX = int(startX) #Values set to floats in call above, must be integers
endY = int(endY)
highestPixel = 0
i = startX
j = startY
yRow = 0

while(i < endX):
    while(j < endY):
        if(fourierImage[j][i] > highestPixel):
            highestPixel = fourierImage[j][i]
            yRow = j
        j += 1
    j = startY
    i +=1
    
print("Y value location with brightest pixel in transform:", yRow)

#   Take row cut of bright pixel in transform image and plot intensity as
#   function of x
rowValues = fourierImage[yRow]
plt.plot(rowValues)
plt.title("Row Values Plotted")
plt.show(block = True)

#   Closing file
hdul.close()

print ("End of program")