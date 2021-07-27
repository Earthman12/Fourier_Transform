# -*- coding: utf-8 -*-
"""
Created on Wed Jul 21 09:52:55 2021

@author: Earthman
"""


import PyQt5 as qt
import numpy as np
import matplotlib.pyplot as plt
import scipy.ndimage as ndi
import os
from matplotlib.colors import LogNorm
from astropy.io import fits
from tkinter.filedialog import askopenfilename
from tkinter import Tk
from astroscrappy import detect_cosmics

#   GUI OBJECT
class transform_gui(object):
    
    def __init__(self):
        #----VARIALBES----------------------------------------------------------
                
        self.image = self.open_image()
                
        #----CREATE WIDGETS-----------------------------------------------------
        
        #   Every GUI must have one instance of QApplication(), inside the brackets[] would be parameters passed to the application
        self.app = qt.QtWidgets.QApplication([])
        self.app.setStyle('Fusion')
        
        self.window = qt.QtWidgets.QWidget()
        #   Set window layout to grid
        self.layout = qt.QtWidgets.QGridLayout()
        self.window.setLayout(self.layout)
        
        #   Test label
        self.label = qt.QtWidgets.QLabel("Whaddup playa this is a test label")
        
        height, width = self.image.shape
        bytes_per_line = 3 * width
        
        #   Error occurs in this line of code
        self.qImg = qt.QtGui.QImage(self.image, width, height, bytes_per_line, qt.QtGui.QImage.Format_RGB888)
        
        self.qPix = qt.QtGui.QPixmap(self.qImg)
        
        self.label2 = qt.QtWidgets.QLabel()
        self.label2.setPixmap(self.qPix)
        
        #---PLACEMENTS--------------------------------------------------------
        
        #   Add widget to the grid
        self.layout.addWidget(self.label,0,0)
        self.layout.addWidget(self.label2,0,1)
        
        
        self.window.show()
        
    #--------------------------------------------------------------------------------------------------
    #----------------------------------GUI FUNCTIONS---------------------------------------------------
    #--------------------------------------------------------------------------------------------------
    def open_image(self):
        
        #   Not having Tk().withdraw() does not make the code execute properly, not completely sure why, but it is necessary
        Tk().withdraw()
        #   Opens up file explorer to select the file
        filePath = askopenfilename()
        print("-0.5")
        fileName = os.path.basename(filePath)
        print("File Name:",fileName)

        #   Opening fits file. Returns Header Data Unit(HDU) List (hdul: header and data array/table)
        hdul = fits.open(filePath)

        #   Primary HDU
        primHDU = hdul[0]
        imageArray = primHDU.data[:,:]
        
        print(type(imageArray))
        
        return imageArray
    
################################################################################################################################
################################################################################################################################
################################################################################################################################

def main():
    
    # GUI object
    gui = transform_gui()
    
    #   This hands control over to Qt and will run the application till the user closes it
    gui.app.exec()

    print ("End of program")
    
#DRIVER CODE

if __name__ == '__main__' :

    main()