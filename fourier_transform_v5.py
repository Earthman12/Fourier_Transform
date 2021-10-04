# -*- coding: utf-8 -*-
"""
Created on Wed Jul 21 09:52:55 2021

@author: Earthman
"""

import os
import sys
from tkinter.filedialog import askopenfilename
from tkinter import Tk
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas, NavigationToolbar2QT as NavigationToolbar
import numpy as np
import scipy.fft
from astropy.io import fits
from astroscrappy import detect_cosmics
from PyQt5 import QtWidgets

##############################################################################
##############################################################################
##############################################################################

class MainWindow(QtWidgets.QMainWindow):
    '''GUI Object'''

    def __init__(self, *args, **kwargs):

        super(MainWindow, self).__init__(*args, **kwargs)
        
        #   GUI constants
        TEXT_INPUT_WIDTH = 200

        #   Original fits image canvas
        self.fits_image = FitsImageCanvas()
        #   Toolbar
        self.toolbar = NavigationToolbar(self.fits_image, self)
        #   Open new image button
        self.open_button = QtWidgets.QPushButton("Open New File")
        self.open_button.clicked.connect(self.fits_image.change_image)

        #   Debias button
        self.debias_button = QtWidgets.QPushButton("Debias Image")
        self.debias_button.clicked.connect(self.fits_image.debias_image)

        #   Y plot widget for stuff when selecting Y row to plot to sit in
        self.y_row_widget = QtWidgets.QWidget()
        #   Frame
        self.y_row_widget.setStyleSheet('''
                                        .QWidget{border: 1px solid black}
                                        ''')
        #   Main set row label
        self.y_main_label = QtWidgets.QLabel("Row Plot Selection")
        #   Input text and button to set Y row for transform plot
        self.y_row_label = QtWidgets.QLabel("Enter row:")
        self.y_row_input = QtWidgets.QLineEdit()
        self.y_row_input.setFixedWidth(TEXT_INPUT_WIDTH)
        self.y_row_submit_button = QtWidgets.QPushButton("Set Y Row")
        self.y_row_submit_button.clicked.connect(self.change_plot_y_row)
        #   Save .DAT file button
        self.save_dat_button = QtWidgets.QPushButton("Save Spectrum")
        self.save_dat_button.clicked.connect(self.fits_image.save_spectrum_as_dat_file)
        #   Up one row button
        self.up_one_row_button = QtWidgets.QPushButton("Up One Row")
        self.up_one_row_button.clicked.connect(self.fits_image.up_one_row)
        #   Down one row button
        self.down_one_row_button = QtWidgets.QPushButton("Down One Row")
        self.down_one_row_button.clicked.connect(self.fits_image.down_one_row)
        #   Set Y row widget layout to grid
        self.y_row_layout = QtWidgets.QGridLayout()
        #   Add Y row widgets to layout
        self.y_row_layout.addWidget(self.y_main_label, 0, 1)
        self.y_row_layout.addWidget(self.y_row_label, 1, 0)
        self.y_row_layout.addWidget(self.y_row_input, 1, 1)
        self.y_row_layout.addWidget(self.y_row_submit_button, 2, 0)
        self.y_row_layout.addWidget(self.save_dat_button, 3, 0)
        self.y_row_layout.addWidget(self.up_one_row_button, 2, 2)
        self.y_row_layout.addWidget(self.down_one_row_button, 3, 2)
        #   Set Y row widget layout
        self.y_row_widget.setLayout(self.y_row_layout)

        #   Crop widget for all crop stuff to sit in
        self.crop_widget = QtWidgets.QWidget()
        #   Frame
        self.crop_widget.setStyleSheet('''
                                       .QWidget{border: 1px solid black;}
                                       ''')
        #   Crop label
        self.crop_label = QtWidgets.QLabel("Crop Image")
        #   X low
        self.x_low_label = QtWidgets.QLabel("Set X min: ")
        self.x_low_input = QtWidgets.QLineEdit()
        self.x_low_input.setFixedWidth(TEXT_INPUT_WIDTH)
        #   X high
        self.x_high_label = QtWidgets.QLabel("Set X max: ")
        self.x_high_input = QtWidgets.QLineEdit()
        self.x_high_input.setFixedWidth(TEXT_INPUT_WIDTH)
        #   Y low
        self.y_low_label = QtWidgets.QLabel("Set Y min: ")
        self.y_low_input = QtWidgets.QLineEdit()
        self.y_low_input.setFixedWidth(TEXT_INPUT_WIDTH)
        #   Y high
        self.y_high_label = QtWidgets.QLabel("Set Y max: ")
        self.y_high_input = QtWidgets.QLineEdit()
        self.y_high_input.setFixedWidth(TEXT_INPUT_WIDTH)
        #   Crop button
        self.crop_button = QtWidgets.QPushButton("Set Image Crop")
        self.crop_button.clicked.connect(self.crop_image)
        #   Set crop widget layout to grid
        self.crop_layout = QtWidgets.QGridLayout()
        #   Add crop widgets
        self.crop_layout.addWidget(self.crop_label, 0, 1)
        self.crop_layout.addWidget(self.x_low_label, 1, 0)
        self.crop_layout.addWidget(self.x_low_input, 2, 0)
        self.crop_layout.addWidget(self.x_high_label, 3, 0)
        self.crop_layout.addWidget(self.x_high_input, 4, 0)
        self.crop_layout.addWidget(self.y_low_label, 1, 2)
        self.crop_layout.addWidget(self.y_low_input, 2, 2)
        self.crop_layout.addWidget(self.y_high_label, 3, 2)
        self.crop_layout.addWidget(self.y_high_input, 4, 2)
        self.crop_layout.addWidget(self.crop_button, 5, 1)
        #   Set crop widget layout
        self.crop_widget.setLayout(self.crop_layout)

        #   GUI Grid Layout
        self.layout = QtWidgets.QGridLayout()
        self.layout.addWidget(self.open_button, 0, 0)
        self.layout.addWidget(self.debias_button, 1, 0)
        self.layout.addWidget(self.y_row_widget, 0, 1, 2, 1)
        self.layout.addWidget(self.crop_widget, 0, 2, 2, 1)
        self.layout.addWidget(self.toolbar, 2, 1)
        self.layout.addWidget(self.fits_image, 3, 0, 1, 3)

        #   Central widget for everything to sit inside
        self.placeholder_widget = QtWidgets.QWidget()
        #   Central widget takes GUI layout written out above
        self.placeholder_widget.setLayout(self.layout)
        self.setCentralWidget(self.placeholder_widget)

        #   This will start the GUI in fullscreen
        self.showMaximized()

    #---------------------------------------------------------------------------
    #-----------------------MainWindow Functions--------------------------------
    #---------------------------------------------------------------------------

    def change_plot_y_row(self):
        '''Changes the row that is plotted'''

        print("-----Changing Y Rows-----")
        
        #   Value from readout value to array row
        readout_value = int(self.y_row_input.text())
        
        #   Check that the new input is greater than 0 and does not exceed Y image length,
        #   if it okay, set the new value and call the 'fits_image' update function
        if(readout_value < ((self.fits_image.image_array.shape[0] / 2) - 1) and readout_value > -((self.fits_image.image_array.shape[0] / 2) + 1)):
            self.fits_image.y_row = int(readout_value)
            self.fits_image.update_figure()

        else:
            print("Input not between 0 and the Y length of the image")

    ##############################################################################

    def crop_image(self):
        '''Takes the inputs from the user and crops the image'''

        #   Get values from text inputs
        x_low = int(self.x_low_input.text())
        x_high = int(self.x_high_input.text())
        y_low = int(self.y_low_input.text())
        y_high = int(self.y_high_input.text())

        #   Check that x_low is less than x_high and same for y and also that
        #   they are in image bounds
        if ((x_low >= 0) and (x_low < x_high) and (y_low >= 0) and (y_low < y_high) and (x_high < self.fits_image.image_array.shape[1]) and (y_high < self.fits_image.image_array.shape[0])):

            print("-----Cropping image-----")
            #   Send them to the fits_image crop function to be cropped
            self.fits_image.set_crop_image(x_low, x_high, y_low, y_high)

        else:
            print("-----Crop limits out of bounds-----")

