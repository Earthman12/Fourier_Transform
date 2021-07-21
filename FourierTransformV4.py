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

def Interferogram(image):
##############################################################################
#   SEARCHES FOR EDGES OF INTERFEROGRAM TO AVOID USER INPUT
#   LOOP THROUGH EACH COLUMN(X) AND ROW(Y) TAKING AVERAGE OF EACH AND 
#   SETS BOUNDARY WHERE COLUMN/ROW BECOMES GREATER THAN AVERAGE
    
    averageColumnArray = np.mean(imageArray, axis = 0)
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
    
    #           LOOP THROUGH EACH ROW(Y) TAKING AVERAGE OF EACH INTO ARRAY
    averageRowArray = np.mean(imageArray, axis = 1)
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
    
    #           SET ZOOMED INTERFEROGRAM VALUES FUNCTION
    interferogramArray = np.zeros(shape = (yHighLim-yLowLim, xHighLim-xLowLim))
    x = 0
    y = 0
    for i in range(xLowLim, xHighLim, 1):
        for j in range(yLowLim, yHighLim, 1):
            interferogramArray[y][x] = imageArray[j][i]
            y += 1
        y = 0
        j = yLowLim
        x += 1

    return interferogramArray
    
##############################################################################
    
def WaveChecker(image):
    
    result = True
    n = len(image)
  
    # Check the wave form 
    # If arr[1] is greater than  
    # left and right. Same pattern  
    # will be followed by whole  
    # elements, else reverse pattern 
    # will be followed by array elements 
      
    if (image[1] > image[0] and image[1] > image[2]): 
        for i in range(1, n - 1, 2): 
  
            if (image[i] > image[i - 1] and 
                image[i] > image[i + 1]): 
                result = True
          
            else : 
                result = False
                break
  
        # Check for last element 
        if (result == True and n % 2 == 0): 
            if (image[n - 1] <= image[n - 2]) : 
                result = False
              
    elif (image[1] < image[0] and
          image[1] < image[2]) : 
        for i in range(1, n - 1, 2) : 
  
            if (image[i] < image[i - 1] and 
                image[i] < image[i + 1]): 
                result = True
              
            else : 
                result = False
                break
  
        # Check for last element 
        if (result == True and n % 2 == 0) : 
            if (image[n - 1] >= image[n - 2]) : 
                result = False
  
    return result 
    
##############################################################################
    
def HanningWindow(image):
    #   Creates the 2d Hanning window
    
    hann1 = np.hanning(len(medValArray))
    hann2 = np.hanning(len(medValArray[0]))
    hann2d = np.sqrt(np.outer(hann1, hann2))
    hannWin = hann2d * medValArray
    
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
#                           DRIVER CODE
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

interferogramArray = Interferogram(imageArray)

#                   FILTER/WINDOW/TRANSFORM FUNCTIONS
##############################################################################
#   Array for median filtered image
medianImage = ndi.median_filter(interferogramArray, size = 2)

#   Empty array for the median values
medValArray = np.zeros(shape = (len(interferogramArray), len(interferogramArray[0])))

#   Find median value in image array
medval = np.median(medianImage)

#   Subtracting average value from all values in array
for i in range(0, len(medianImage), 1):
    for j in range(0, len(medianImage[i]), 1):
        medValArray[i][j] = medianImage[i][j] - medval

hanningWindow = HanningWindow(medValArray)

fourierTransformImage = FourierTransform(hanningWindow)

#                   IMAGE DISPLAY FUNCTIONS
##############################################################################

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
plt.imshow(hanningWindow, origin = 'lower', cmap = 'gray')
plt.title("Hanning Window Output")
plt.xlabel("Pixel No.")
plt.ylabel("Pixel No.")
plt.show(block=True)

#   2D Fourier Transform
plt.imshow(fourierTransformImage, origin ='lower', cmap='gray')
plt.title("Fourier Image")
plt.xlabel("Pixel No.")
plt.ylabel("Pixel No.")
plt.show(block=True)

##############################################################################

rowValues = WavelengthFinder(fourierTransformImage)

#   Take row cut of bright pixel in transform image and plot intensity as
#   function of x
plt.plot(rowValues)
plt.title("Row Values Plotted")
plt.show(block = True)

#   Closing file
hdul.close()

print ("End of program")