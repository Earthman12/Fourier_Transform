# -*- coding: utf-8 -*-
"""
Created on Wed Jul 21 09:52:55 2021

@author: Earthman
"""

import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas, NavigationToolbar2QT as NavigationToolbar
from matplotlib.colors import LogNorm
import numpy as np
import scipy.ndimage as ndi
import os
import sys
from astropy.io import fits
from tkinter.filedialog import askopenfilename
from tkinter import Tk
from astroscrappy import detect_cosmics
from PyQt5 import QtCore, QtGui, QtWidgets

################################################################################################################################
################################################################################################################################
################################################################################################################################

class MainWindow(QtWidgets.QMainWindow):
    
    def __init__(self, *args, **kwargs):
        
        super(MainWindow, self).__init__(*args, **kwargs)
        
        #   Original fits image canvas
        self.fits_image = FitsImageCanvas()
        #   Toolbar
        self.toolbar = NavigationToolbar(self.fits_image, self)
        #   Image name label
        self.image_name_label = QtWidgets.QLabel(self.fits_image.get_image_name())
        #   Open new image button
        self.open_button = QtWidgets.QPushButton("Open File")
        self.open_button.clicked.connect(self.change_fits_image_data)
        
        #   GUI Grid Layout
        self.layout = QtWidgets.QGridLayout()
        self.layout.addWidget(self.image_name_label, 0, 0)
        self.layout.addWidget(self.toolbar, 1, 0)
        self.layout.addWidget(self.fits_image, 2, 0)
        self.layout.addWidget(self.open_button, 3, 0)
        
        #   Central widget for everything to sit inside
        self.placeholder_widget = QtWidgets.QWidget()
        self.placeholder_widget.setLayout(self.layout)
        self.setCentralWidget(self.placeholder_widget)
        
        #   This will start the GUI in fullscreen
        #self.showMaximized()
        
        self.show()
        
    #--------------------------------------------------------------------------------------------------
    #----------------------------------MainWindow FUNCTIONS--------------------------------------------
    #--------------------------------------------------------------------------------------------------
        
    def change_fits_image_data(self):
        
        print("Changing FITS images")
        
        #   Clear the list of axes to get have fresh axes to draw on in case image size is different
        self.fits_image.axes.clear()
        
        #   Set the new image and set the array to the 'image_array' variable
        self.fits_image.image_array = self.fits_image.open_fits_image()
        #   Add subplot to the figure
        self.fits_image.axes.append(self.fits_image.figure.add_subplot(self.fits_image.rows, self.fits_image.col, 1))
        #   Set the new image array and transform to their display objects and set the min and max accordingly for the new image
        self.fits_image.original_display_object.set_data(self.fits_image.image_array)
        self.fits_image.original_display_object.set_clim(vmin = np.min(self.fits_image.image_array), vmax = np.max(self.fits_image.image_array))
        
        print('testers')
        
        #   Set new cosmics image
        self.fits_image.cosmic_image = self.fits_image.apply_cosmics()
        print('chonk')
        #   Add subplot to the figure
        self.fits_image.axes.append(self.fits_image.figure.add_subplot(self.fits_image.rows, self.fits_image.col, 2))
        #   Set the cosmic image to its display object
        self.fits_image.cosmic_display_object.set_data(self.fits_image.cosmic_image)
        self.fits_image.cosmic_display_object.set_clim(vmin = np.min(self.fits_image.cosmic_image), vmax = np.max(self.fits_image.cosmic_image))
        
        #   Set transform on the new image and set it the 'transform_image' variable
        self.fits_image.transform_image = self.fits_image.fourier_transform()
        #   Add subplot to the figure
        self.fits_image.axes.append(self.fits_image.figure.add_subplot(self.fits_image.rows, self.fits_image.col, 3))
        #   Set the new transform image to its display object variable        
        self.fits_image.transform_display_object.set_data(self.fits_image.transform_image)
        self.fits_image.transform_display_object.set_clim(vmin = np.min(self.fits_image.transform_image), vmax = np.max(self.fits_image.transform_image))
        
        #   Re-draw it on to the figure
        self.fits_image.draw()
        
        #   Update image name label
        self.image_name_label.setText(self.fits_image.get_image_name())
        
