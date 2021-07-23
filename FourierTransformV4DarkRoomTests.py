#FOURIER TRANSFORM CODE

def subAverage(image):
    
    print("SUBTRACTING AVERAGE VALUE FROM IMAGE...")
    
    subAverageImage = np.zeros(shape = (len(image), len(image[0])))
    averageVal = np.median(image)
    
    for i in range(0, len(subAverageImage), 1):
        for j in range(0, len(subAverageImage[0]), 1):
            subAverageImage[i][j] = image[i][j] - averageVal
        
    return subAverageImage
    
##############################################################################
   
def HanningWindow(image):
    
    print("APPLYING HANNING WINDOW...")
    
    #   Creates the 2d Hanning window
    hann1 = np.hanning(len(image))
    hann2 = np.hanning(len(image[0]))
    hann2d = np.sqrt(np.outer(hann1, hann2))
    hannWin = hann2d * image
    
    return hannWin
    
##############################################################################
    
def FourierTransform(image):
    
    print("FOURIER TRANSFORMING...")
    
    #   Fourier Transforming
    f = np.fft.fft2(image)
    #   Shifting zero frequency component to center spectrum
    fshift = np.fft.fftshift(f)
    
    powerSpectrum = (np.abs(fshift) ** 2)
    
    #   Visual representation of Fourier Transform
    fourierImage = np.log10(powerSpectrum)
    
    return fourierImage
    
##############################################################################
    
def displayImage(image, title):
    
    if (title == "Median Filtered Image"):#Median filter has log norm
        plt.imshow(image, origin='lower', cmap='gray',  norm = LogNorm())
        plt.title(title)
        plt.xlabel("Pixel No.")
        plt.ylabel("Pixel No.")
        plt.show(block=True)
    
    else:
        plt.imshow(image, origin='lower', cmap='gray', vmin = np.min(image), vmax = np.max(image))
        plt.title(title)
        plt.xlabel("Pixel No.")
        plt.ylabel("Pixel No.")
        plt.show(block=True)
        
##############################################################################

def cropImage(image):
    
    print("CROPPING IMAGE...")
    
    xMin = 100
    xMax = 965
    yMin = 400
    yMax = 750
    
    croppedImage = np.zeros(shape = (yMax-yMin, xMax-xMin))
    
    i = xMin
    j = yMin
    x = 0
    y = 0
    while(i < xMax):
        while(j < yMax):
            croppedImage[y][x] = image[j][i]
            j += 1
            y += 1
        y = 0
        j = yMin
        i += 1
        x += 1
        
    return croppedImage

##############################################################################

def rowCut(transform):
    
    print("TAKING A SLICE OF THE TRANSFORM...")
    
    yRow = input("Choose Y row to take slice of: ")
    yRow = int(yRow)
    
    rowCutValuesArray = np.zeros(shape = len(transform[yRow]))
    
    for i in range(0, len(rowCutValuesArray), 1):
        #   TAKE ABSOLUTE VALUE OF TOP, MID, & BOTTOM
        absTop = abs(transform[yRow + 1][i])
        absMid = abs(transform[yRow][i])
        absBot = abs(transform[yRow - 1][i])
        #   SQUARE TOP, MID, & BOTTOM
        squareTop = absTop * absTop
        squareMid = absMid * absMid
        squareBot = absBot * absBot
        #   ADD THEM TOGETHER
        rowCutValuesArray[i] = squareTop + squareMid + squareBot
        
    plt.plot(rowCutValuesArray)
    plt.ylim(np.min(rowCutValuesArray), np.max(rowCutValuesArray))
    plt.title("Row " + str(yRow) + " Values")
    
    return rowCutValuesArray
    
##############################################################################

def debias(image):
    
    print("DEBIASING INTERFEROGRAM...")
    
    #Co-add images together and makes average out of it which is subtracted from
    #the original image
    #biasStack = np.zeros(shape = (len(image), len(image[0])))
    
    filePath = '.\Dark_Room_Files\CleanedBias_16sReadout.fits'
    
    biasImageHDUL = fits.open(filePath)
    biasImagePrimHDU = biasImageHDUL[0]
    biasImage = biasImagePrimHDU.data[:,:]
    
    displayImage(biasImage, 'CleanBias_16sReadout.fits')
    
    debiasImage = image - biasImage
    
    return debiasImage
    
##############################################################################

def subMinVal(image):
    
    print("SUBTRACTING MINIMUM VALUE FROM THE IMAGE...")
    
    sub_min_val_image = image - np.min(image)
    
    return sub_min_val_image
    
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
from astroscrappy import detect_cosmics

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
displayImage(imageArray, ("Original " + fileName + " Image"))
print(len(imageArray[0]), "values in the X axis")
print(len(imageArray), "values in the Y axis")

#   Detect cosmic rays
cosmic_array = detect_cosmics(imageArray, sigclip = 5.0, sigfrac = 0.3, readnoise = 10.0, gain = 2.2, satlevel = 65536, niter = 4, cleantype ='meanmask' , fsmode='median',sepmed=True, psfmodel='gauss', psffwhm =2.5, psfsize =7)
cosmic_array_image = cosmic_array[1]
displayImage(cosmic_array_image, "Cosmic image")

#   Debias image
debiasedImage = debias(imageArray)

#   Crops Image
croppedImage = cropImage(debiasedImage)
displayImage(croppedImage, "Cropped Image")

#   Median filtered image
#print("APPLYING MEDIAN FILTER...")
#medianImage = ndi.median_filter(croppedImage, size = 1)
#displayImage(medianImage, "Median Filtered Image")

#   Finding average value and subtracting it from each value 
#subAverageImage = subAverage(croppedImage)
#displayImage(subAverageImage, "Average Value Subtracted")

#   Subtracting the minimum value
sub_min_val_image = subMinVal(croppedImage)
displayImage(sub_min_val_image, "Minimum Value Subtracted Image")

#   Applying Hanning window
hanningWindow = HanningWindow(croppedImage)
displayImage(hanningWindow, "Hanning Window Output")

#   Fourier transforming
fourierTransformImage = FourierTransform(hanningWindow)
displayImage(fourierTransformImage, "Fourier Image")

#   Take row cut
rowCutValues = rowCut(fourierTransformImage)

#   Save row values to data file
saveFile = open("Spectrum_Values.dat", "w")
np.savetxt(saveFile, rowCutValues, fmt = '%.4e')

#   Closing file
hdul.close()

print ("End of program")