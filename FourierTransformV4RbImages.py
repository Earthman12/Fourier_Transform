# -*- coding: utf-8 -*-
"""
Created on Mon Jul 13 11:10:31 2020

@author: Earthman
"""

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

def Interferogram(image, fileName):
    
    if(fileName == "RB1.FIT"):
        #SET BOUNDS OF INTERFEROGRAM AUTOMATICALLY AND RETURN IT
        xLow = 31
        xHigh= 439
        yLow = 5
        yHigh = 197
        print("Interferogram between pixels: X:", xLow, "-", xHigh, "and Y:", yLow, "-", yHigh, "Total:", xHigh - xLow, "x", yHigh - yLow)
    
    elif (fileName == "rb2(1).fit"):
        #DO SAME WITH THIS AND SET BOUNDS AND RETURN
        xLow = 51
        xHigh= 324
        yLow = 4
        yHigh = 199
        print("Interferogram between pixels: X:", xLow, "-", xHigh, "and Y:", yLow, "-", yHigh, "Total:", xHigh - xLow, "x", yHigh - yLow)

    else:       
        print("Code does not support this file")
        raise SystemExit

    interferogramImage = setImage(image, xLow, xHigh, yLow, yHigh)
    
    return interferogramImage
    
##############################################################################

def subAverage(image):
    
    subAverageImage = np.zeros(shape = (len(image), len(image[0])))
    averageVal = np.median(image)
    
    for i in range(0, len(subAverageImage), 1):
        for j in range(0, len(subAverageImage[0]), 1):
            subAverageImage[i][j] = image[i][j] - averageVal
        
    return subAverageImage
    
##############################################################################
   
def HanningWindow(image):
    #   Creates the 2d Hanning window
    
    hann1 = np.hanning(len(image))
    hann2 = np.hanning(len(image[0]))
    hann2d = np.sqrt(np.outer(hann1, hann2))
    hannWin = hann2d * image
    
    return hannWin
    
##############################################################################
    
def FourierTransform(image):
    
    #   Fourier Transforming
    f = np.fft.fft2(image)
    #   Shifting zero frequency component to center spectrum
    fshift = np.fft.fftshift(f)    
    #   Visual representation of Fourier Transform
    fourierImage = np.log(np.abs(fshift))
    
    return fourierImage
    
##############################################################################
    
def WavelengthFinder(transform):
    
    #   Searching for brightest pixel in 4th quadrant of transform
    startX = len(transform[0]) / 2 #X center
    endX = len(transform[0]) #right end
    startY = 0                  #bottom
    endY = len(transform) / 2 #Y center
    startX = int(startX) #Values set to floats in call above, must be integers
    endY = int(endY)
    highestPixel = 0
    i = startX
    j = startY
    yRow = 0
    
    for i in range(startX, endX, 1):
        for j in range(startY, endY, 1):
            if(transform[j][i] > highestPixel):
                highestPixel = transform[j][i]
                yRow = j
        j = startY
        
    print("Brightest pixel in fourth quadrant of transform located in row:", yRow)
    
    #   Values from bright pixel row are stored in seperate array after taking
    #   the absolute value of each value in row and its corresponding value 
    #   above and below, squaring them, and then adding them together into 
    #   the seperate array
    addedValuesArray = np.zeros(shape = len(transform[yRow]))
    
    for i in range(0, len(addedValuesArray), 1):
        #   TAKE ABSOLUTE VALUE OF TOP, MID, & BOTTOM
        absTop = abs(transform[yRow + 1][i])
        absMid = abs(transform[yRow][i])
        absBot = abs(transform[yRow - 1][i])
        #   SQUARE TOP, MID, & BOTTOM
        squareTop = absTop * absTop
        squareMid = absMid * absMid
        squareBot = absBot * absBot
        #   ADD THEM TOGETHER
        addedValuesArray[i] = squareTop + squareMid +squareBot
        
    return addedValuesArray
    
##############################################################################
    
def setImage(image, xLow, xHigh, yLow, yHigh):
    
    x = 0
    y = 0
    newImage = np.zeros(shape = (yHigh - yLow, xHigh - xLow))
    
    for i in range(xLow, xHigh, 1):
        for j in range(yLow, yHigh, 1):
            newImage[y][x] = image[j][i]
            y += 1
        y = 0
        x += 1
        
    return newImage
    
##############################################################################
    
def resolvePower(plotValues):
    
    #TWO LINES THAT ARE IN INTERFEROGRAM: 6298.3252A and 6299.2245A
    waveDiff = 6299.2245 - 6298.3252
    
    #NEED TO FIND LOCATION OF TWO PEAKS. RB1.FIT: px240 & px266.
    #                                    rb2(1).fit: px161 & px178
    #dataExtreme IS ARRAY OF PEAK LOCATIONS IN PLOT ARRAY
    dataExtreme = sig.find_peaks(plotValues, height = 500, distance = 10)
    peakValueLocs = dataExtreme[0]
    
    print("Two peaks in plot calculated to be at pixel", peakValueLocs[0], "& pixel", peakValueLocs[1], "corresponding to lines 6298.3252Å & 6299.2245Å")
    peakDiff = peakValueLocs[1] - peakValueLocs[0]
    
    resolvingPower = waveDiff / peakDiff
    print("The resolving power is calculated to be:", round(resolvingPower, 6), "Å/pixel")
        
##############################################################################
    
def displayImage(image, title):
    
    if (title == "Median Filtered Image"):#Median filter has log norm
        plt.imshow(image, origin='lower', cmap='gray', norm = LogNorm())
        plt.title(title)
        plt.xlabel("Pixel No.")
        plt.ylabel("Pixel No.")
        plt.show(block=True)
    
    else:
        plt.imshow(image, origin='lower', cmap='gray')
        plt.title(title)
        plt.xlabel("Pixel No.")
        plt.ylabel("Pixel No.")
        plt.show(block=True)
    
##############################################################################
    
#                           DRIVER CODE
#   Displays fits image, cuts out section with the interferogram, and fourier transforms
import numpy as np
import matplotlib.pyplot as plt
import scipy.ndimage as ndi
import scipy.signal as sig
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
imageArray = primHDU.data[:,:]

#   Displays Fits Image
displayImage(imageArray, fileName)

#   Interferogram image
interferogramArray = Interferogram(imageArray, fileName)
displayImage(interferogramArray, "Zoomed Interferogram Image")

#   Median filtered image
medianImage = ndi.median_filter(interferogramArray, size = 1)
displayImage(medianImage, "Median Filtered Image")

#   Finding average value and subtracting it from each value 
subAverageImage = subAverage(medianImage)
displayImage(subAverageImage, "Average Value Subtracted")

#   Applying Hanning window
hanningWindow = HanningWindow(subAverageImage)
displayImage(hanningWindow, "Hanning Window Output")

#   Fourier transforming
fourierTransformImage = FourierTransform(hanningWindow)
displayImage(fourierTransformImage, "Fourier Image")

#   Take row cut of bright pixel in transform image and plot intensity as
#   function of x
rowValues = WavelengthFinder(fourierTransformImage)
plt.plot(rowValues)
plt.title("Row Values Plotted")
plt.show(block = True)

#   Calculating the resolving power
resolvePower(rowValues)

#   Closing file
hdul.close()

print ("End of program")