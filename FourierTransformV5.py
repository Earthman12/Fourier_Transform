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
        
        #   Change image data from image class
        self.fits_image.change_image()
        
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
        self.rows = 2
        self.col = 3
        
        #   Original Fits Image variables
        self.image_name = ''
        self.image_array = self.open_fits_image()
        #   Adding subplot to the figure and setting title
        self.axes.append(self.figure.add_subplot(self.rows, self.col, 1))
        self.axes[0].set_title("Original Fits Image")
        #   Display object variable for fits image
        self.original_display_object = self.axes[0].imshow(self.image_array, origin='lower', cmap='gray', vmin = np.min(self.image_array), vmax = np.max(self.image_array))
        
        #   Cosmic Filtered Fits Image Variables
        self.cosmic_image = self.apply_cosmics()
        #   Add subplot to figure and set title
        self.axes.append(self.figure.add_subplot(self.rows,self.col,2))
        self.axes[1].set_title("Cosmics filtered image")
        #   Display object variable for cosmic image
        self.cosmic_display_object = self.axes[1].imshow(self.cosmic_image, origin='lower', cmap='gray', vmin = np.min(self.cosmic_image), vmax = np.max(self.cosmic_image))
        
        #   Transform Image Variables
        self.transform_image = self.fourier_transform()
        #   Add subplot to figure and set title
        self.axes.append(self.figure.add_subplot(self.rows,self.col, 3))
        self.axes[2].set_title("Fourier Transform")
        #   Display object variable for transform image
        self.transform_display_object = self.axes[2].imshow(self.transform_image, origin='lower', cmap='gray', vmin = np.min(self.transform_image), vmax = np.max(self.transform_image))
        
        #   Fourier Transform Row Plot Variables
        #   Default row cut will be in the middle of the transform
        self.y_row = int(len(self.transform_image) / 2)
        #   Get row values that have the absolute values and squares of the row and its top and bottom row added
        self.row_cut_values = self.row_cut()
        #   Add subplot to figure and set title
        self.axes.append(self.figure.add_subplot(self.rows,self.col, 5))
        self.axes[3].set_title("Row Cut Plot")
        #   Display object for transform row plot
        self.row_plot_display_object = self.axes[3].plot(self.row_cut_values)
        
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
    
    ##############################################################################
    
    def change_image(self):
        
        print("Changing FITS images")
        
        #   Clear the list of axes to get have fresh axes to draw on in case image size is different
        #   Must also clear the figure to avoid getting a MatPlotLib Deprecation Warning
        self.axes.clear()
        self.figure.clear()
        
        #   Set the new image and set the array to the 'image_array' variable
        self.image_array = self.open_fits_image()
        #   Add subplot to the figure and set title
        self.axes.append(self.figure.add_subplot(self.rows, self.col, 1))
        self.axes[0].set_title("Original Fits Image")
        #   Set the new image array and transform to their display objects and set the min and max accordingly for the new image
        self.original_display_object = self.axes[0].imshow(self.image_array, origin='lower', cmap='gray', vmin = np.min(self.image_array), vmax = np.max(self.image_array))
        
        #   Set new cosmics image
        self.cosmic_image = self.apply_cosmics()
        #   Add subplot to the figure and set title
        self.axes.append(self.figure.add_subplot(self.rows, self.col, 2))
        self.axes[1].set_title("Cosmics filtered image")
        #   Set the cosmic image to its display object
        self.cosmic_display_object = self.axes[1].imshow(self.cosmic_image, origin='lower', cmap='gray', vmin = np.min(self.cosmic_image), vmax = np.max(self.cosmic_image))
        
        #   Set transform on the new image and set it the 'transform_image' variable
        self.transform_image = self.fourier_transform()
        #   Add subplot to the figure and set title
        self.axes.append(self.figure.add_subplot(self.rows, self.col, 3))
        self.axes[2].set_title("Fourier Transform")
        #   Set the new transform image to its display object variable        
        self.transform_display_object = self.axes[2].imshow(self.transform_image, origin='lower', cmap='gray', vmin = np.min(self.transform_image), vmax = np.max(self.transform_image))
        
        #   Set the plot for the new image
        #   Middle of image
        self.y_row = int(len(self.transform_image) / 2)
        
        #   Get row values that have the absolute values and squares of the row and its top and bottom row added
        self.row_cut_values = self.row_cut()
        #   Add subplot to figure and set title
        self.axes.append(self.figure.add_subplot(self.rows,self.col, 5))
        self.axes[3].set_title("Row Cut Plot")
        #   Display object for transform row plot
        self.row_plot_display_object = self.axes[3].plot(self.row_cut_values)
        
        #   Re-draw it on to the figure
        self.draw()
        
    ##############################################################################
    
    def row_cut(self):
        
        print("Getting values for row of Y values")
        
        #   Create empty array the length of the rows
        row_values_array = np.zeros(shape = len(self.transform_image[self.y_row]))
        
        #  Loop through the values in the row and take the absolute value and the square of the row and the row above and below it and add them together
        for i in range(0, len(row_values_array), 1):
            #   Get absolute value of the row and its top and bottom
            abs_top = abs(self.transform_image[self.y_row + 1][i])
            abs_row = abs(self.transform_image[self.y_row][i])
            abs_bottom = abs(self.transform_image[self.y_row - 1][i])
            #   Get the square 
            square_top = abs_top * abs_top
            square_row = abs_row * abs_row
            square_bottom = abs_bottom * abs_bottom
            #   Add them together
            row_values_array[i] = square_top + square_row + square_bottom
        
        return row_values_array
    
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