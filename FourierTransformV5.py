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
        
        print ("0")
        
        #----CREATE WIDGETS-----------------------------------------------------
        
        #   Every GUI must have one instance of QApplication(), inside the brackets[] would be parameters passed to the application
        self.app = qt.QtWidgets.QApplication([])
        self.app.setStyle('Fusion')
        
        print ("1")
        
        self.window = qt.QtWidgets.QWidget()
        #   Set window layout to grid
        self.layout = qt.QtWidgets.QGridLayout()
        self.window.setLayout(self.layout)
        
        print ("2")

        self.label = qt.QtWidgets.QLabel("Whaddup playa this is a test label")
        
        print ("3")
        
        self.qImg = qt.QtGui.QPixmap(qt.QtGui.QImage(self.image.data, self.image.shape[0], self.image.shape[1], qt.QtGui.QImage.Format_RGB888))
        
        print ("4")
        
        self.label2 = qt.QtWidgets.QLabel()
        self.label2 = qt.QtWidgets.QLabel.setPixmap(self.qImg)
        
        print ("5")
        
        
        
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
        fileName = os.path.basename(filePath)
        print("File Name:",fileName)

        #   Opening fits file. Returns Header Data Unit(HDU) List (hdul: header and data array/table)
        hdul = fits.open(filePath)

        #   Primary HDU
        primHDU = hdul[0]
        imageArray = primHDU.data[:,:]
        
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