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
        #   VARIABLES
        
        #   CREATE WIDGETS
        #   Every GUI must have one instance of QApplication(), inside the brackets[] would be parameters passed to the application
        self.app = qt.QtWidgets.QApplication([])
        self.app.setStyle('Fusion')

        self.label = qt.QtWidgets.QLabel("Whaddup playa")
        self.label.show()

def main():
    
    # GUI object
    gui = transform_gui()
    
    #   This hands control over to Qt and will run the application till the user closes it
    gui.app.exec()

    print ("End of program")
    
#DRIVER CODE

if __name__ == '__main__' :

    main()