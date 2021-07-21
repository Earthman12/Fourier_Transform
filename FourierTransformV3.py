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

#   Displays fits image, cuts out section with the interferogram, and fourier transforms

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

#   Displays Fits Image
plt.imshow(imageArray, origin='lower', cmap='gray')
plt.title(fileName + ' Fits Image')
plt.xlabel("Pixel No.")
plt.ylabel("Pixel No.")
plt.show(block=True)

print(len(imageArray[0]), "values in the X axis")
print(len(imageArray), "values in the Y axis")

#                   BARBER POLE FUNCTION
##############################################################################
#   Finding average pixel count for each column and determining highest 
#   average and getting location
#   NEEDS WORK DETERMINING IF ARRAY IS A BARBER POLE
averageColumnArray = np.mean(imageArray, axis = 0)
i = 0
highestColumnAverage = 0
xCoordCenter = 0
for i in range(len(averageColumnArray)):#Finds Barber Pole Location
    if (averageColumnArray[i] > highestColumnAverage):
        highestColumnAverage = averageColumnArray[i]
        xCoordCenter = i
barberPoleX = xCoordCenter
print("Barber pole X pixel center calculated to be:", barberPoleX)
#   Filling barber array with column(barber pole) values of x coordinate
#   location of highest average values
barber = np.zeros(len(imageArray))
i = 0
for i in range(len(imageArray)):
    barber[i] = imageArray[i][int(barberPoleX)]

#   Find Y coordinate for brightest pixel in barber pole
yCoordCenter = 0
yHighVal = 0
i = 0
for i in range(len(barber)):
    if (barber[i] > yHighVal):
        yHighVal = barber[i]
        yCoordCenter = i
print("Y center is determined by highest value in barber pole, pixel no.:", yCoordCenter)

#                   INTERFEROGRAM FUNCTION
##############################################################################
#   SEARCHES FOR EDGES OF INTERFEROGRAM TO AVOID USER INPUT
#   LOOP THROUGH EACH COLUMN(X) AND ROW(Y) TAKING AVERAGE OF EACH AND 
#   SETS BOUNDARY WHERE COLUMN/ROW BECOMES GREATER THAN AVERAGE
i = 0
xLowLim = 0 
xHighLim = len(averageColumnArray) #Limits set to edges initially
averageOfAverageColumnArray = np.mean(averageColumnArray)
checkLimit = False
while(checkLimit == False):#Check left limit
    if(averageColumnArray[i] > averageOfAverageColumnArray):
        xLowLim = i
        checkLimit = True
    i += 1

i = len(averageColumnArray) - 1
checkLimit = False
while(checkLimit == False):#Check right limit
    if(averageColumnArray[i] > averageOfAverageColumnArray):
        xHighLim = i
        checkLimit = True
    i -= 1
    
print("Interferogram X limits calculated to be between pixels:", xLowLim,"-", xHighLim, ". Total X pixels =", xHighLim - xLowLim)

#   LOOP THROUGH EACH ROW(Y) TAKING AVERAGE OF EACH INTO ARRAY
averageRowArray = np.mean(imageArray, axis = 1)
highestRowAverage = 0

i = 0
yLowLim = 0
yHighLim = len(averageRowArray)
averageOfAverageRowArray = np.mean(averageRowArray)
checkLimit = False
while(checkLimit == False):#Check bottom limit
    if(averageRowArray[i] > averageOfAverageRowArray):
        yLowLim = i
        checkLimit = True
    i += 1

i = len(averageRowArray) - 1
checkLimit = False
while(checkLimit == False):#Check top limit
    if(averageRowArray[i] > averageOfAverageRowArray):
        yHighLim = i
        checkLimit = True
    i -= 1

print("Interferogram Y limits calculated to be between pixels:", yLowLim, "-", yHighLim,". Total y pixels =", yHighLim - yLowLim)

#                   SET ZOOMED INTERFEROGRAM VALUES FUNCTION
##############################################################################
interferogramArray = np.zeros(shape = (yHighLim-yLowLim, xHighLim-xLowLim))
i = xLowLim
j = yLowLim
x = 0
y = 0
while(i < xHighLim):
    while(j < yHighLim):
        interferogramArray[y][x] = imageArray[j][i]
        j += 1
        y += 1
    y = 0
    j = yLowLim
    i += 1
    x += 1

#                   FILTER/WINDOW/TRANSFORM FUNCTIONS
##############################################################################
#   Array for median filtered image
medianImage = ndi.median_filter(interferogramArray, size = 2)

#   Empty array for the median values
medValArray = np.zeros(shape = (len(interferogramArray), len(interferogramArray[0])))

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

#                   IMAGE DISPLAY FUNCTIONS
##############################################################################
#   Barber Pole Values
plt.plot(barber)
plt.title("Barber Pole Values")
plt.show(block = True)

#   Interferogram
plt.imshow(interferogramArray, origin = 'lower', cmap = 'gray')
plt.title("Zoomed Interferogram Image")
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
plt.title("Average Value Subtracted")
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

##############################################################################
#   Searching for brightest pixel in 4th quadrant of transform
startX = len(fourierImage[0]) / 2 #X center
endX = len(fourierImage[0]) #right end
startY = 0                  #bottom
endY = len(fourierImage) / 2 #Y center
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
    
print("Brightest pixel in fourth quadrant of transform located in row:", yRow)

#   Take row cut of bright pixel in transform image and plot intensity as
#   function of x
rowValues = fourierImage[yRow]
plt.plot(rowValues)
plt.title("Row Values Plotted")
plt.show(block = True)

#   Closing file
hdul.close()

print ("End of program")