##############################################################################
##############################################################################
##############################################################################

class FitsImageCanvas(FigureCanvas):
    '''Image object'''

    def __init__(self, parent = None):
        
        #   Figure contstants
        self.FIGURE_SIZE_X = 20
        self.FIGURE_SIZE_Y = 10
        self.ROWS = 2
        self.COL = 3

        #   Figure variables
        self.figure = Figure(figsize = (self.FIGURE_SIZE_X,self.FIGURE_SIZE_Y))
        super(FitsImageCanvas, self).__init__(self.figure)
        self.axes = []

        #   Original fits image variables
        self.image_name = ''
        self.image_array = self.open_fits_image()

        self.set_filters_and_plot()

    #---------------------------------------------------------------------------
    #-----------------------ImageCanvas Functions-------------------------------
    #---------------------------------------------------------------------------

    def open_fits_image(self):
        '''Opens a new fits image'''

        #   Not having Tk().withdraw() does not make the code execute properly,
        #   not completely sure why, but it is necessary
        Tk().withdraw()
        #   Opens up file explorer to select the file
        file_path = askopenfilename()
        file_name = os.path.basename(file_path)

        print("File Name:",file_name)
        self.image_name = file_name

        #   Opening fits file. Returns Header Data Unit(HDU) List
        #   (hdul: header and data array/table)
        hdul = fits.open(file_path)

        #   Primary HDU
        primary_hdu = hdul[0]
        image_array = primary_hdu.data[:,:]

        print("Number of X axis values: " + str(image_array.shape[1]))
        print("Number of Y axis values: " + str(image_array.shape[0]))

        return image_array

    ##############################################################################

    def open_bias_image(self):
        '''Opens a bias image to subtract from the fits image'''

        print("Opening bias image...")

        #   Not having Tk().withdraw() does not make the code execute properly,
        #   not completely sure why, but it is necessary
        Tk().withdraw()
        #   Opens up file explorer to select the file
        file_path = askopenfilename()
        file_name = os.path.basename(file_path)

        print("File Name:",file_name)

        #   Opening fits file. Returns Header Data Unit(HDU) List
        #   (hdul: header and data array/table)
        hdul = fits.open(file_path)

        #   Primary HDU
        primary_hdu = hdul[0]
        image_array = primary_hdu.data[:,:]

        print("Number of X axis values: " + str(image_array.shape[1]))
        print("Number of Y axis values: " + str(image_array.shape[0]))

        return image_array

    ##############################################################################

    def get_image_name(self):
        '''Returns the name of the image'''

        return self.image_name

    ##############################################################################

    def fourier_transform(self):
        '''Returns a transformed image of the hanning filtered fits image'''

        print("Transforming image...")

        #   Fourier Transforming
        f_transform = scipy.fft.fft2(self.hanning_image)
        #   Shifting zero frequency component to center spectrum
        f_shift = np.fft.fftshift(f_transform)

        power_spectrum = (np.abs(f_shift) ** 2)

        #   Visual representation of Fourier Transform
        fourier_image = np.log10(power_spectrum)

        return fourier_image

    ##############################################################################

    def apply_cosmics(self):
        '''Returns a cosmics filtered image of the original fits image'''

        print("Applying cosmics filter...")

        #   Detect cosmic rays
        cosmic_array = detect_cosmics(self.image_array, sigclip = 5.0, sigfrac = 0.3, readnoise = 10.0, gain = 2.2, satlevel = 65536, niter = 4, cleantype ='meanmask' , fsmode='median',sepmed=True, psfmodel='gauss', psffwhm =2.5, psfsize =7)
        cosmic_array_image = cosmic_array[1]

        return cosmic_array_image

    ##############################################################################

    def apply_hanning(self):
        '''Returns a hanning window image of the cosmics filtered image'''

        print("Applying Hanning window...")

        #   Creating the 2d Hanning window
        hanning_x = np.hanning(self.cosmic_image.shape[1])
        hanning_y = np.hanning(self.cosmic_image.shape[0])
        hanning_window = np.sqrt(np.outer(hanning_y, hanning_x))
        hanning_image = hanning_window * self.cosmic_image

        return hanning_image

    ##############################################################################

    def change_image(self):
        '''Changes the fits image variable'''

        print("-----Changing FITS Images-----")

        #   Set the new image and set the array to the 'image_array' variable
        self.image_array = self.open_fits_image()

        #   Set the rest of the images
        self.set_filters_and_plot()

    ##############################################################################

    def set_filters_and_plot(self):
        '''Sets the filtered images and plot variables'''

        print("Setting filtered images and plot...")

        #   Set new cosmic filtered image
        self.cosmic_image = self.apply_cosmics()

        #   Set new hanning window image
        self.hanning_image = self.apply_hanning()

        #   Set new transform image
        self.transform_image = self.fourier_transform()

        #   Reset row cut to middle of image
        self.y_row = 0

        #   Call update_figure function to re-draw it
        self.update_figure()

    ##############################################################################

    def row_cut(self):
        '''Returns a certain y row's values in the transform'''

        #   Converting 0,0 array row value to actual array row value
        converted_row_value = int(self.y_row + self.transform_image.shape[0] / 2)

        print("Getting values for row num: " + str(self.y_row))
        print("Converted array value: " + str(converted_row_value))

        #   Create empty array the length of the rows
        row_values_array = np.zeros(shape = len(self.transform_image[converted_row_value]))

        #  Loop through the values in the row and take the absolute value and the square
        #   of the row and the row above and below it and add them together
        for i in range(0, row_values_array.shape[0], 1):
            #   Get absolute value of the row and its top and bottom
            abs_top = abs(self.transform_image[converted_row_value + 1][i])
            abs_row = abs(self.transform_image[converted_row_value][i])
            abs_bottom = abs(self.transform_image[converted_row_value - 1][i])
            #   Get the square
            square_top = abs_top * abs_top
            square_row = abs_row * abs_row
            square_bottom = abs_bottom * abs_bottom
            #   Add them together
            row_values_array[i] = square_top + square_row + square_bottom

        return row_values_array

    ##############################################################################

    def update_figure(self):
        '''Updates the figure on the GUI to new image variables'''

        #   This function will be called whenever the images or plot needs to be updated,
        #   it will make it easier to keep calling this then re-write code

        #   Clear the list of axes to get have fresh axes to draw on in case image size is different
        #   Must also clear the figure to avoid getting a MatPlotLib Deprecation Warning
        self.axes.clear()
        self.figure.clear()

        #   ORIGINAL FITS IMAGE
        #   Add subplot to the figure and set title
        self.axes.append(self.figure.add_subplot(self.ROWS, self.COL, 1))
        self.axes[0].set_title("Original " + self.image_name + " Image")
        #   Set the new image array and transform to their display objects and set
        #   the min and max accordingly for the new image
        self.original_display_object = self.axes[0].imshow(self.image_array, origin='lower', cmap='gray', vmin = np.min(self.image_array), vmax = np.max(self.image_array))

        #   COSMICS IMAGE
        #   Add subplot to the figure and set title
        self.axes.append(self.figure.add_subplot(self.ROWS, self.COL, 2))
        self.axes[1].set_title("Cosmics Filtered Image")
        #   Set the cosmic image to its display object
        self.cosmic_display_object = self.axes[1].imshow(self.cosmic_image, origin='lower', cmap='gray', vmin = np.min(self.cosmic_image), vmax = np.max(self.cosmic_image))

        #   HANNING WINDOW IMAGE
        #   Add subplot to figure and set title
        self.axes.append(self.figure.add_subplot(self.ROWS, self.COL, 3))
        self.axes[2].set_title("Hanning Window Image")
        #   Display object variable for hanning image
        self.hanning_display_object = self.axes[2].imshow(self.hanning_image, origin='lower', cmap='gray', vmin = np.min(self.hanning_image), vmax = np.max(self.hanning_image))

        #   FOURIER TRANSFORM IMAGE
        #   Add subplot to the figure and set title
        self.axes.append(self.figure.add_subplot(self.ROWS, self.COL, 4))
        self.axes[3].set_title("Fourier Transform")
        #   Pre-set the axis' extent so 0,0 is in the middle
        extent = [-self.transform_image.shape[1] / 2, self.transform_image.shape[1] / 2, -self.transform_image.shape[0] / 2, self.transform_image.shape[0] / 2]
        #   Pre-set min and max values
        min_val = np.min(self.transform_image)
        max_val = np.max(self.transform_image)
        #   Set the new transform image to its display object variable
        self.transform_display_object = self.axes[3].imshow(self.transform_image, origin='lower', extent = extent, cmap='gray', vmin = min_val, vmax = max_val)

        #   ROW OF VALUES PLOT
        #   Add subplot to figure and set title
        self.axes.append(self.figure.add_subplot(self.ROWS, self.COL, 5))
        self.axes[4].set_title("Row " + str(self.y_row) + " Plot")
        #   Calling row_cut function that returns transform row values
        transform_row_values = self.row_cut()
        #   Making second array to plot with so x axis has 0 in middle
        row_size = len(transform_row_values)
        x_axis_values = np.arange(-row_size / 2, row_size / 2, dtype = 'int')
        #   Display object for transform row plot, displaying the log of the values
        self.row_plot_display_object = self.axes[4].plot(x_axis_values, np.log10(transform_row_values))

        #   Re-draw it on to the figure
        self.draw()

        print("Figure Updated")

    ##############################################################################

    def save_spectrum_as_dat_file(self):
        '''Saves the y rows values that are plotted as a .DAT file'''

        print("Saving spectrum plot as .DAT")

        #   Get just file name, takes the '.fits' out
        file_name_split = self.get_image_name().split(".")
        #   The file should save as "name_values_row_num_0"
        title = file_name_split[0] + "_values_row_num_" + str(self.y_row)
        print("File name: " + title)

        #   Save it to 4 decimal places
        values = self.row_cut()
        #   'tofile() saves the data but in binary
        #values.tofile(title + ".dat")
        save_file = open(title + ".dat", "w")
        np.savetxt(save_file, values, fmt = "%.4e")

        print("Save Successful")

    ##############################################################################

    def set_crop_image(self, x_low, x_high, y_low, y_high):
        '''Takes in the crop bounds and returns the cropped image'''

        print("Setting the cropped image")

        #   Create empty array for the new cropped image
        cropped_image = np.zeros(shape = (y_high - y_low, x_high - x_low))

        #   Loop variables
        i = x_low
        j = y_low
        x_count = 0
        y_count = 0

        #   Loop to set the cropped image
        while i < x_high:
            while j < y_high:
                cropped_image[y_count][x_count] = self.image_array[j][i]
                j += 1
                y_count += 1
            y_count = 0
            j = y_low
            i += 1
            x_count += 1

        #   Set the image to the new cropped image and update the rest of the images and plot
        self.image_array = cropped_image
        print("Number of values in the X axis: " + str(self.image_array.shape[1]))
        print("Number of values in the Y axis: " + str(self.image_array.shape[0]))
        self.set_filters_and_plot()

    ##############################################################################

    def debias_image(self):
        '''Subtracts a bias image from the fits image'''

        print("-----Debiasing image-----")

        #   Open debiased image and save to a variable
        bias_image = self.open_bias_image()

        #   Check to make sure that the X and Y dimensions are the same
        if(bias_image.shape[1] == self.image_array.shape[1] and bias_image.shape[0] == self.image_array.shape[0]):
            print("Dimensions match, proceeding to debias image...")

            #   Subtract the bias and update the image variable and figure
            self.image_array = self.image_array - bias_image

            #   Set the new image so it updates the in the figure
            self.set_filters_and_plot()

        else:
            print("Image and bias image dimensions do not match, please select a different one")

    ##############################################################################

    def up_one_row(self):
        '''Moves the plot up one row'''

        self.y_row += 1
        print("-----Moving plot up one row to " + str(self.y_row) + "-----")
        self.update_figure()

    ##############################################################################

    def down_one_row(self):
        '''Moves the plot down one row'''

        self.y_row -= 1

        print("-----Moving plot down one row to " + str(self.y_row) + "-----")

        self.update_figure()

##############################################################################
##############################################################################
##############################################################################

def main():
    '''Main driver code'''

    #   Every GUI must have one instance of QApplication(), inside the brackets[]
    #   would be parameters passed to the application
    app = QtWidgets.QApplication([])

    main_window = MainWindow()
    main_window.show()

    #   app.exec() hands control over to Qt and will run the application till the user closes it
    app.exec()
    print ("End of program")
    sys.exit()

#DRIVER CODE

if __name__ == '__main__' :

    main()
