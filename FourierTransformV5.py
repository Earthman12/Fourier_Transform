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
        
        #   Open the new image and set the array to the 'image_array' variable
        self.fits_image.image_array = self.fits_image.open_fits_image()
        #   Set the new image array and transform to their display objects and set the min and max accordingly for the new image
        self.fits_image.display_object.set_data(self.fits_image.image_array)
        self.fits_image.display_object.set_clim(vmin = np.min(self.fits_image.image_array), vmax = np.max(self.fits_image.image_array))
        
        #   Call the transform on the new image and set it the 'transform_image' variable
        self.fits_image.transform_image = self.fits_image.fourier_transform()
        #   Set the new transform image to its display object variable        
        self.fits_image.display_object_2.set_data(self.fits_image.transform_image)
        self.fits_image.display_object_2.set_clim(vmin = np.min(self.fits_image.transform_image), vmax = np.max(self.fits_image.transform_image))
        
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
        self.figure = Figure(figsize = (10,5))
        self.axes = []
        rows = 1
        col = 2
        
        #   Fits Image variables
        self.image_name = ''
        self.image_array = self.open_fits_image()
        #   Adding subplot to the figure
        self.axes.append(self.figure.add_subplot(rows, col, 1))
        #   Display object variable for fits image
        self.display_object = self.axes[0].imshow(self.image_array, origin='lower', cmap='gray', vmin = np.min(self.image_array), vmax = np.max(self.image_array))
        
        #   Transform Image Variables
        self.transform_image = self.fourier_transform()
        #   Add subplot to figure
        self.axes.append(self.figure.add_subplot(rows,col, 2))
        #   Display object variable for transform image
        self.display_object_2 = self.axes[1].imshow(self.transform_image, origin='lower', cmap='gray', vmin = np.min(self.transform_image), vmax = np.max(self.transform_image))
        
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