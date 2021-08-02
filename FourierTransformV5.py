# -*- coding: utf-8 -*-
"""
Created on Wed Jul 21 09:52:55 2021

@author: Earthman
"""

import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar
from matplotlib.backends.backend_qt5agg import FigureCanvas
import matplotlib
matplotlib.use('Qt5Agg')
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
        
        test_label = QtWidgets.QLabel("Whaddup playa this is a test label")
        
        fits_image = FitsImageCanvas()

        toolbar = NavigationToolbar(fits_image, self)
        
        #   GUI Layout
        layout = QtWidgets.QGridLayout()
        layout.addWidget(test_label)
        layout.addWidget(toolbar)
        layout.addWidget(fits_image)
        
        #   Central widget for everything to sit inside
        placeholder_widget = QtWidgets.QWidget()
        placeholder_widget.setLayout(layout)
        self.setCentralWidget(placeholder_widget)
        
        self.show()
  
################################################################################################################################
################################################################################################################################
################################################################################################################################
    
class FitsImageCanvas(FigureCanvasQTAgg):
    
    def __init__(self, parent = None):
        
        figure = Figure()
        ax = figure.subplots()
        
        image_array = self.open_fits_image()
        
        ax.imshow(image_array, origin='lower', cmap='gray', vmin = np.min(image_array), vmax = np.max(image_array))
        
        super(FitsImageCanvas, self).__init__(figure)
        
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

        #   Opening fits file. Returns Header Data Unit(HDU) List (hdul: header and data array/table)
        hdul = fits.open(file_path)

        #   Primary HDU
        primary_HDU = hdul[0]
        image_array = primary_HDU.data[:,:]
        
        print(type(image_array))
        print(image_array.data)
        
        return image_array
    
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
    
    
#DRIVER CODE

if __name__ == '__main__' :

    main()