################################################################################################################################
################################################################################################################################
################################################################################################################################
    
class FitsImageCanvas(FigureCanvas):
    
    def __init__(self, parent = None):
        
        #   Figure variables
        self.figure = Figure(figsize = (20,10))
        self.axes = []
        self.rows = 1
        self.col = 3
        
        #   Original Fits Image variables
        self.image_name = ''
        self.image_array = self.open_fits_image()
        #   Adding subplot to the figure
        self.axes.append(self.figure.add_subplot(self.rows, self.col, 1))
        #   Display object variable for fits image
        self.original_display_object = self.axes[0].imshow(self.image_array, origin='lower', cmap='gray', vmin = np.min(self.image_array), vmax = np.max(self.image_array))
        
        #   Cosmic Filtered Fits Image Variables
        self.cosmic_image = self.apply_cosmics()
        #   Add subplot to figure
        self.axes.append(self.figure.add_subplot(self.rows,self.col,2))
        #   Display object variable for cosmic image
        self.cosmic_display_object = self.axes[1].imshow(self.cosmic_image, origin='lower', cmap='gray', vmin = np.min(self.cosmic_image), vmax = np.max(self.cosmic_image))
        
        #   Transform Image Variables
        self.transform_image = self.fourier_transform()
        #   Add subplot to figure
        self.axes.append(self.figure.add_subplot(self.rows,self.col, 3))
        #   Display object variable for transform image
        self.transform_display_object = self.axes[2].imshow(self.transform_image, origin='lower', cmap='gray', vmin = np.min(self.transform_image), vmax = np.max(self.transform_image))
        
        super(FitsImageCanvas, self).__init__(self.figure)
        
    #--------------------------------------------------------------------------------------------------
    #----------------------------------ImageCanvas FUNCTIONS-------------------------------------------
    #--------------------------------------------------------------------------------------------------
        
    def open_fits_image(self):
        
        #   Not having Tk().withdraw() does not make the code execute properly, not completely sure why, but it is necessary
        Tk().withdraw()
        #   Opens up file explorer to select the file
        file_path = askopenfilename()
        file_name = os.path.basename(file_path)
        
        print("File Name:",file_name)
        self.image_name = file_name

        #   Opening fits file. Returns Header Data Unit(HDU) List (hdul: header and data array/table)
        hdul = fits.open(file_path)

        #   Primary HDU
        primary_HDU = hdul[0]
        image_array = primary_HDU.data[:,:]
        
        print("Variable type: " + str(type(image_array)))
        print(len(image_array[0]), "values in the X axis")
        print(len(image_array), "values in the Y axis")
        
        return image_array
    
    ##############################################################################
    
    def get_image_name(self):
        
        return self.image_name
    
    ##############################################################################
    
    def fourier_transform(self):
        
        print("Transforming image")
        
        #   Fourier Transforming
        f = np.fft.fft2(self.image_array)
        #   Shifting zero frequency component to center spectrum
        fshift = np.fft.fftshift(f)
        
        powerSpectrum = (np.abs(fshift) ** 2)
        
        #   Visual representation of Fourier Transform
        fourierImage = np.log10(powerSpectrum)
        
        return fourierImage
    
    ##############################################################################
    
    def apply_cosmics(self):
        
        print("Applying cosmics filter...")
        
        #   Detect cosmic rays
        cosmic_array = detect_cosmics(self.image_array, sigclip = 5.0, sigfrac = 0.3, readnoise = 10.0, gain = 2.2, satlevel = 65536, niter = 4, cleantype ='meanmask' , fsmode='median',sepmed=True, psfmodel='gauss', psffwhm =2.5, psfsize =7)
        cosmic_array_image = cosmic_array[1]
        
        return cosmic_array_image
    
################################################################################################################################
################################################################################################################################
################################################################################################################################

def main():
    
    #   Every GUI must have one instance of QApplication(), inside the brackets[] would be parameters passed to the application
    app = QtWidgets.QApplication([])
    app.setStyle('Fusion')
    
    main_window = MainWindow()
    
    #   app.exec() hands control over to Qt and will run the application till the user closes it
    app.exec()
    print ("End of program")
    sys.exit()
    
    
#DRIVER CODE

if __name__ == '__main__' :

    main()